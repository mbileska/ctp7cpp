#include <iostream>

#include "WOMBAT.h"
#include "parameters.h"

void WOMBAT(
    input_t inputs[N_INPUT_1_1],
    result_t layer13_out[N_LAYER_16]
) {

    // hls-fpga-machine-learning insert IO
    #pragma HLS INLINE

#ifndef __SYNTHESIS__
    static bool loaded_weights = false;
    if (!loaded_weights) {
        // hls-fpga-machine-learning insert load weights
        nnet::load_weights_from_txt<weight4_t, 100>(w3, "w4.txt");
        nnet::load_weights_from_txt<bias4_t, 4>(b3, "b4.txt");
        nnet::load_weights_from_txt<norm_1_scale_t, 4>(s5, "s6.txt");
        nnet::load_weights_from_txt<norm_1_bias_t, 4>(b5, "b6.txt");
        nnet::load_weights_from_txt<weight10_t, 1536>(w9, "w10.txt");
        nnet::load_weights_from_txt<bias10_t, 16>(b9, "b10.txt");
        nnet::load_weights_from_txt<weight13_t, 32>(w12, "w13.txt");
        nnet::load_weights_from_txt<bias13_t, 2>(b12, "b13.txt");
        loaded_weights = true;
    }
#endif

    // ****************************************
    // NETWORK INSTANTIATION
    // ****************************************

    // hls-fpga-machine-learning insert layers

    layer2_t layer2_out[N_INPUT_1_1];
    #pragma HLS ARRAY_PARTITION variable=layer2_out complete dim=0
    nnet::relu<input_t, layer2_t, relu_config2>(inputs, layer2_out, 1); // relu30_1

    layer3_t layer3_out[OUT_HEIGHT_3*OUT_WIDTH_3*N_CHAN_3];
    #pragma HLS ARRAY_PARTITION variable=layer3_out complete dim=0
    nnet::zeropad2d_cl<layer2_t, layer3_t, config3>(layer2_out, layer3_out); // zero_padding

    layer4_t layer4_out[OUT_HEIGHT_4*OUT_WIDTH_4*N_FILT_4];
    #pragma HLS ARRAY_PARTITION variable=layer4_out complete dim=0
    nnet::conv_2d_cl<layer3_t, layer4_t, config4>(layer3_out, layer4_out, w3, b3); // conv_1

    layer6_t layer6_out[OUT_HEIGHT_4*OUT_WIDTH_4*N_FILT_4];
    #pragma HLS ARRAY_PARTITION variable=layer6_out complete dim=0
    nnet::normalize<layer4_t, layer6_t, config6>(layer4_out, layer6_out, s5, b5); // norm_1

    layer7_t layer7_out[OUT_HEIGHT_4*OUT_WIDTH_4*N_FILT_4];
    #pragma HLS ARRAY_PARTITION variable=layer7_out complete dim=0
    nnet::relu<layer6_t, layer7_t, relu_config7>(layer6_out, layer7_out); // relu_1

    layer8_t layer8_out[OUT_HEIGHT_8*OUT_WIDTH_8*N_FILT_8];
    #pragma HLS ARRAY_PARTITION variable=layer8_out complete dim=0
    nnet::pooling2d_cl<layer7_t, layer8_t, config8>(layer7_out, layer8_out); // pool_1

    auto& layer9_out = layer8_out;
    layer10_t layer10_out[N_LAYER_10];
    #pragma HLS ARRAY_PARTITION variable=layer10_out complete dim=0
    nnet::dense<layer8_t, layer10_t, config10>(layer9_out, layer10_out, w9, b9); // dense_1

    layer12_t layer12_out[N_LAYER_10];
    #pragma HLS ARRAY_PARTITION variable=layer12_out complete dim=0
    nnet::relu<layer10_t, layer12_t, relu_config12>(layer10_out, layer12_out); // relu_2

    nnet::dense<layer12_t, result_t, config13>(layer12_out, layer13_out, w12, b12); // dense_out

}
