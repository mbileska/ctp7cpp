#include <iostream>

#include "cicada.h"
#include "parameters.h"

void cicada(
    input_t inputs_[N_INPUT_1_1],
    result_t layer7_out[N_LAYER_5]
) {

    // hls-fpga-machine-learning insert IO
    #pragma HLS INLINE 

#ifndef __SYNTHESIS__
    static bool loaded_weights = false;
    if (!loaded_weights) {
        // hls-fpga-machine-learning insert load weights
        nnet::load_weights_from_txt<weight2_t, 4032>(w2, "w2.txt");
        nnet::load_weights_from_txt<bias2_t, 16>(b2, "b2.txt");
        nnet::load_weights_from_txt<weight5_t, 16>(w5, "w5.txt");
        nnet::load_weights_from_txt<bias5_t, 1>(b5, "b5.txt");
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
    nnet::relu<layer2_t, layer4_t, relu_config4>(layer2_out, layer4_out); // relu1

    layer5_t layer5_out[N_LAYER_5];
    #pragma HLS ARRAY_PARTITION variable=layer5_out complete dim=0
    nnet::dense<layer4_t, layer5_t, config5>(layer4_out, layer5_out, w5, b5); // dense2

    nnet::relu<layer5_t, result_t, relu_config7>(layer5_out, layer7_out); // outputs

}
