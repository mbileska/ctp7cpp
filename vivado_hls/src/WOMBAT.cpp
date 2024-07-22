#include <iostream>

#include "WOMBAT.h"
#include "parameters.h"

void WOMBAT(
    input_t inputs[N_INPUT_1_1],
    result_t layer12_out[N_LAYER_16]
) {

    // hls-fpga-machine-learning insert IO
    // #pragma HLS ARRAY_RESHAPE variable=inputs complete dim=0
    // #pragma HLS ARRAY_PARTITION variable=layer12_out complete dim=0
    // #pragma HLS INTERFACE ap_vld port=inputs,layer12_out 
    // #pragma HLS DATAFLOW 
    #pragma HLS INLINE

#ifndef __SYNTHESIS__
    static bool loaded_weights = false;
    if (!loaded_weights) {
        // hls-fpga-machine-learning insert load weights
        nnet::load_weights_from_txt<weight3_t, 36>(w3, "w3.txt");
        nnet::load_weights_from_txt<bias3_t, 4>(b3, "b3.txt");
        nnet::load_weights_from_txt<norm_1_scale_t, 4>(s5, "s5.txt");
        nnet::load_weights_from_txt<norm_1_bias_t, 4>(b5, "b5.txt");
        nnet::load_weights_from_txt<weight9_t, 4032>(w9, "w9.txt");
        nnet::load_weights_from_txt<bias9_t, 16>(b9, "b9.txt");
        nnet::load_weights_from_txt<weight12_t, 32>(w12, "w12.txt");
        nnet::load_weights_from_txt<bias12_t, 2>(b12, "b12.txt");
        loaded_weights = true;
    }
#endif

    // ****************************************
    // NETWORK INSTANTIATION
    // ****************************************

    // hls-fpga-machine-learning insert layers

    layer2_t layer2_out[N_INPUT_1_1*N_INPUT_2_1*N_INPUT_3_1];
    #pragma HLS ARRAY_PARTITION variable=layer2_out complete dim=0
    nnet::relu<input_t, layer2_t, relu_config2>(inputs, layer2_out, 1); // relu30_1

    layer3_t layer3_out[OUT_HEIGHT_3*OUT_WIDTH_3*N_FILT_3];
    #pragma HLS ARRAY_PARTITION variable=layer3_out complete dim=0
    nnet::conv_2d_cl<layer2_t, layer3_t, config3>(layer2_out, layer3_out, w3, b3); // conv_1

    layer5_t layer5_out[OUT_HEIGHT_3*OUT_WIDTH_3*N_FILT_3];
    #pragma HLS ARRAY_PARTITION variable=layer5_out complete dim=0
    nnet::normalize<layer3_t, layer5_t, config5>(layer3_out, layer5_out, s5, b5); // norm_1

    layer6_t layer6_out[OUT_HEIGHT_3*OUT_WIDTH_3*N_FILT_3];
    #pragma HLS ARRAY_PARTITION variable=layer6_out complete dim=0
    nnet::relu<layer5_t, layer6_t, relu_config6>(layer5_out, layer6_out); // relu_1

    layer7_t layer7_out[OUT_HEIGHT_7*OUT_WIDTH_7*N_FILT_7];
    #pragma HLS ARRAY_PARTITION variable=layer7_out complete dim=0
    nnet::pooling2d_cl<layer6_t, layer7_t, config7>(layer6_out, layer7_out); // pool_1

    auto& layer8_out = layer7_out;
    layer9_t layer9_out[N_LAYER_9];
    #pragma HLS ARRAY_PARTITION variable=layer9_out complete dim=0
    nnet::dense<layer7_t, layer9_t, config9>(layer8_out, layer9_out, w9, b9); // dense_1

    layer11_t layer11_out[N_LAYER_9];
    #pragma HLS ARRAY_PARTITION variable=layer11_out complete dim=0
    nnet::relu<layer9_t, layer11_t, relu_config11>(layer9_out, layer11_out); // relu_2

    nnet::dense<layer11_t, result_t, config12>(layer11_out, layer12_out, w12, b12); // dense_out

}
