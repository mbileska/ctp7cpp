import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import h5py
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K

def custom_mse_with_heavy_penalty(y_true, y_pred, threshold=1.0, penalty_factor=1.5):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    
    residual = y_true - y_pred
    
    small_residuals = K.square(residual)
    
    large_residuals = K.square(residual) * K.square(penalty_factor) * tf.cast(K.abs(residual) > threshold, tf.float32)
    
    combined_residuals = tf.where(K.abs(residual) < threshold, small_residuals, large_residuals)
    
    return K.mean(combined_residuals)

def load_pb_model(model_path):
    model = tf.saved_model.load(model_path)
    return model

def predict(model, input_data):
    infer = model.signatures['serving_default']
    input_tensor = tf.convert_to_tensor(input_data, dtype=tf.float32)
    
    print("Input tensor shape:", input_tensor.shape)  # Debug statement
    
    predictions = infer(input_tensor)['output'].numpy()
    return predictions

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
        
        plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, 'heatmaps.png'))
    plt.close()

def load_data(file_path):
    with h5py.File(file_path, 'r') as f:
        cregions = f['cregions'][:]
        genPhi = f['genPhi_1'][:]
        genEta = f['genEta_1'][:]
        cregionsMetrics = cregions - 30.0
        cregionsMetrics[cregionsMetrics < 0] = 0.0
    
    print("cregions shape:", cregions.shape)  
    print("genPhi shape:", genPhi.shape)  
    print("genEta shape:", genEta.shape)  
    
    return cregions, genPhi, genEta, cregionsMetrics

def calculate_labels(cregions, genPhi, genEta):
    labels = []

    for img, phi, eta in zip(cregions, genPhi, genEta):
        heatmap = img.reshape((18, 14))
        sums = np.array([[np.sum(heatmap[i:i+3, j:j+3]) for j in range(heatmap.shape[1]-2)] for i in range(heatmap.shape[0]-2)])
        largest_index = np.argmax(sums)
        largest = np.unravel_index(largest_index, sums.shape)
        
        sums = sums.astype(float)
        sums[max(0, largest[0]-2):min(sums.shape[0], largest[0]+3), max(0, largest[1]-2):min(sums.shape[1], largest[1]+3)] = -np.inf

        phi_min, phi_max = int(max(0, phi - 3)), int(min(sums.shape[0], phi + 3))
        eta_min, eta_max = int(max(0, eta - 3)), int(min(sums.shape[1], eta + 3))
        
        second_largest_region = sums[phi_min:phi_max, eta_min:eta_max]
        second_largest_index = np.argmax(second_largest_region)
        second_largest_relative = np.unravel_index(second_largest_index, second_largest_region.shape)
        second_largest = (second_largest_relative[0] + phi_min, second_largest_relative[1] + eta_min)

        labels.append([largest[0]+1, largest[1]+1, second_largest[0]+1, second_largest[1]+1])
    
    return np.array(labels)

model_path = 'modelTrue_epochs500_batch32/model'
cregionsl, genPhi, genEta, cregions = load_data("data/dataZB.h5")
labels = calculate_labels(cregions, genPhi, genEta)
save_path = 'output/'

custom_objects = {'custom_mse_with_heavy_penalty': custom_mse_with_heavy_penalty}
model = load_model(model_path, custom_objects=custom_objects)

scores = model.predict(cregions, verbose=0)

plot_heatmaps(cregions, scores, genPhi, genEta, labels, save_path)
