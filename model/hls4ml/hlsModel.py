import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import hls4ml
import numpy as np
import tensorflow as tf
from hls4ml.model.layers import Activation as ActivationHLS
from hls4ml.model.optimizer import OptimizerPass, register_pass
from tensorflow.keras import backend as K
from tensorflow.keras.utils import custom_object_scope
from tensorflow.keras.layers import Layer, Input
from tensorflow.keras.models import Model, load_model


class CircularPadding2D(Layer):
    def __init__(self, padding=(1, 1), **kwargs):
        self.padding = padding
        super(CircularPadding2D, self).__init__(**kwargs)

    def call(self, inputs):
        pad_width, pad_height = self.padding
        padded_inputs = tf.concat([inputs[:, -pad_width:], inputs, inputs[:, :pad_width]], axis=1)
        return padded_inputs

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[1] + 2 * self.padding[0], input_shape[2], input_shape[3])

def custom_mse_with_heavy_penalty(y_true, y_pred, threshold=1.0, penalty_factor=1.5):
    y_true = tf.cast(y_true, tf.float32)
    y_pred = tf.cast(y_pred, tf.float32)
    
    residual = y_true - y_pred
    
    small_residuals = K.square(residual)
    
    large_residuals = K.square(residual) * K.square(penalty_factor) * tf.cast(K.abs(residual) > threshold, tf.float32)
    
    combined_residuals = tf.where(K.abs(residual) < threshold, small_residuals, large_residuals)
    
    return K.mean(combined_residuals)

class EliminateLinearActivationCustom(OptimizerPass):
    def match(self, node):
        return (
            isinstance(node, ActivationHLS) and node.get_attr("activation") == "linear"
        )

    def transform(self, model, node):
        model.remove_node(node)
        return True

class Subtract30ReLU(Layer):
    def __init__(self, **kwargs):
        super(Subtract30ReLU, self).__init__(**kwargs)

    def call(self, inputs):
        return tf.nn.relu(inputs - 30.0)
    
    def get_config(self):
        return super().get_config()

def remove_custom_layer(keras_model, custom_layer_name):
    input_shape = keras_model.input_shape[1:]  
    inputs = Input(shape=input_shape)
    x = inputs
    for layer in keras_model.layers:
        if layer.name == custom_layer_name:
            continue
        x = layer(x)
    new_model = Model(inputs=inputs, outputs=x)
    return new_model

def get_hls_config(keras_model, strategy="Latency"):
    hls_config = hls4ml.utils.config_from_keras_model(keras_model, granularity="name")
    hls_config["Model"]["Strategy"] = strategy

    for layer in hls_config["LayerName"].keys():
        hls_config["LayerName"][layer]["ReuseFactor"] = 2

    input_layer_name = keras_model.layers[0].name
    hls_config["LayerName"][input_layer_name]["Precision"]["result"] = "ap_uint<10>"

    conv_layers = ["conv_1"]
    for layer in conv_layers:
        hls_config["LayerName"][layer]["Precision"]["weight"] = "ap_fixed<8,1>"
        hls_config["LayerName"][layer]["Precision"]["bias"] = "ap_fixed<8,1>"
        hls_config["LayerName"][layer]["Precision"]["result"] = "ap_fixed<16,6>"
        hls_config["LayerName"][layer]["Strategy"] = "Resource"  # Manually set to Resource

    dense_layers = ["dense_1", "dense_out"]
    for layer in dense_layers:
        hls_config["LayerName"][layer]["Precision"]["weight"] = "ap_fixed<8,1>"
        hls_config["LayerName"][layer]["Precision"]["bias"] = "ap_fixed<8,1>"
        hls_config["LayerName"][layer]["Precision"]["result"] = "ap_fixed<16,6>"

    activation_layers = ["relu_1", "relu_2"]
    for layer in activation_layers:
        hls_config["LayerName"][layer]["Precision"]["result"] = "ap_fixed<16,6>"

    return hls_config

def convert_to_hls4ml_model(keras_model, hls_config):
    hls_model = hls4ml.converters.convert_from_keras_model(
        keras_model,
        clock_period=6.25,
        backend="Vivado",
        hls_config=hls_config,
        io_type="io_parallel",
        output_dir="WOMBAT",
        part="xc7vx690tffg1927-2",
        project_name="WOMBAT",
        # version="1.0.0",
    )
    hls_model.compile()
    return hls_model

def main() -> None:
    # Workaround for linear activation layer removal
    hls4ml.model.flow.flow.update_flow(
        "optimize", remove_optimizers=["eliminate_linear_activation"]
    )
    register_pass(
        "overwrite_eliminate_linear_activation", EliminateLinearActivationCustom
    )
    hls4ml.model.flow.flow.update_flow(
        "convert", add_optimizers=["overwrite_eliminate_linear_activation"]
    )

    # Load pre-trained QKeras model with custom loss function in scope
    with custom_object_scope({'custom_mse_with_heavy_penalty': custom_mse_with_heavy_penalty, 'Subtract30ReLU': Subtract30ReLU, 'CircularPadding2D':CircularPadding2D}):
        keras_model = tf.keras.models.load_model("modelApprentice_epochs10_batch32/model", custom_objects={'custom_mse_with_heavy_penalty': custom_mse_with_heavy_penalty, 'Subtract30ReLU': Subtract30ReLU,'CircularPadding2D':CircularPadding2D})

    # Compile the Keras model with the custom loss function
    keras_model.compile(optimizer='adam', loss=custom_mse_with_heavy_penalty)

    # Remove custom layer before converting to HLS model
    keras_model_no_custom_layer = remove_custom_layer(keras_model, 'relu30_1')
    keras_model_no_custom_layer = remove_custom_layer(keras_model, 'padding_1')


    # Generate hls4ml config
    hls_config = get_hls_config(keras_model_no_custom_layer, strategy="Latency")

    # Generate hls4ml model
    hls_model = convert_to_hls4ml_model(keras_model_no_custom_layer, hls_config)

    hls_model.write()

    # Visualize the HLS model configuration
    hls4ml.utils.plot_model(hls_model, show_shapes=True, show_precision=True, to_file='model_hls4ml.png')

if __name__ == "__main__":
    main()
