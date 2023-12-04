#include <iostream>

#include "cicada.h"
#include "parameters.h"

void cicada(
    input_t inputs_[N_INPUT_1_1],
    result_t layer8_out[N_LAYER_6]
) {

    // hls-fpga-machine-learning insert IO
    #pragma HLS INLINE 

#ifndef __SYNTHESIS__
    static bool loaded_weights = false;
    if (!loaded_weights) {
        // hls-fpga-machine-learning insert load weights
        nnet::load_weights_from_txt<weight2_t, 3780>(w2, "w2.txt");
        nnet::load_weights_from_txt<bias2_t, 15>(b2, "b2.txt");
        nnet::load_weights_from_txt<qbn1_scale_t, 15>(s4, "s4.txt");
        nnet::load_weights_from_txt<qbn1_bias_t, 15>(b4, "b4.txt");
        nnet::load_weights_from_txt<weight6_t, 15>(w6, "w6.txt");
        nnet::load_weights_from_txt<bias6_t, 1>(b6, "b6.txt");
        loaded_weights = true;
    }
#endif

    // ****************************************
    // NETWORK INSTANTIATION
    // ****************************************

    // hls-fpga-machine-learning insert layers

    layer2_t layer2_out[N_LAYER_2];
    #pragma HLS ARRAY_PARTITION variable=layer2_out complete dim=0
    nnet::dense<input_t, layer2_t, config2>(inputs_, layer2_out, w2, b2); // dense1

    layer4_t layer4_out[N_LAYER_2];
    #pragma HLS ARRAY_PARTITION variable=layer4_out complete dim=0
    nnet::normalize<layer2_t, layer4_t, config4>(layer2_out, layer4_out, s4, b4); // QBN1

    layer5_t layer5_out[N_LAYER_2];
    #pragma HLS ARRAY_PARTITION variable=layer5_out complete dim=0
    nnet::relu<layer4_t, layer5_t, relu_config5>(layer4_out, layer5_out); // relu1

    layer6_t layer6_out[N_LAYER_6];
    #pragma HLS ARRAY_PARTITION variable=layer6_out complete dim=0
    nnet::dense<layer5_t, layer6_t, config6>(layer5_out, layer6_out, w6, b6); // output

    nnet::relu<layer6_t, result_t, relu_config8>(layer6_out, layer8_out); // outputs

}
