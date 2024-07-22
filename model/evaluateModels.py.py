import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import h5py
from tensorflow.keras.models import load_model
from tensorflow.keras import backend as K
from sklearn.metrics import roc_curve, auc, mean_squared_error, r2_score

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

def plot_heatmaps(cregions, predictions, labels, save_path, model_name):
    plt.figure(figsize=(20, 10))
    temp = np.arange(0, 15, 1)
    
    for i in temp:
        plt.subplot(3, 5, i + 1)
        plt.imshow(cregions[i].reshape((18, 14)), cmap='viridis', aspect='auto')
        pred1 = predictions[i]
        manual1 = labels[i]
        
        ellipse_pred1 = patches.Ellipse((pred1[1], pred1[0]), width=3, height=3, edgecolor='blue', facecolor='none', label='Predicted')
        plt.gca().add_patch(ellipse_pred1)
        
        ellipse_true = patches.Ellipse((labels[1], labels[0]), width=3, height=3, edgecolor='red', facecolor='none', label='True')
        plt.gca().add_patch(ellipse_true)
        
        plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, f'heatmaps_{model_name}.png'))
    plt.close()

def load_data(file_path):
    with h5py.File(file_path, 'r') as f:
        cregions = f['cregions'][:]
        genPhi = f['genPhi_1'][:]
        genEta = f['genEta_1'][:]
        genPt = f['genPt_1'][:]
        cregionsMetrics = f['cregions'][:]#cregions - 30.0
        # cregionsMetrics[cregionsMetrics < 0] = 0.0
    
    return cregions, genPhi, genEta, cregionsMetrics, genPt

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


def create_combined_dataset(zb_cregions1, hbb_cregions1, zb_cregions, hbb_cregions, zb_genPhi, hbb_genPhi, zb_genEta, hbb_genEta):
    min_length = min(len(zb_cregions), len(hbb_cregions))
    zb_cregions = zb_cregions[:min_length]
    zb_cregions1 = zb_cregions1[:min_length]

    zb_genPhi = zb_genPhi[:min_length]
    zb_genEta = zb_genEta[:min_length]
    hbb_cregions = hbb_cregions[:min_length]
    hbb_cregions1 = hbb_cregions1[:min_length]

    hbb_genPhi = hbb_genPhi[:min_length]
    hbb_genEta = hbb_genEta[:min_length]
    
    combined_cregions = np.vstack((zb_cregions, hbb_cregions))
    combined_cregions1 = np.vstack((zb_cregions1, hbb_cregions1))

    combined_genPhi = np.hstack((zb_genPhi, hbb_genPhi))
    combined_genEta = np.hstack((zb_genEta, hbb_genEta))
    
    labels = np.array(['ZB'] * min_length + ['HBB'] * min_length)
    
    return combined_cregions1, combined_cregions, combined_genPhi, combined_genEta, labels

def determine_event_type(zb_predictions, predictions, threshold=0.5):
    avg_zb_predictions = np.mean(zb_predictions, axis=0)
    upper_bound = avg_zb_predictions + threshold
    lower_bound = avg_zb_predictions - threshold

    event_types = []
    for pred in predictions:
        if np.all(pred >= lower_bound) and np.all(pred <= upper_bound):
            event_types.append('ZB')
        else:
            event_types.append('HBB')

    return np.array(event_types)

def plot_efficiency(predictions, cregions, true_labels, save_path, pt_values, model_name):
    true_labels = np.array(true_labels, dtype=int)
    tolerance = 2
    accuracies = []

    for i in range(len(predictions)):
        pred_phi, pred_eta = predictions[i]
        true_phi, true_eta = true_labels[i]

        pred_phi = int(np.clip(pred_phi, 1, 16))
        pred_eta = int(np.clip(pred_eta, 1, 12))
        
        true_phi = int(np.clip(true_phi, 1, 16))
        true_eta = int(np.clip(true_eta, 1, 12))
        
        accurate = (abs(pred_phi - true_phi) <= tolerance) and (abs(pred_eta - true_eta) <= tolerance)
        accuracies.append(accurate)

    pt_values = np.array(pt_values)
    accuracies = np.array(accuracies)

    num_bins = 30
    bins = np.linspace(min(pt_values), 600, num_bins)
    bin_indices = np.digitize(pt_values, bins)

    bin_efficiency = []
    for bin_idx in range(1, len(bins)):
        bin_mask = bin_indices == bin_idx
        bin_accuracy = accuracies[bin_mask]
        if len(bin_accuracy) > 0:
            bin_efficiency.append(np.mean(bin_accuracy))
        else:
            bin_efficiency.append(0)

    plt.figure(figsize=(10, 6))
    plt.plot(bins[1:-1], bin_efficiency[1:], 'o-', label='Efficiency')

    plt.xlabel('Pt (GeV)')
    plt.ylabel('Fraction of Accurate Grid Position Predictions')
    plt.ylim(0, 1.1)

    plt.legend()
    plt.savefig(os.path.join(save_path, f'efficiency_{model_name}.png'))
    plt.close()

def plot_roc_curve(event_types, combined_labels, save_path, model_name):
    y_true = np.array([1 if label == 'HBB' else 0 for label in combined_labels])
    y_scores = np.array([1 if event == 'HBB' else 0 for event in event_types])
    
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(10, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.ylim(0, 1)

    plt.legend(loc="lower right")
    plt.savefig(os.path.join(save_path, f'roc_curve_{model_name}.png'))
    plt.close()

def evaluate_hbb_predictions(hbb_cregions, hbb_labels, model, save_path, model_name):
    hbb_predictions = model.predict(hbb_cregions, verbose=0)
    hbb_predictions[:, 0] = np.clip(hbb_predictions[:, 0], 1, 16)
    hbb_predictions[:, 1] = np.clip(hbb_predictions[:, 1], 1, 12)
    
    hbb_labels[:, 0] = np.clip(hbb_labels[:, 0], 1, 16)
    hbb_labels[:, 1] = np.clip(hbb_labels[:, 1], 1, 12)

    tolerance = 2
    correct_predictions_hbb = (np.abs(hbb_predictions - hbb_labels) <= tolerance).all(axis=1)
    accuracy_hbb = np.mean(correct_predictions_hbb)
    print(f'HBB accuracy ({model_name}): {accuracy_hbb:.2f}')

    plt.figure(figsize=(10, 6))
    plt.scatter(hbb_labels[:, 1], hbb_labels[:, 0], color='red', label='True Position')
    plt.scatter(hbb_predictions[:, 1], hbb_predictions[:, 0], color='blue', label='Predicted Position', marker='x')
    plt.xlabel('Eta')
    plt.ylabel('Phi')
    plt.title('HBB Event Predictions')
    plt.legend()
    plt.savefig(os.path.join(save_path, f'hbb_predictions_splatter_{model_name}.png'))
    plt.close()

    return hbb_predictions, correct_predictions_hbb

def plot_accuracy_by_grid_position(predictions, labels, save_path, model_name):
    tolerance = 2
    correct_predictions = (np.abs(predictions - labels) <= tolerance).all(axis=1)
    accuracy_grid = np.zeros((18, 14))

    for i in range(18):
        for j in range(14):
            mask = (labels[:, 0] == i) & (labels[:, 1] == j)
            if np.sum(mask) > 0:
                accuracy_grid[i, j] = np.mean(correct_predictions[mask])
    
    plt.figure(figsize=(12, 8))
    plt.imshow(accuracy_grid, cmap='viridis', aspect='auto')
    plt.colorbar(label='Accuracy')
    plt.xlabel('Eta')
    plt.ylabel('Phi')
    plt.title('Accuracy by Grid Position')
    plt.savefig(os.path.join(save_path, f'accuracy_by_grid_position_{model_name}.png'))
    plt.close()

def calculate_metrics(predictions, labels):
    mse = mean_squared_error(labels, predictions)
    r2 = r2_score(labels, predictions)
    accuracy_with_tolerance = np.mean((np.abs(predictions[:, 0] - labels[:, 0]) <= 2) & 
                                      (np.abs(predictions[:, 1] - labels[:, 1]) <= 2))
    
    print(f'MSE: {mse:.2f}')
    print(f'R^2: {r2:.2f}')
    print(f'Accuracy with ±3 tolerance: {accuracy_with_tolerance:.2f}')
    
    return mse, r2, accuracy_with_tolerance

def evaluate_model(model_path, model_name, zb_cregions, hbb_cregions, hbb_labels, combined_cregions, combined_labels, save_path, genPt):
    custom_objects = {'custom_mse_with_heavy_penalty': custom_mse_with_heavy_penalty}
    model = load_model(model_path, custom_objects=custom_objects)

    zb_predictions = model.predict(zb_cregions, verbose=0)
    zb_predictions = np.array(zb_predictions).astype(int)

    combined_predictions = model.predict(combined_cregions, verbose=0)
    combined_predictions = np.array(combined_predictions).astype(int)

    event_types = determine_event_type(zb_predictions, combined_predictions)
    hbb_predictions, correct_predictions_hbb = evaluate_hbb_predictions(hbb_cregions, hbb_labels, model, save_path, model_name)

    plot_efficiency(hbb_predictions, hbb_cregions, hbb_labels, save_path, genPt, model_name)
    plot_roc_curve(event_types, combined_labels, save_path, model_name)
    plot_accuracy_by_grid_position(hbb_predictions, hbb_labels, save_path, model_name)
    # plot_heatmaps(hbb_cregions, hbb_predictions,  hbb_labels, save_path, model_name)

    mse, r2, accuracy_with_tolerance = calculate_metrics(hbb_predictions, hbb_labels)

    correct_predictions = (event_types == combined_labels)
    accuracy = np.mean(correct_predictions)
    print(f'Overall accuracy ({model_name}): {accuracy:.2f}')

    plt.figure(figsize=(10, 6))
    plt.bar(['ZB', 'HBB'], [np.mean(correct_predictions[combined_labels == 'ZB']), np.mean(correct_predictions[combined_labels == 'HBB'])])
    plt.xlabel('Event Type')
    plt.ylabel('Accuracy')
    plt.title('Accuracy by Event Type')
    plt.savefig(os.path.join(save_path, f'accuracy_by_event_type_{model_name}.png'))
    plt.close()

# Load data
zb_cregionsl, zb_genPhi, zb_genEta, zb_cregions, genPtZB = load_data("data/dataZB.h5")
hbb_cregionsl, hbb_genPhi, hbb_genEta, hbb_cregions, genPt = load_data("data/data.h5")

hbb_labels = calculate_labels(hbb_cregions, hbb_genPhi, hbb_genEta)
cregions_comb, combined_cregions, combined_genPhi, combined_genEta, combined_labels = create_combined_dataset(zb_cregionsl, hbb_cregionsl, zb_cregions, hbb_cregions, zb_genPhi, hbb_genPhi, zb_genEta, hbb_genEta)

# Evaluate models
model_paths = ['modelApprentice_epochs100_batch32/model', 'modelMaster_epochs100_batch32/model']
model_names = ['apprentice', 'master']
save_path = 'evaluations/'

for model_path, model_name in zip(model_paths, model_names):
    evaluate_model(model_path, model_name, zb_cregions, hbb_cregions, hbb_labels, combined_cregions, combined_labels, save_path, genPt)
