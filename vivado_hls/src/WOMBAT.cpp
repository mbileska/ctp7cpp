#include <iostream>

#include "WOMBAT.h"
#include "parameters.h"

void WOMBAT(
    input_t inputs[N_INPUT_1_1],
    result_t layer11_out[N_LAYER_16]
) {

    // hls-fpga-machine-learning insert IO
    // #pragma HLS ARRAY_RESHAPE variable=inputs complete dim=0
    // #pragma HLS ARRAY_PARTITION variable=layer11_out complete dim=0
    // #pragma HLS INTERFACE ap_vld port=inputs,layer11_out 
    // #pragma HLS DATAFLOW 
    #pragma HLS INLINE

#ifndef __SYNTHESIS__
    static bool loaded_weights = false;
    if (!loaded_weights) {
        // hls-fpga-machine-learning insert load weights
        nnet::load_weights_from_txt<weight2_t, 36>(w2, "w2.txt");
        nnet::load_weights_from_txt<bias2_t, 4>(b2, "b2.txt");
        nnet::load_weights_from_txt<norm_1_scale_t, 4>(s4, "s4.txt");
        nnet::load_weights_from_txt<norm_1_bias_t, 4>(b4, "b4.txt");
        nnet::load_weights_from_txt<weight8_t, 4032>(w8, "w8.txt");
        nnet::load_weights_from_txt<bias8_t, 16>(b8, "b8.txt");
        nnet::load_weights_from_txt<weight11_t, 32>(w11, "w11.txt");
        nnet::load_weights_from_txt<bias11_t, 2>(b11, "b11.txt");
        loaded_weights = true;
    }
#endif

    // ****************************************
    // NETWORK INSTANTIATION
    // ****************************************

    // hls-fpga-machine-learning insert layers

    layer2_t layer2_out[OUT_HEIGHT_2*OUT_WIDTH_2*N_FILT_2];
    #pragma HLS ARRAY_PARTITION variable=layer2_out complete dim=0
    nnet::conv_2d_cl<input_t, layer2_t, config2>(inputs, layer2_out, w2, b2); // conv_1

    layer4_t layer4_out[OUT_HEIGHT_2*OUT_WIDTH_2*N_FILT_2];
    #pragma HLS ARRAY_PARTITION variable=layer4_out complete dim=0
    nnet::normalize<layer2_t, layer4_t, config4>(layer2_out, layer4_out, s4, b4); // norm_1

    layer5_t layer5_out[OUT_HEIGHT_2*OUT_WIDTH_2*N_FILT_2];
    #pragma HLS ARRAY_PARTITION variable=layer5_out complete dim=0
    nnet::relu<layer4_t, layer5_t, relu_config5>(layer4_out, layer5_out); // relu_1

    layer6_t layer6_out[OUT_HEIGHT_6*OUT_WIDTH_6*N_FILT_6];
    #pragma HLS ARRAY_PARTITION variable=layer6_out complete dim=0
    nnet::pooling2d_cl<layer5_t, layer6_t, config6>(layer5_out, layer6_out); // pool_1

    auto& layer7_out = layer6_out;
    layer8_t layer8_out[N_LAYER_8];
    #pragma HLS ARRAY_PARTITION variable=layer8_out complete dim=0
    nnet::dense<layer6_t, layer8_t, config8>(layer7_out, layer8_out, w8, b8); // dense_1

    layer10_t layer10_out[N_LAYER_8];
    #pragma HLS ARRAY_PARTITION variable=layer10_out complete dim=0
    nnet::relu<layer8_t, layer10_t, relu_config10>(layer8_out, layer10_out); // relu_2

    nnet::dense<layer10_t, result_t, config11>(layer10_out, layer11_out, w11, b11); // dense_out

}
