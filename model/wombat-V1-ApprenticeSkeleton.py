

import h5py
import numpy as np
import tensorflow as tf
from keras.optimizers import Adam

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D,ZeroPadding2D, Cropping2D, Layer, BatchNormalization, PReLU, AveragePooling2D, Concatenate, Flatten, Dense, Dropout, Lambda, Subtract
from tensorflow.keras.callbacks import Callback, EarlyStopping
# from qkeras import QConv2D, QDense, QActivation, QDenseBatchnorm
from qkeras.qlayers import QActivation
from qkeras.quantizers import quantized_bits
from tensorflow.keras import backend as K
from keras.layers import Input, Conv2D, PReLU, BatchNormalization, Activation, AveragePooling2D, Flatten, Dense, Subtract, ReLU

import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.patches as patches
import argparse
import os
from tensorflow.keras.layers import (
    Activation,
    AveragePooling2D,
    Conv2D,
    Dense,
    Dropout,
    Flatten,
    Input,
    Reshape,
    UpSampling2D,
)
from qkeras import QConv2D, QDense, QActivation
from qkeras import QActivation, QConv2D, QDense, quantized_bits


from keras.layers import Input, Reshape, BatchNormalization, AveragePooling2D, Flatten, Lambda




def load_data(file_path):
    with h5py.File(file_path, 'r') as f:
        cregions = f['cregions'][:]
        genPhi = f['genPhi_1'][:]
        genEta = f['genEta_1'][:]
        cregionsMetrics = f['cregions'][:]#cregions - 30.0
        # cregionsMetrics[cregionsMetrics < 0] = 0.0
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




class Subtract30ReLU(Layer):
    def __init__(self, **kwargs):
        super(Subtract30ReLU, self).__init__(**kwargs)

    def call(self, inputs):
        return tf.nn.relu(inputs - 30.0)
    
    def get_config(self):
        return super().get_config()

def build_model():
    input_tensor = Input(shape=(18, 14, 1), name="inputs")
    x=input_tensor

    
    x = QActivation('quantized_relu(quantized_bits(8, 1, 1, alpha=1))', name="relu30_1")(x)
    x = QConv2D(4, (3, 3), strides=(1, 1), padding='same', kernel_quantizer=quantized_bits(8, 1, 1, alpha=1), bias_quantizer=quantized_bits(8, 1, 1, alpha=1), name="conv_1")(x)

    x = BatchNormalization(name="norm_1")(x)
    x = QActivation('quantized_relu(quantized_bits(8, 1, 1, alpha=1))', name="relu_1")(x)

    
    x = AveragePooling2D((2, 2), name="pool_1")(x)

    x = Flatten(name="flatten_1")(x)
    x = QDense(16, kernel_quantizer=quantized_bits(8, 1, 1, alpha=1), bias_quantizer=quantized_bits(8, 1, 1, alpha=1), name="dense_1")(x)
    x = QActivation('quantized_relu(quantized_bits(8, 1, 1, alpha=1))', name="relu_2")(x)

    x = Dropout(0.05)(x)
    
    output_layer = QDense(2, kernel_quantizer=quantized_bits(8, 1, 1, alpha=1), bias_quantizer=quantized_bits(8, 1, 1, alpha=1), name="dense_out")(x)
    
    model = Model(inputs=input_tensor, outputs=output_layer)
    model.compile(optimizer='adam', loss=custom_mse_with_heavy_penalty)
    
    return model


def custom_mse_with_heavy_penalty(y_true, y_pred, threshold=1.0, penalty_factor=1.5):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    
    residual = y_true - y_pred
    
    small_residuals = K.square(residual)
    
    large_residuals = K.square(residual) * K.square(penalty_factor) * tf.cast(K.abs(residual) > threshold, tf.float32)
    
    combined_residuals = tf.where(K.abs(residual) < threshold, small_residuals, large_residuals)
    
    return K.mean(combined_residuals)

class LossHistory(Callback):
    def __init__(self, save_path):
        super().__init__()
        self.save_path = save_path

    def on_train_begin(self, logs={}):
        self.losses = []
        self.val_losses = []

    def on_epoch_end(self, epoch, logs={}):
        self.losses.append(logs.get('loss'))
        self.val_losses.append(logs.get('val_loss'))
        print(f'Epoch {epoch+1}: loss = {logs.get("loss")}, val_loss = {logs.get("val_loss")}')
        self.plot_losses()

    def plot_losses(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.losses, label='Training Loss')
        plt.plot(self.val_losses, label='Validation Loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.savefig(os.path.join(self.save_path, 'loss_plot.png'))
        plt.close()



def plot_heatmaps(cregions, predictions, genPhi, genEta, labels, save_path):
    plt.figure(figsize=(20, 10))
    temp = np.arange(0, 15, 1)
    
    for i in temp:
        plt.subplot(3, 5, i + 1)
        plt.imshow(cregions[i].reshape((18, 14)), cmap='viridis', aspect='auto')
        pred1 = predictions[i][:2]
        manual1 = labels[i][:2]
        
        ellipse_pred1 = patches.Ellipse((pred1[1], pred1[0]), width=3, height=3, edgecolor='blue', facecolor='none', label='Predicted')
        plt.gca().add_patch(ellipse_pred1)
        
        ellipse_true = patches.Ellipse((genEta[i], genPhi[i]), width=3, height=3, edgecolor='red', facecolor='none', label='True')
        plt.gca().add_patch(ellipse_true)
        
        ellipse_manual1 = patches.Ellipse((manual1[1], manual1[0]), width=3, height=3, edgecolor='green', facecolor='none', label='Manual')
        plt.gca().add_patch(ellipse_manual1)
        
        plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'heatmaps.png'))
    plt.close()



def main():
    parser = argparse.ArgumentParser(description='Train a model with specified parameters.')
    parser.add_argument('h5_filename', type=str, help='Path to the H5 file')
    parser.add_argument('epochs', type=int, help='Number of epochs')
    parser.add_argument('batch_size', type=int, help='Batch size')

    args = parser.parse_args()

    num_epochs = args.epochs
    file_path = args.h5_filename
    batch_size = args.batch_size


    save_path = f'metrics/modelSkeleton_epochs{num_epochs}_batch{batch_size}'
    os.makedirs(save_path, exist_ok=True)

    cregionsl, genPhi, genEta, cregions = load_data(file_path)
    labels = calculate_labels(cregions, genPhi, genEta)


    model = build_model()
    
    history = LossHistory(save_path)
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    cregions = cregions.reshape((cregions.shape[0], 18, 14, 1))
    labels = labels.reshape((labels.shape[0], 2))

    model.fit(cregions, labels, epochs=num_epochs, batch_size=batch_size, validation_split=0.2, callbacks=[history])#, early_stopping

    predictions = model.predict(cregions[:15])
    plot_heatmaps(cregions, predictions, genPhi[:15], genEta[:15], labels[:15], save_path)

    predictions = model.predict(cregions)
    evaluate_model(predictions, labels, save_path)

    model_save_path = os.path.join(save_path, 'model')
    model.save(model_save_path, save_format='tf')

if __name__ == '__main__':
    main()
