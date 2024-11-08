import h5py
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (
    Input, Conv2D, MaxPooling2D, Flatten, Dense,
    Lambda, Concatenate
)
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
from tensorflow.keras.callbacks import Callback, EarlyStopping
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import os
import argparse
import matplotlib.patches as patches
from sklearn.model_selection import train_test_split
from tensorflow.keras.layers import Dropout
from sklearn.model_selection import KFold
from tensorflow.keras.models import load_model

from tensorflow.keras.regularizers import l2

def load_data(file_path):
    """
    Load the dataset from the HDF5 file and preprocess the labels.

    Parameters:
    - file_path: Path to the HDF5 file.

    Returns:
    - cregions: Input data reshaped for the model.
    - labels: Labels containing phi and eta.
    - cregionsMetrics: Original cregions data (for metrics if needed).
    """
    with h5py.File(file_path, 'r') as f:
        cregions = f['cregions'][:]
        genPhi = f['genPhi_1'][:]
        genEta = f['genEta_1'][:]
        cregionsMetrics = f['cregions'][:]
    labels = np.stack((genPhi, genEta), axis=1)
    return cregions, labels, cregionsMetrics


def get_circular_mse(max_value):
    def circular_mse(y_true, y_pred):
        diff = y_pred - y_true
        circular_diff = (diff + max_value / 2) % max_value - max_value / 2
        return tf.reduce_mean(tf.square(circular_diff))
    return circular_mse
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


def custom_loss(y_true, y_pred):
    y_true = tf.reshape(y_true, (-1, 2))  
    phi_true, eta_true = y_true[..., 0], y_true[..., 1]
    phi_pred, eta_pred = y_pred[..., 0], y_pred[..., 1]
    
    phi_loss = get_circular_mse(17.0)(phi_true, phi_pred)
    eta_loss = tf.keras.losses.mean_squared_error(eta_true, eta_pred)
    
    return phi_loss + eta_loss
def build_model():
    """
    Define and compile the model with custom layers.
    
    Returns:
    - model: Compiled Keras model.
    """
    inputs = Input(shape=(18 * 14,), name="INPUT")

    reshaped_inputs = Lambda(lambda x: tf.reshape(x, (-1, 18, 14, 1)))(inputs)

    x = Subtract30ReLU()(reshaped_inputs)

    x = CircularPadding2D(padding=(1, 0))(x)
    
    x = Conv2D(32, kernel_size=(3, 3), padding='same', activation='relu', kernel_regularizer=l2(0.001))(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)
    x = Dropout(0.25)(x)

    x = Conv2D(64, kernel_size=(3, 3), padding='same', activation='relu')(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Conv2D(128, kernel_size=(3, 3), padding='same', activation='relu')(x)
    x = MaxPooling2D(pool_size=(2, 2))(x)

    x = Flatten()(x)
    x = Dense(256, activation='relu')(x)
    x = Dense(128, activation='relu')(x)

    phi_output = Dense(1, activation='linear', name='phi_output_1')(x)
    eta_output = Dense(1, activation='linear', name='eta_output')(x)

    phi_output_scaled = Lambda(lambda y: tf.clip_by_value(y, 0, 17), name='phi_output')(phi_output)

    output = Concatenate(name='OUTPUT')([phi_output_scaled, eta_output])

    model = Model(inputs=inputs, outputs=output)

    model.compile(
        optimizer='adam',
        loss=custom_loss,
        metrics={'OUTPUT': 'mae'}
    )
    return model




def evaluate_model(predictions, labels, save_path):
    """
    Evaluate the model's predictions and save metrics and plots.

    Parameters:
    - predictions: Predicted values.
    - labels: True labels.
    - save_path: Directory to save evaluation results.
    """
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

def circular_residual(true, pred, max_value):
    """
    Compute the residuals for a circular variable.

    Parameters:
    - true: True values.
    - pred: Predicted values.
    - max_value: Maximum value of the circular variable.

    Returns:
    - residual: Circular residuals.
    """
    diff = (pred - true) % max_value
    residual = np.where(diff > max_value / 2, diff - max_value, diff)
    return residual

def wrapped_mae(y_true, y_pred, max_value):
    """
    Compute the Mean Absolute Error for a circular dimension.

    Parameters:
    - y_true: True values.
    - y_pred: Predicted values.
    - max_value: Maximum value of the circular variable.

    Returns:
    - MAE: Wrapped Mean Absolute Error.
    """
    residuals = circular_residual(y_true, y_pred, max_value)
    return np.mean(np.abs(residuals))

def wrapped_mse(y_true, y_pred, max_value):
    """
    Compute the Mean Squared Error for a circular dimension.

    Parameters:
    - y_true: True values.
    - y_pred: Predicted values.
    - max_value: Maximum value of the circular variable.

    Returns:
    - MSE: Wrapped Mean Squared Error.
    """
    residuals = circular_residual(y_true, y_pred, max_value)
    return np.mean(residuals ** 2)

def wrapped_r2_score(y_true, y_pred, max_value):
    """
    Compute the R^2 score for a circular dimension.

    Parameters:
    - y_true: True values.
    - y_pred: Predicted values.
    - max_value: Maximum value of the circular variable.

    Returns:
    - R^2 Score: Wrapped R^2 score.
    """
    residuals = circular_residual(y_true, y_pred, max_value)
    total_variance = np.var(y_true)
    return 1 - (np.mean(residuals ** 2) / total_variance)

def evaluate_model_wrap(predictions, labels, save_path):
    """
    Evaluates the model's predictions against the true labels, handling circular residuals for phi.

    Parameters:
    - predictions: NumPy array of predicted phi and eta values.
    - labels: NumPy array of true phi and eta values.
    - save_path: Directory to save evaluation results.
    """
    max_phi = 17.0  
    max_eta = 13.0  

    phi_true = labels[:, 0]
    eta_true = labels[:, 1]
    phi_pred = predictions[:, 0]
    eta_pred = predictions[:, 1]

    residuals_phi = circular_residual(phi_true, phi_pred, max_phi)
    residuals_eta = eta_true - eta_pred

    mae_phi = wrapped_mae(phi_true, phi_pred, max_phi)
    mse_phi = wrapped_mse(phi_true, phi_pred, max_phi)
    rmse_phi = np.sqrt(mse_phi)
    r2_phi = wrapped_r2_score(phi_true, phi_pred, max_phi)

    mae_eta = mean_absolute_error(eta_true, eta_pred)
    mse_eta = mean_squared_error(eta_true, eta_pred)
    rmse_eta = np.sqrt(mse_eta)
    r2_eta = r2_score(eta_true, eta_pred)

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

    print("\nModel Evaluation Metrics (Wrapped):")
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

def load_pretrained_model(pretrained_model_path):
    """
    Load the pre-trained model from a given file path.
    Fine-tune by unfreezing the final layers.
    
    Parameters:
    - pretrained_model_path: Path to the pre-trained model file (.h5 or saved model format)
    
    Returns:
    - model: The pre-trained model ready for fine-tuning
    """
    model = load_model(pretrained_model_path, custom_objects={'circular_mse': circular_mse})

    for layer in model.layers:  
        layer.trainable = True

    model.compile(
        optimizer='adam',
        loss={
            'phi_output': circular_mse,
            'eta_output': 'mean_squared_error'
        },
        metrics={
            'phi_output': 'mae',
            'eta_output': 'mae'
        }
    )
    
    return model

def main():
    parser = argparse.ArgumentParser(description='Train a model with specified parameters.')
    parser.add_argument('h5_filename', type=str, help='Path to the H5 file')
    parser.add_argument('epochs', type=int, help='Number of epochs to fine-tune the model')
    parser.add_argument('batch_size', type=int, help='Batch size')
    parser.add_argument('--pretrained_model', type=str, help='Path to a pre-trained model file (optional)', default=None)
    parser.add_argument('--pretrained_epochs', type=int, help='Specify pre-trained epochs if history is unavailable', default=0)

    args = parser.parse_args()

    num_epochs = args.epochs
    file_path = args.h5_filename
    batch_size = args.batch_size
    pretrained_model_path = args.pretrained_model
    manual_pretrained_epochs = args.pretrained_epochs

    cregions, labels, cregionsMetrics = load_data(file_path)
    cregions = cregions.reshape((-1, 18 * 14)) 

    phi_labels = labels[:, 0]  
    eta_labels = labels[:, 1]  

    if pretrained_model_path:
        model = load_pretrained_model(pretrained_model_path)
        pretrained_epochs = manual_pretrained_epochs
    else:
        model = build_model()
        pretrained_epochs = 0

    total_epochs = pretrained_epochs + num_epochs

    save_path = f'metrics/model_epochs{total_epochs}_pretrained{pretrained_epochs}_fine{num_epochs}_batch{batch_size}'
    os.makedirs(save_path, exist_ok=True)
    history = LossHistory(save_path)

    kf = KFold(n_splits=5)
    for train_index, val_index in kf.split(cregions):
        x_train, x_val = cregions[train_index], cregions[val_index]
        y_train, y_val = labels[train_index], labels[val_index]

        model.fit(
            x_train, y_train,  
            validation_data=(x_val, y_val),
            epochs=num_epochs,  
            batch_size=batch_size,
            callbacks=[history],
            verbose=2
        )

    predictions = model.predict(cregions)

    model_save_path = os.path.join(save_path, 'model')
    model.save(model_save_path, save_format='tf')
    evaluate_model(predictions, labels, save_path)
    evaluate_model_wrap(predictions, labels, save_path)
    plot_heatmaps(cregions[:15].reshape((-1, 18, 14)), predictions[:15], phi_labels[:15], eta_labels[:15], labels[:15], save_path)


if __name__ == '__main__':
    main()
