#include <iostream>

#include "cicada.h"
#include "parameters.h"

void cicada(
    input_t inputs_[N_INPUT_1_1],
    result_t layer12_out[N_LAYER_10]
) {

    // hls-fpga-machine-learning insert IO
    #pragma HLS ARRAY_RESHAPE variable=inputs_ complete dim=0
    #pragma HLS ARRAY_PARTITION variable=layer12_out complete dim=0
    #pragma HLS INTERFACE ap_vld port=inputs_,layer12_out 
    #pragma HLS DATAFLOW 

#ifndef __SYNTHESIS__
    static bool loaded_weights = false;
    if (!loaded_weights) {
        // hls-fpga-machine-learning insert load weights
        nnet::load_weights_from_txt<weight3_t, 27>(w3, "w3.txt");
        nnet::load_weights_from_txt<bias3_t, 3>(b3, "b3.txt");
        nnet::load_weights_from_txt<weight7_t, 2880>(w7, "w7.txt");
        nnet::load_weights_from_txt<bias7_t, 20>(b7, "b7.txt");
        nnet::load_weights_from_txt<weight10_t, 20>(w10, "w10.txt");
        nnet::load_weights_from_txt<bias10_t, 1>(b10, "b10.txt");
        loaded_weights = true;
    }
#endif

    // ****************************************
    // NETWORK INSTANTIATION
    // ****************************************

    // hls-fpga-machine-learning insert layers

    auto& layer2_out = inputs_;
    layer3_t layer3_out[OUT_HEIGHT_3*OUT_WIDTH_3*N_FILT_3];
    #pragma HLS ARRAY_PARTITION variable=layer3_out complete dim=0
    nnet::conv_2d_cl<input_t, layer3_t, config3>(layer2_out, layer3_out, w3, b3); // conv

    layer5_t layer5_out[OUT_HEIGHT_3*OUT_WIDTH_3*N_FILT_3];
    #pragma HLS ARRAY_PARTITION variable=layer5_out complete dim=0
    nnet::relu<layer3_t, layer5_t, relu_config5>(layer3_out, layer5_out); // relu1

    auto& layer6_out = layer5_out;
    layer7_t layer7_out[N_LAYER_7];
    #pragma HLS ARRAY_PARTITION variable=layer7_out complete dim=0
    nnet::dense<layer5_t, layer7_t, config7>(layer6_out, layer7_out, w7, b7); // dense1

    layer9_t layer9_out[N_LAYER_7];
    #pragma HLS ARRAY_PARTITION variable=layer9_out complete dim=0
    nnet::relu<layer7_t, layer9_t, relu_config9>(layer7_out, layer9_out); // relu2

    layer10_t layer10_out[N_LAYER_10];
    #pragma HLS ARRAY_PARTITION variable=layer10_out complete dim=0
    nnet::dense<layer9_t, layer10_t, config10>(layer9_out, layer10_out, w10, b10); // output

    nnet::relu<layer10_t, result_t, relu_config12>(layer10_out, layer12_out); // outputs

}
