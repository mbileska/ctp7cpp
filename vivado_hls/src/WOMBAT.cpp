#include <iostream>

#include "WOMBAT.h"
#include "parameters.h"

void WOMBAT(
    input_t inputs[N_INPUT_1_1],
    result_t layer17_out[N_LAYER_17]
) {

    // hls-fpga-machine-learning insert IO
    #pragma HLS INLINE

#ifndef __SYNTHESIS__
    static bool loaded_weights = false;
    if (!loaded_weights) {
        // hls-fpga-machine-learning insert load weights
        nnet::load_weights_from_txt<weight4_t, 100>(w4, "w4.txt");
        nnet::load_weights_from_txt<bias4_t, 4>(b4, "b4.txt");
        nnet::load_weights_from_txt<norm_1_scale_t, 4>(s6, "s6.txt");
        nnet::load_weights_from_txt<norm_1_bias_t, 4>(b6, "b6.txt");
        nnet::load_weights_from_txt<weight8_t, 800>(w8, "w8.txt");
        nnet::load_weights_from_txt<bias8_t, 8>(b8, "b8.txt");
        nnet::load_weights_from_txt<norm_2_scale_t, 8>(s10, "s10.txt");
        nnet::load_weights_from_txt<norm_2_bias_t, 8>(b10, "b10.txt");
        nnet::load_weights_from_txt<weight14_t, 3072>(w14, "w14.txt");
        nnet::load_weights_from_txt<bias14_t, 16>(b14, "b14.txt");
        nnet::load_weights_from_txt<weight17_t, 32>(w17, "w17.txt");
        nnet::load_weights_from_txt<bias17_t, 2>(b17, "b17.txt");
        loaded_weights = true;
    }
#endif

    // ****************************************
    // NETWORK INSTANTIATION
    // ****************************************

    // hls-fpga-machine-learning insert layers

    layer2_t layer2_out[N_INPUT_1_1];
    #pragma HLS ARRAY_PARTITION variable=layer2_out complete dim=0
    nnet::relu<input_t, layer2_t, relu_config2>(inputs, layer2_out); // relu30_1

    layer3_t layer3_out[OUT_HEIGHT_3*OUT_WIDTH_3*N_CHAN_3];
    #pragma HLS ARRAY_PARTITION variable=layer3_out complete dim=0
    nnet::zeropad2d_cl<layer2_t, layer3_t, config3>(layer2_out, layer3_out); // zero_padding

    layer4_t layer4_out[OUT_HEIGHT_4*OUT_WIDTH_4*N_FILT_4];
    #pragma HLS ARRAY_PARTITION variable=layer4_out complete dim=0
    nnet::conv_2d_cl<layer3_t, layer4_t, config4>(layer3_out, layer4_out, w4, b4); // conv_1

    layer6_t layer6_out[OUT_HEIGHT_4*OUT_WIDTH_4*N_FILT_4];
    #pragma HLS ARRAY_PARTITION variable=layer6_out complete dim=0
    nnet::normalize<layer4_t, layer6_t, config6>(layer4_out, layer6_out, s6, b6); // norm_1

    layer7_t layer7_out[OUT_HEIGHT_4*OUT_WIDTH_4*N_FILT_4];
    #pragma HLS ARRAY_PARTITION variable=layer7_out complete dim=0
    nnet::relu<layer6_t, layer7_t, relu_config7>(layer6_out, layer7_out); // relu_1

    layer8_t layer8_out[OUT_HEIGHT_8*OUT_WIDTH_8*N_FILT_8];
    #pragma HLS ARRAY_PARTITION variable=layer8_out complete dim=0
    nnet::conv_2d_cl<layer7_t, layer8_t, config8>(layer7_out, layer8_out, w8, b8); // conv_2

    layer10_t layer10_out[OUT_HEIGHT_8*OUT_WIDTH_8*N_FILT_8];
    #pragma HLS ARRAY_PARTITION variable=layer10_out complete dim=0
    nnet::normalize<layer8_t, layer10_t, config10>(layer8_out, layer10_out, s10, b10); // norm_2

    layer11_t layer11_out[OUT_HEIGHT_8*OUT_WIDTH_8*N_FILT_8];
    #pragma HLS ARRAY_PARTITION variable=layer11_out complete dim=0
    nnet::relu<layer10_t, layer11_t, relu_config11>(layer10_out, layer11_out); // relu_3

    layer12_t layer12_out[OUT_HEIGHT_12*OUT_WIDTH_12*N_FILT_12];
    #pragma HLS ARRAY_PARTITION variable=layer12_out complete dim=0
    nnet::pooling2d_cl<layer11_t, layer12_t, config12>(layer11_out, layer12_out); // pool_1

    auto& layer13_out = layer12_out;
    layer14_t layer14_out[N_LAYER_14];
    #pragma HLS ARRAY_PARTITION variable=layer14_out complete dim=0
    nnet::dense<layer12_t, layer14_t, config14>(layer13_out, layer14_out, w14, b14); // dense_1

    layer16_t layer16_out[N_LAYER_14];
    #pragma HLS ARRAY_PARTITION variable=layer16_out complete dim=0
    nnet::relu<layer14_t, layer16_t, relu_config16>(layer14_out, layer16_out); // relu_2

    nnet::dense<layer16_t, result_t, config17>(layer16_out, layer17_out, w17, b17); // dense_out

}
