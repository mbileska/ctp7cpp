import h5py
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import argparse
import os
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, BatchNormalization, AveragePooling2D, Flatten, Dense, Dropout, Lambda, Layer
from tensorflow.keras.callbacks import Callback, EarlyStopping
from qkeras import QConv2D, QDense, QActivation
from qkeras.quantizers import quantized_bits
from tensorflow.keras import backend as K


def load_data(file_path):
    with h5py.File(file_path, 'r') as f:
        cregions = f['cregions'][:]
        genPhi = f['genPhi_1'][:]
        genEta = f['genEta_1'][:]
        cregionsMetrics = cregions - 30.0
        cregionsMetrics[cregionsMetrics < 0] = 0.0
    return cregions, genPhi, genEta, cregionsMetrics

def calculate_labels(cregions, genPhi, genEta):
    labels = []

    for img, phi, eta in zip(cregions, genPhi, genEta):
        heatmap = img.reshape((18, 14))

        # Summing with wrap-around for the phi dimension
        sums = np.array([
            [np.sum(heatmap[i:i + 3, j:j + 3]) for j in range(heatmap.shape[1] - 2)]
            for i in range(heatmap.shape[0] - 2)
        ])
        
        # Find the largest 3x3 grid within ±3 units from (genPhi, genEta) with wrap-around in phi
        phi_min, phi_max = int(phi - 3), int(phi + 3)
        eta_min, eta_max = int(max(0, eta - 3)), int(min(sums.shape[1], eta + 3))

        # Handle wrap-around in phi dimension
        if phi_min < 0 or phi_max >= 18:
            # Create a wrapped-around region for phi
            sums_wrapped = np.concatenate((sums[phi_min:], sums[:phi_max % 18 + 1]), axis=0)
            phi_min_wrapped = phi_min % 18
            phi_max_wrapped = (phi_max % 18) + sums_wrapped.shape[0] - (phi_max % 18 + 1)
        else:
            sums_wrapped = sums[phi_min:phi_max + 1]
            phi_min_wrapped = phi_min
            phi_max_wrapped = phi_max

        # Restrict to eta range
        sums_restricted = sums_wrapped[:, eta_min:eta_max + 1]

        # Find the largest 3x3 region within the restricted area
        largest_index = np.argmax(sums_restricted)
        largest_relative = np.unravel_index(largest_index, sums_restricted.shape)
        largest = (largest_relative[0] + phi_min_wrapped, largest_relative[1] + eta_min)

        # Handle wrap-around adjustment in phi dimension for the final coordinates
        largest = (largest[0] % 18, largest[1])
        
        labels.append([largest[0] + 1, largest[1] + 1])

    return np.array(labels)

def evaluate_model(predictions, labels, save_path):
    mae = mean_absolute_error(labels, predictions)
    mse = mean_squared_error(labels, predictions)
    rmse = np.sqrt(mse)
    r2 = r2_score(labels, predictions)
    
    metrics = {
        "Mean Absolute Error": mae,
        "Mean Squared Error": mse,
        "Root Mean Squared Error": rmse,
        "R^2 Score": r2
    }
    
    print("\nModel Evaluation Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value}")
    
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 2, 1)
    plt.title("Mean Absolute Error")
    plt.bar("MAE", mae)
    
    plt.subplot(2, 2, 2)
    plt.title("Mean Squared Error")
    plt.bar("MSE", mse)
    
    plt.subplot(2, 2, 3)
    plt.title("Root Mean Squared Error")
    plt.bar("RMSE", rmse)
    
    plt.subplot(2, 2, 4)
    plt.title("R^2 Score")
    plt.bar("R^2", r2)
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'evaluation_metrics.png'))
    plt.close()

    residuals = labels - predictions
    plt.figure(figsize=(10, 5))
    plt.hist(residuals.flatten(), bins=50)
    plt.title('Residuals Distribution')
    plt.xlabel('Residual')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(save_path, 'residuals_distribution.png'))
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.scatter(labels.flatten(), predictions.flatten(), alpha=0.5)
    plt.title('Prediction vs Actual')
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.savefig(os.path.join(save_path, 'prediction_vs_actual.png'))
    plt.close()

class LossHistory(Callback):
    def __init__(self, save_path, learning_rate):
        super().__init__()
        self.save_path = save_path
        self.learning_rate = learning_rate
        self.epoch_losses = []

    def on_epoch_end(self, epoch, logs={}):
        loss = logs.get('val_loss')
        self.epoch_losses.append((epoch, loss))
        print(f'Epoch {epoch+1}: val_loss = {loss}')
        self.save_losses()

    def save_losses(self):
        lr_path = os.path.join(self.save_path, f'lr_{self.learning_rate:.0e}')
        os.makedirs(lr_path, exist_ok=True)
        with open(os.path.join(lr_path, 'validation_loss.txt'), 'w') as f:
            for epoch, loss in self.epoch_losses:
                f.write(f"{epoch+1}, {loss}\n")
        plt.figure(figsize=(10, 5))
        epochs, losses = zip(*self.epoch_losses)
        plt.plot(epochs, losses, label=f'LR={self.learning_rate:.0e}')
        plt.xlabel('Epochs')
        plt.ylabel('Validation Loss')
        plt.legend()
        plt.savefig(os.path.join(lr_path, 'validation_loss_plot.png'))
        plt.close()

def plot_heatmaps(cregions, predictions, genPhi, genEta, labels, save_path):
    plt.figure(figsize=(20, 10))
    temp = np.arange(0, 15, 1)
    for i in temp:
        plt.subplot(3, 5, i+1)
        plt.imshow(cregions[i].reshape((18, 14)), cmap='viridis', aspect='auto')
        pred1 = predictions[i][:2]
        pred2 = predictions[i][2:]
        manual1 = labels[i][:2]
        manual2 = labels[i][2:]
        ellipse_pred1 = patches.Ellipse((pred1[1], pred1[0]), width=3, height=3, edgecolor='blue', facecolor='none', label='Predicted')
        ellipse_pred2 = patches.Ellipse((pred2[1], pred2[0]), width=3, height=3, edgecolor='blue', facecolor='none')
        plt.gca().add_patch(ellipse_pred1)
        plt.gca().add_patch(ellipse_pred2)
        ellipse_true = patches.Ellipse((genEta[i], genPhi[i]), width=3, height=3, edgecolor='red', facecolor='none', label='True')
        plt.gca().add_patch(ellipse_true)
        ellipse_manual1 = patches.Ellipse((manual1[1], manual1[0]), width=3, height=3, edgecolor='green', facecolor='none', label='Manual')
        ellipse_manual2 = patches.Ellipse((manual2[1], manual2[0]), width=3, height=3, edgecolor='green', facecolor='none')
        plt.gca().add_patch(ellipse_manual1)
        plt.gca().add_patch(ellipse_manual2)
        plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'heatmaps.png'))
    plt.close()

def build_model(learning_rate):
    input_tensor = Input(shape=(18, 14, 1), name="inputs")
    x = input_tensor
    x = QConv2D(32, (3, 3), padding='same', kernel_quantizer=quantized_bits(8, 1, 1, alpha=1), bias_quantizer=quantized_bits(8, 1, 1, alpha=1), name="conv_1")(x)
    x = BatchNormalization(name="norm_1")(x)
    x = QActivation('quantized_relu(8)', name="relu_1")(x)
    x = AveragePooling2D((2, 2), name="pool_1")(x)
    x = QConv2D(64, (3, 3), padding='same', kernel_quantizer=quantized_bits(8, 1, 1, alpha=1), bias_quantizer=quantized_bits(8, 1, 1, alpha=1), name="conv_2")(x)
    x = BatchNormalization(name="norm_2")(x)
    x = QActivation('quantized_relu(8)', name="relu_2")(x)
    x = AveragePooling2D((2, 2),name="pool_2")(x)
    x = Flatten(name="flatten_1")(x)
    x = QDense(128, kernel_quantizer=quantized_bits(8, 1, 1, alpha=1), bias_quantizer=quantized_bits(8, 1, 1, alpha=1), name="dense_1")(x)
    x = QActivation('quantized_relu(8)', name="relu_3")(x)
    x = Dropout(0.5)(x)
    output_layer = QDense(4, kernel_quantizer=quantized_bits(8, 1, 1, alpha=1), bias_quantizer=quantized_bits(8, 1, 1, alpha=1), name="dense_out")(x)
    model = Model(inputs=input_tensor, outputs=output_layer)
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    model.compile(optimizer=optimizer, loss=custom_mse_with_heavy_penalty)
    return model

def custom_mse_with_heavy_penalty(y_true, y_pred, threshold=1.0, penalty_factor=1.5):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    residual = y_true - y_pred
    small_residuals = K.square(residual)
    large_residuals = K.square(residual) * K.square(penalty_factor) * tf.cast(K.abs(residual) > threshold, tf.float32)
    combined_residuals = tf.where(K.abs(residual) < threshold, small_residuals, large_residuals)
    return K.mean(combined_residuals)

def main():
    parser = argparse.ArgumentParser(description='Train a model with specified parameters.')
    parser.add_argument('h5_filename', type=str, help='Path to the H5 file')
    parser.add_argument('epochs', type=int, help='Number of epochs')
    parser.add_argument('batch_size', type=int, help='Batch size')
    parser.add_argument('learning_rates', type=float, nargs='+', help='Learning rates to try')

    args = parser.parse_args()

    num_epochs = args.epochs
    file_path = args.h5_filename
    batch_size = args.batch_size
    learning_rates = args.learning_rates

    save_path = f'metrics/modelTrue_epochs{num_epochs}_batch{batch_size}'
    os.makedirs(save_path, exist_ok=True)

    cregionsl, genPhi, genEta, cregions = load_data(file_path)
    labels = calculate_labels(cregions, genPhi, genEta)

    cregions = cregions.reshape((cregions.shape[0], 18, 14, 1))
    labels = labels.reshape((labels.shape[0], 4))

    for lr in learning_rates:
        lr_save_path = os.path.join(save_path, f'lr_{lr:.0e}')
        os.makedirs(lr_save_path, exist_ok=True)

        model = build_model(lr)
        history = LossHistory(lr_save_path, lr)
        early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

        model.fit(cregions, labels, epochs=num_epochs, batch_size=batch_size, validation_split=0.2, callbacks=[history, early_stopping])

        predictions = model.predict(cregions)
        evaluate_model(predictions, labels, lr_save_path)

        model_save_path = os.path.join(lr_save_path, 'model')
        model.save(model_save_path, save_format='tf')

if __name__ == '__main__':
    main()
