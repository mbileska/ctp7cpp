import h5py
import numpy as np
import tensorflow as tf
from keras.optimizers import Adam
import os
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, Layer,ZeroPadding2D, BatchNormalization, PReLU, AveragePooling2D, Concatenate, Flatten, Dense, Dropout, Lambda, Subtract
from tensorflow.keras.callbacks import Callback, EarlyStopping
from qkeras.qlayers import QActivation
from qkeras.quantizers import quantized_bits
from tensorflow.keras import backend as K
from keras.layers import Input, Conv2D, BatchNormalization, Activation, AveragePooling2D, Flatten, Dense, Subtract, ReLU

import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.patches as patches
import argparse
import os
from tensorflow.keras.layers import (
    Input,
    Conv2D,
    Layer,
    BatchNormalization,
    Activation,
    MaxPooling2D,
    UpSampling2D,
    Concatenate,
    Flatten,
    Dense,
    Dropout,
    Lambda,
)
from qkeras import QConv2D, QDense, QActivation
from qkeras import QActivation, QConv2D, QDense, quantized_bits


from keras.layers import Input, Reshape, BatchNormalization, AveragePooling2D, Flatten, Lambda




def load_data(file_path):
    with h5py.File(file_path, 'r') as f:
        cregions = f['cregions'][:]
        genPhi = f['genPhi_1'][:]
        genEta = f['genEta_1'][:]
        cregionsMetrics = f['cregions'][:] 
    return cregions, genPhi, genEta, cregionsMetrics

def circular_mse(y_true, y_pred, max_value=17):
    """
    Computes the Mean Squared Error for a circular dimension like phi.

    Parameters:
    - y_true: Tensor of true values.
    - y_pred: Tensor of predicted values.
    - max_value: The maximum value for the circular dimension (e.g., 18 for phi).

    Returns:
    - Circular MSE as a scalar tensor.
    """
    diff = y_pred - y_true

    circular_diff = (diff + max_value / 2) % max_value - max_value / 2

    return tf.reduce_mean(tf.square(circular_diff))








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

class CircularPadding2D(Layer):
    def __init__(self, padding=(1, 0), **kwargs):
        self.padding = padding
        super(CircularPadding2D, self).__init__(**kwargs)

    def call(self, inputs):
        pad_phi, pad_eta = self.padding 


        if pad_phi > 0:
            left_pad = inputs[:, -pad_phi:, :, :]  
            right_pad = inputs[:, :pad_phi, :, :] 
            inputs = tf.concat([left_pad, inputs, right_pad], axis=1) 



        if pad_eta > 0:
            inputs = tf.pad(inputs, [[0, 0], [0, 0], [pad_eta, pad_eta], [0, 0]], mode='CONSTANT')


        return inputs

    def compute_output_shape(self, input_shape):
        shape = list(input_shape)
        shape[1] += 2 * self.padding[0]  
        shape[2] += 2 * self.padding[1] 
        return tuple(shape)

    def remove_padding(self, inputs):
        pad_phi, pad_eta = self.padding
        if pad_phi > 0:
            inputs = inputs[:, pad_phi:-pad_phi, :, :]
        if pad_eta > 0:
            inputs = inputs[:, :, pad_eta:-pad_eta, :]
        return inputs





def encoder_block(x, filters, kernel_size=(3, 3), strides=(1, 1), padding='same',
                  use_circular_padding=False, circular_padding_layer=None):
    if use_circular_padding and circular_padding_layer:
        x = circular_padding_layer(x)  # Apply circular padding only on the phi dimension
    x = Conv2D(filters, kernel_size=kernel_size, strides=strides, padding=padding)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    if use_circular_padding and circular_padding_layer:
        x = circular_padding_layer.remove_padding(x)  # Remove the padding after convolution
    return x

def decoder_block(x, filters, kernel_size=(3, 3), strides=(1, 1), padding='same',
                  use_circular_padding=False, circular_padding_layer=None):
    if use_circular_padding and circular_padding_layer:
        x = circular_padding_layer(x)  # Apply circular padding only on the phi dimension
    x = Conv2D(filters, kernel_size=kernel_size, strides=strides, padding=padding)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    if use_circular_padding and circular_padding_layer:
        x = circular_padding_layer.remove_padding(x)  # Remove the padding after convolution
    return x



def autoencoder_model():
    circular_padding_layer = CircularPadding2D(padding=(1, 0)) 
    inputs = Input(shape=(18, 14, 1), name="INPUT")

    x = Subtract30ReLU()(inputs)

    x = encoder_block(x, 32, use_circular_padding=True, circular_padding_layer=circular_padding_layer)
    x = MaxPooling2D(pool_size=(2, 1), strides=(2, 1))(x)

    x = encoder_block(x, 64, use_circular_padding=True, circular_padding_layer=circular_padding_layer)
    x = MaxPooling2D(pool_size=(2, 1), strides=(2, 1))(x)

    x = encoder_block(x, 128, use_circular_padding=True, circular_padding_layer=circular_padding_layer)

    shape_before_flatten = K.int_shape(x)
    x = Flatten()(x)
    latent = Dense(128, activation='relu', name='latent_vector')(x)

    coord = Dense(64, activation='relu')(latent)
    coord = Dense(32, activation='relu')(coord)
    coord = Dense(2, activation='sigmoid')(coord)

    phi_output = Lambda(lambda x: x[:, 0:1] * 17, name='phi_output')(coord)
    eta_output = Lambda(lambda x: x[:, 1:2] * 13, name='eta_output')(coord)

    x = Dense(np.prod(shape_before_flatten[1:]), activation='relu')(latent)
    x = Reshape(shape_before_flatten[1:])(x)

    x = UpSampling2D(size=(2, 1))(x) 
    x = decoder_block(x, 128, use_circular_padding=True, circular_padding_layer=circular_padding_layer)

    x = UpSampling2D(size=(2, 1))(x) 
    x = decoder_block(x, 64, use_circular_padding=True, circular_padding_layer=circular_padding_layer)

    x = Lambda(lambda x: tf.pad(x, [[0, 0], [1, 1], [0, 0], [0, 0]], mode='CONSTANT'))(x)  # Phi: 16 -> 18

    x = Conv2D(1, kernel_size=(3, 3), padding='same', activation='sigmoid', name='reconstructed_output')(x)

    model = Model(inputs=inputs, outputs=[phi_output, eta_output, x])

    return model


def build_model():

    model = autoencoder_model()

    model.compile(
        optimizer='adam',
        loss={
            # 'phi_output': circular_mse, 
            'phi_output': 'mean_squared_error',   
            'eta_output': 'mean_squared_error',
            'reconstructed_output': 'binary_crossentropy'
        },
        loss_weights={
            'phi_output': 1.0,
            'eta_output': 1.0,
            'reconstructed_output': 0.000001
        },
        metrics={
            'phi_output': 'mae',
            'eta_output': 'mae',
            'reconstructed_output': 'accuracy'
        }
    )


    return model



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
        plt.subplot(3, 5, i+1)
        plt.imshow(cregions[i].reshape((18, 14)), cmap='viridis', aspect='auto')
        pred1 = predictions[i][:2]
        manual1 = labels[i][:2]
        
        ellipse_pred1 = patches.Ellipse((pred1[1], pred1[0]), width=3, height=3, edgecolor='blue', facecolor='none', label='Predicted')
        plt.gca().add_patch(ellipse_pred1)
        

        
        ellipse_manual1 = patches.Ellipse((manual1[1], manual1[0]), width=3, height=3, edgecolor='red', facecolor='none', label='True')
        plt.gca().add_patch(ellipse_manual1)
        
        plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'heatmaps.png'))
    plt.close()

def plot_mse_heatmap(cregions, reconstructed_output, save_path):
    """
    Plots the Mean Squared Error (MSE) between the original and reconstructed grid regions
    as a heatmap based on phi (y-axis) and eta (x-axis).
    
    Parameters:
    - cregions: The original grid regions (shape: [num_samples, 18, 14, 1]).
    - reconstructed_output: The reconstructed output from the model (shape: [num_samples, 18, 14, 1]).
    - save_path: Path where the heatmap image will be saved.
    """
    
    # Ensure cregions and reconstructed_output are properly shaped
    cregions = cregions.reshape((-1, 18, 14))
    reconstructed_output = reconstructed_output.reshape((-1, 18, 14))
    
    # Calculate MSE for each grid point (phi, eta)
    mse_grid = np.mean((cregions - reconstructed_output) ** 2, axis=0)
    
    # Plot the MSE as a heatmap
    plt.figure(figsize=(8, 6))
    plt.imshow(mse_grid, cmap='viridis', aspect='auto')
    plt.colorbar(label='MSE')
    
    # Set axis labels and titles
    plt.xlabel('Eta (x-axis)')
    plt.ylabel('Phi (y-axis)')
    plt.title('Mean Squared Error (MSE) Heatmap for Reconstructed Grid')
    
    # Save the heatmap
    plt.savefig(os.path.join(save_path, 'mse_heatmap.png'))
    plt.close()

    print(f"Heatmap saved to {os.path.join(save_path, 'mse_heatmap.png')}")


def plot_phi_eta_mse_heatmaps(labels, phi_pred, eta_pred, save_path):
    """
    Plots the MSE of predicted phi and eta values on separate phi-eta grids, with:
    - Phi on the y-axis
    - Eta on the x-axis

    Parameters:
    - labels: The true phi and eta values (shape: [num_samples, 2]).
    - phi_pred: The predicted phi values (shape: [num_samples, 1]).
    - eta_pred: The predicted eta values (shape: [num_samples, 1]).
    - save_path: Path where the heatmap images will be saved.
    """
    
    phi_true = labels[:, 0]
    eta_true = labels[:, 1]
    
    phi_grid = np.linspace(0, 17, 18) 
    eta_grid = np.linspace(0, 13, 14) 
    
    mse_phi_grid, _, _ = np.histogram2d(
        eta_true, 
        phi_true, 
        bins=[eta_grid, phi_grid], 
        weights=(phi_true - phi_pred[:, 0])**2
    )
    mse_eta_grid, _, _ = np.histogram2d(
        eta_true, 
        phi_true, 
        bins=[eta_grid, phi_grid], 
        weights=(eta_true - eta_pred[:, 0])**2
    )
    
    phi_count, _, _ = np.histogram2d(
        eta_true, 
        phi_true, 
        bins=[eta_grid, phi_grid]
    )
    eta_count, _, _ = np.histogram2d(
        eta_true, 
        phi_true, 
        bins=[eta_grid, phi_grid]
    )
    
    mse_phi_grid /= np.maximum(phi_count, 1) 
    mse_eta_grid /= np.maximum(eta_count, 1)  
    
    extent = [eta_grid[0], eta_grid[-1], phi_grid[0], phi_grid[-1]]
    
    # Plot MSE for phi
    plt.figure(figsize=(8, 6))
    plt.imshow(
        mse_phi_grid.T, 
        cmap='viridis', 
        aspect='auto', 
        origin='lower', 
        extent=extent,
        interpolation='nearest'
    )
    plt.colorbar(label='MSE of Phi')
    plt.xlabel('Eta (x-axis)')
    plt.ylabel('Phi (y-axis)')
    plt.title('MSE of Phi on Phi-Eta Grid')
    plt.savefig(os.path.join(save_path, 'mse_phi_heatmap.png'))
    plt.close()

    # Plot MSE for eta
    plt.figure(figsize=(8, 6))
    plt.imshow(
        mse_eta_grid.T, 
        cmap='viridis', 
        aspect='auto', 
        origin='lower', 
        extent=extent,
        interpolation='nearest'
    )
    plt.colorbar(label='MSE of Eta')
    plt.xlabel('Eta (x-axis)')
    plt.ylabel('Phi (y-axis)')
    plt.title('MSE of Eta on Phi-Eta Grid')
    plt.savefig(os.path.join(save_path, 'mse_eta_heatmap.png'))
    plt.close()
    
    print(f"MSE heatmaps saved to {save_path}")

def circular_residual(true, pred, max_value):
    diff = (pred - true) % max_value
    residual = np.where(diff > max_value / 2, diff - max_value, diff)
    return residual


def wrapped_mse(y_true, y_pred, max_value):
    """
    Compute the Mean Squared Error for a circular dimension.
    """
    residuals = circular_residual(y_true, y_pred, max_value)
    return tf.reduce_mean(tf.square(residuals))


def wrapped_mae(y_true, y_pred, max_value):
    """
    Compute the Mean Absolute Error for a circular dimension.
    """
    residuals = circular_residual(y_true, y_pred, max_value)
    return tf.reduce_mean(tf.abs(residuals))


def wrapped_r2_score(y_true, y_pred, max_value):
    """
    Compute the R^2 score for a circular dimension.
    """
    y_true = tf.cast(y_true, tf.float64)
    y_pred = tf.cast(y_pred, tf.float64)

    residuals = circular_residual(y_true, y_pred, max_value)
    
    total_variance = tf.reduce_mean(tf.square(y_true - tf.reduce_mean(y_true)))

    total_variance = tf.cast(total_variance, tf.float64)

    return 1 - tf.reduce_mean(tf.square(residuals)) / total_variance





def evaluate_model_wrap(predictions, labels, save_path):
    """
    Evaluates the model's predictions against the true labels, handling circular residuals for phi.

    Parameters:
    - predictions: NumPy array of shape (num_samples, 2), where columns correspond to phi and eta predictions.
    - labels: NumPy array of shape (num_samples, 2), where columns correspond to true phi and eta values.
    - save_path: Directory path to save the evaluation plots.
    """
    
    max_phi = 17
    max_eta = 14 
    
    if isinstance(predictions, tf.Tensor):
        predictions = predictions.numpy()
    if isinstance(labels, tf.Tensor):
        labels = labels.numpy()
    
    residuals_phi = circular_residual(labels[:, 0], predictions[:, 0], max_phi)
    residuals_eta = labels[:, 1] - predictions[:, 1]
    
    mae_phi = wrapped_mae(labels[:, 0], predictions[:, 0], max_phi)
    mse_phi = wrapped_mse(labels[:, 0], predictions[:, 0], max_phi)
    r2_phi = wrapped_r2_score(labels[:, 0], predictions[:, 0], max_phi)

    mae_eta = mean_absolute_error(labels[:, 1], predictions[:, 1])
    mse_eta = mean_squared_error(labels[:, 1], predictions[:, 1])
    r2_eta = r2_score(labels[:, 1], predictions[:, 1])

    rmse_phi = np.sqrt(mse_phi)
    rmse_eta = np.sqrt(mse_eta)

    metrics = {
        "Phi MAE": mae_phi,
        "Phi MSE": mse_phi,
        "Phi RMSE": rmse_phi,
        "Phi R^2 Score": r2_phi,
        "Eta MAE": mae_eta,
        "Eta MSE": mse_eta,
        "Eta RMSE": rmse_eta,
        "Eta R^2 Score": r2_eta,
    }
    
    print("\nModel Evaluation Metrics:")
    for metric, value in metrics.items():
        print(f"{metric}: {value}")
    
    os.makedirs(save_path, exist_ok=True)
    
    plt.figure(figsize=(10, 5))
    plt.hist(residuals_phi, bins=50, color='blue', alpha=0.7)
    plt.title('Phi Residuals Distribution (Wrapped)')
    plt.xlabel('Phi Residual')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(save_path, 'phi_residuals_distribution.png'))
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.hist(residuals_eta, bins=50, color='green', alpha=0.7)
    plt.title('Eta Residuals Distribution')
    plt.xlabel('Eta Residual')
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(save_path, 'eta_residuals_distribution.png'))
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.hist(residuals_phi, bins=50, color='blue', alpha=0.5, label='Phi Residuals (Wrapped)')
    plt.hist(residuals_eta, bins=50, color='green', alpha=0.5, label='Eta Residuals')
    plt.title('Combined Residuals Distribution')
    plt.xlabel('Residual')
    plt.ylabel('Frequency')
    plt.legend()
    plt.savefig(os.path.join(save_path, 'combined_residuals_distribution.png'))
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.scatter(labels[:, 0], predictions[:, 0], alpha=0.5, color='blue', label='Phi Predictions')
    plt.title('Phi Prediction vs Actual')
    plt.xlabel('Actual Phi')
    plt.ylabel('Predicted Phi')
    plt.legend()
    plt.savefig(os.path.join(save_path, 'phi_prediction_vs_actual.png'))
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.scatter(labels[:, 1], predictions[:, 1], alpha=0.5, color='green', label='Eta Predictions')
    plt.title('Eta Prediction vs Actual')
    plt.xlabel('Actual Eta')
    plt.ylabel('Predicted Eta')
    plt.legend()
    plt.savefig(os.path.join(save_path, 'eta_prediction_vs_actual.png'))
    plt.close()
class EvaluateEveryN(Callback):
    def __init__(self, every_n_epochs, num_epochs, batch_size, full_data=None):
        super().__init__()
        self.every_n_epochs = every_n_epochs
        self.num_epochs = num_epochs
        self.batch_size = batch_size
        self.full_data = full_data  
        self.save_path = f'metrics/INTERM_modelMasterV2.2_epochs{num_epochs}_batch{batch_size}'

    def on_epoch_end(self, epoch, logs=None):
        if (epoch + 1) % self.every_n_epochs == 0:
            epoch_save_path = os.path.join(self.save_path, f'epoch_{epoch+1}')
            os.makedirs(epoch_save_path, exist_ok=True)
            print(f"\nEpoch {epoch+1}: Performing evaluation on the entire dataset and saving model to {epoch_save_path}.")

            cregions_full, labels_full = self.full_data

            phi_pred, eta_pred, reconstructed_output = self.model.predict(cregions_full)

            predictions = np.concatenate([phi_pred, eta_pred], axis=1)
            rounded_predictions = np.round(predictions).astype(int)
            rounded_predictions[:, 0] = np.clip(rounded_predictions[:, 0], 0, 17)
            rounded_predictions[:, 1] = np.clip(rounded_predictions[:, 1], 0, 13)

            evaluate_model(predictions, labels_full, epoch_save_path)
            evaluate_model_wrap(predictions, labels_full, epoch_save_path)

            self.model.save(os.path.join(epoch_save_path, f'model_epoch_{epoch+1}'), save_format='tf')
def save_results_to_txt(cregions, genPhi, genEta, phi_pred, eta_pred, filename='results.txt'):
    """
    Save the cregions, true eta/phi, and predicted eta/phi to a text file.

    Parameters:
    - cregions: The 18x14 input region arrays.
    - genPhi: True phi values.
    - genEta: True eta values.
    - phi_pred: Predicted phi values.
    - eta_pred: Predicted eta values.
    - filename: Output filename.
    """
    with open(filename, 'w') as f:
        for i in range(len(cregions)):
            f.write(f"Event {i + 1}:\n")
            f.write("CRegions (18x14):\n")
            for row in cregions[i].reshape((18, 14)):
                f.write(" ".join(f"{val:6.2f}" for val in row) + "\n")

            f.write(f"True Phi: {genPhi[i]:.2f}, True Eta: {genEta[i]:.2f}\n")
            f.write(f"Predicted Phi: {phi_pred[i][0]:.2f}, Predicted Eta: {eta_pred[i][0]:.2f}\n")
            f.write("\n" + "="*50 + "\n\n")

    print(f"Results saved to {filename}")


def main():
    parser = argparse.ArgumentParser(description='Train a model with specified parameters.')
    parser.add_argument('h5_filename', type=str, help='Path to the H5 file')
    parser.add_argument('epochs', type=int, help='Number of epochs')
    parser.add_argument('batch_size', type=int, help='Batch size')

    args = parser.parse_args()

    num_epochs = args.epochs
    file_path = args.h5_filename
    batch_size = args.batch_size


    save_path = f'metrics/modelMasterV2.2_epochs{num_epochs}_batch{batch_size}'
    os.makedirs(save_path, exist_ok=True)

    cregionsl, genPhi, genEta, cregions = load_data(file_path)
    labels = np.stack((genPhi, genEta), axis=1)


    model = build_model()
    evaluation_callback = EvaluateEveryN(
        every_n_epochs=100,
        num_epochs=num_epochs,
        batch_size=batch_size,
        full_data=(cregions, labels) 
    )
    history = LossHistory(save_path)
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

    cregions = cregions.reshape((cregions.shape[0], 18, 14, 1))
    labels = labels.reshape((labels.shape[0], 2))

    model.fit(
        cregions, 
        {
            'phi_output': labels[:, 0],  
            'eta_output': labels[:, 1],  
            'reconstructed_output': cregions 
        },
        epochs=num_epochs,
        batch_size=batch_size,
        validation_split=0.2,
        callbacks=[history, evaluation_callback],
        verbose=2
    )
 
    phi_pred, eta_pred, reconstructed_output = model.predict(cregions)

 
    plot_mse_heatmap(cregions, reconstructed_output, save_path)
 
    predictions = np.concatenate([phi_pred, eta_pred], axis=1)

 
    rounded_predictions = np.round(predictions).astype(int)

 
    rounded_predictions[:, 0] = np.clip(rounded_predictions[:, 0], 0, 17)  # Phi (0 to 17)
    rounded_predictions[:, 1] = np.clip(rounded_predictions[:, 1], 0, 13)  # Eta (0 to 13)



 
    plot_heatmaps(cregions[:15], predictions[:15], genPhi[:15], genEta[:15], labels[:15], save_path)


    model_save_path = os.path.join(save_path, 'model')
    model.save(model_save_path, save_format='tf')
    plot_phi_eta_mse_heatmaps(labels, phi_pred, eta_pred, save_path)

    evaluate_model(predictions, labels, save_path)
    evaluate_model_wrap(predictions, labels, save_path)
    save_results_to_txt(cregions, genPhi, genEta, phi_pred, eta_pred)




if __name__ == '__main__':
    main()
