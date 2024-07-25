import h5py
import numpy as np
import tensorflow as tf
from keras.optimizers import Adam
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Input, Conv2D, ZeroPadding2D, Layer, BatchNormalization, Activation, AveragePooling2D, Flatten, Dense, Dropout
from tensorflow.keras.callbacks import Callback, EarlyStopping, ModelCheckpoint

from qkeras.qlayers import QActivation
from qkeras.quantizers import quantized_bits
from tensorflow.keras import backend as K
from keras.layers import Input
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.patches as patches
import argparse
import os
from qkeras import QConv2D, QDense
from tensorflow.keras.preprocessing.image import ImageDataGenerator


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
        pad_height, pad_width = self.padding
        input_shape = tf.shape(inputs)

        if pad_height > 0:
            top_pad = inputs[:, -pad_height:, :, :]
            bottom_pad = inputs[:, :pad_height, :, :]
            middle_section = inputs[:, pad_height:-pad_height, :, :]
            padded_inputs = tf.concat([top_pad, middle_section, bottom_pad], axis=1)
        else:
            padded_inputs = inputs

        return padded_inputs

    def compute_output_shape(self, input_shape):
        return input_shape

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

def load_data(file_path):
    with h5py.File(file_path, 'r') as f:
        cregions = f['cregions'][:]
        genPhi = f['genPhi_1'][:]
        genEta = f['genEta_1'][:]
        cregionsMetrics = f['cregions'][:] #cregions - 30.0
        # cregionsMetrics[cregionsMetrics < 0] = 0.0
    return cregions, genPhi, genEta, cregionsMetrics

def calculate_labels(cregions, genPhi, genEta):
    labels = []
    for img, phi, eta in zip(cregions, genPhi, genEta):
        heatmap = img.reshape((18, 14))
        sums = np.array([
            [np.sum(heatmap[i:i + 3, j:j + 3]) for j in range(heatmap.shape[1] - 2)]
            for i in range(heatmap.shape[0] - 2)
        ])
        phi_min, phi_max = int(phi - 3), int(phi + 3)
        eta_min, eta_max = int(max(0, eta - 3)), int(min(sums.shape[1], eta + 3))
        if (phi_min < 0) or (phi_max >= 18):
            sums_wrapped = np.concatenate((sums[phi_min:], sums[:phi_max % 18 + 1]), axis=0)
            phi_min_wrapped = phi_min % 18
            phi_max_wrapped = (phi_max % 18) + sums_wrapped.shape[0] - (phi_max % 18 + 1)
        else:
            sums_wrapped = sums[phi_min:phi_max + 1]
            phi_min_wrapped = phi_min
            phi_max_wrapped = phi_max
        sums_restricted = sums_wrapped[:, eta_min:eta_max + 1]
        largest_index = np.argmax(sums_restricted)
        largest_relative = np.unravel_index(largest_index, sums_restricted.shape)
        largest = (largest_relative[0] + phi_min_wrapped, largest_relative[1] + eta_min)
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

def build_masterModel():
    input_tensor = Input(shape=(18, 14, 1), name="inputs")
    x = input_tensor
    x = Subtract30ReLU(name="relu30_1")(x)
    x = ZeroPadding2D(padding=(1, 0), name="zero_padding")(x)
    x = CircularPadding2D(padding=(1, 0), name="padding_1")(x)
    x = Conv2D(16, (3, 3), padding='same', name="conv_1")(x)
    x = BatchNormalization(name="norm_1")(x)
    x = Activation('relu', name="relu_1")(x)
    x = Conv2D(32, (3, 3), padding='same', name="conv_2")(x)
    x = BatchNormalization(name="norm_2")(x)
    x = Activation('relu', name="relu_2")(x)
    x = Conv2D(64, (3, 3), padding='same', name="conv_3")(x)
    x = BatchNormalization(name="norm_3")(x)
    x = Activation('relu', name="relu_3")(x)
    x = AveragePooling2D((2, 2), name="pool_1")(x)
    x = Flatten(name="flatten_1")(x)
    x = Dense(128, name="dense_1")(x)
    x = Activation('relu', name="relu_4")(x)
    x = Dropout(0.5)(x)
    output_layer = Dense(2, name="dense_out")(x)
    model = Model(inputs=input_tensor, outputs=output_layer)
    model.compile(optimizer='adam', loss=custom_mse_with_heavy_penalty)
    return model

def build_apprenticeModel():
    input_tensor = Input(shape=(18, 14, 1), name="inputs")
    x = input_tensor
    x = Subtract30ReLU(name="relu30_1")(x)
    x = ZeroPadding2D(padding=(1, 0), name="zero_padding")(x)
    x = CircularPadding2D(padding=(1, 0), name="padding_1")(x)
    x = QConv2D(4, (5, 5), strides=(1, 1), padding='same', kernel_quantizer=quantized_bits(8, 1, 1, alpha=1), bias_quantizer=quantized_bits(8, 1, 1, alpha=1), name="conv_1")(x)
    x = BatchNormalization(name="norm_1")(x)
    x = QActivation('quantized_relu(quantized_bits(8, 1, 1, alpha=1))', name="relu_1")(x)
    x = AveragePooling2D((3, 3), name="pool_2")(x)
    x = Flatten(name="flatten_1")(x)
    x = QDense(16, kernel_quantizer=quantized_bits(8, 1, 1, alpha=1), bias_quantizer=quantized_bits(8, 1, 1, alpha=1), name="dense_1")(x)
    x = QActivation('quantized_relu(quantized_bits(8, 1, 1, alpha=1))', name="relu_2")(x)
    x = Dropout(0.05)(x)
    output_layer = QDense(2, kernel_quantizer=quantized_bits(8, 1, 1, alpha=1), bias_quantizer=quantized_bits(8, 1, 1, alpha=1), name="dense_out")(x)
    model = Model(inputs=input_tensor, outputs=output_layer)
    model.compile(optimizer='adam', loss=custom_mse_with_heavy_penalty)
    return model

def get_soft_targets(model, data, batch_size):
    soft_targets = model.predict(data, batch_size=batch_size)
    return soft_targets

def distillation_loss(soft_targets, temperature, alpha=0.5):
    def loss(y_true, y_pred):
        y_pred_soft = tf.nn.softmax(y_pred / temperature)
        y_true_soft = tf.nn.softmax(soft_targets[:tf.shape(y_true)[0]] / temperature)

        distillation_loss = tf.keras.losses.KLD(y_true_soft, y_pred_soft) * (temperature ** 2)
        supervised_loss = tf.keras.losses.MSE(y_true, y_pred)

        return alpha * supervised_loss + (1 - alpha) * distillation_loss
    return loss


def main():
    parser = argparse.ArgumentParser(description='Train a model with specified parameters.')
    parser.add_argument('h5_filename', type=str, help='Path to the H5 file')
    parser.add_argument('epochs', type=int, help='Number of epochs')
    parser.add_argument('batch_size', type=int, help='Batch size')
    parser.add_argument('train', type=int, help='Train new model(s): 1-yes, 0-no, 2-train only apprentice')


    args = parser.parse_args()

    num_epochs = args.epochs
    file_path = args.h5_filename
    batch_size = args.batch_size
    train = args.train

    save_path = f'metrics/modelDistillation_epochs{num_epochs}_batch{batch_size}'
    os.makedirs(save_path, exist_ok=True)

    cregionsl, genPhi, genEta, cregions = load_data(file_path)
    labels = calculate_labels(cregions, genPhi, genEta)

    cregions = cregions.reshape((cregions.shape[0], 18, 14, 1))
    labels = labels.reshape((labels.shape[0], 2))

    if train == 1:
        masterModel = build_masterModel()
        apprenticeModel = build_apprenticeModel()
        history = LossHistory(save_path)
        masterModel.fit(cregions, labels, epochs=num_epochs, batch_size=batch_size, validation_split=0.2, callbacks=[history])
        soft_targets = get_soft_targets(masterModel, cregions, batch_size)
        soft_targets = tf.convert_to_tensor(soft_targets)

    if train==2:
        masterModel = load_model("metrics/modelMaster_epochs500_batch32/model", custom_objects={'Subtract30ReLU': Subtract30ReLU, 'CircularPadding2D': CircularPadding2D, 'custom_mse_with_heavy_penalty': custom_mse_with_heavy_penalty})
        apprenticeModel = build_apprenticeModel()
        history = LossHistory(save_path)
        soft_targets = get_soft_targets(masterModel, cregions, batch_size)
        soft_targets = tf.convert_to_tensor(soft_targets)
    else:
        masterModel = load_model("metrics/modelMaster_epochs500_batch32/model", custom_objects={'Subtract30ReLU': Subtract30ReLU, 'CircularPadding2D': CircularPadding2D, 'custom_mse_with_heavy_penalty': custom_mse_with_heavy_penalty})
        apprenticeModel = load_model("metrics/modelApprentice_epochs1000_batch32/model", custom_objects={'Subtract30ReLU': Subtract30ReLU, 'CircularPadding2D': CircularPadding2D, 'custom_mse_with_heavy_penalty': custom_mse_with_heavy_penalty})
        history = LossHistory(save_path)
        soft_targets = get_soft_targets(masterModel, cregions, batch_size)
        soft_targets = tf.convert_to_tensor(soft_targets)

    temperature = 5.0
    alpha = 0.5

    # Data augmentation
    datagen = ImageDataGenerator(
        rotation_range=10,
        width_shift_range=0.1,
        height_shift_range=0.1,
        horizontal_flip=True
    )
    train_generator = datagen.flow(cregions, labels, batch_size=batch_size)

    # Learning rate schedule
    initial_learning_rate = 0.001
    lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
        initial_learning_rate, decay_steps=10000, decay_rate=0.9, staircase=True
    )
    optimizer = Adam(learning_rate=lr_schedule)

    # Compile apprentice model
    apprenticeModel.compile(
        optimizer=optimizer,
        loss=distillation_loss(soft_targets, temperature, alpha),
        metrics=['accuracy']
    )

    # Callbacks for early stopping and model checkpointing
    early_stopping = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)
    checkpoint = ModelCheckpoint('best_model.h5', monitor='val_loss', save_best_only=True)

    apprenticeModel.fit(
        train_generator,
        epochs=num_epochs,
        validation_data=(cregions, labels),
        callbacks=[history, checkpoint]#early_stopping,
    )

    predictions = apprenticeModel.predict(cregions[:15])
    plot_heatmaps(cregionsl, predictions, genPhi[:15], genEta[:15], labels[:15], save_path)

    predictions = apprenticeModel.predict(cregions)
    evaluate_model(predictions, labels, save_path)

    model_save_path = os.path.join(save_path, 'apprenticeModel')
    apprenticeModel.save(model_save_path, save_format='tf')

if __name__ == '__main__':
    main()