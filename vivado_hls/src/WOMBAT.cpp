#include <iostream>

#include "WOMBAT.h"
#include "parameters.h"

void WOMBAT(
    input_t input_2[N_INPUT_1_1],
    result_t layer16_out[N_LAYER_16]
) {

    // hls-fpga-machine-learning insert IO
    #pragma HLS INLINE
//    #pragma HLS INTERFACE ap_vld port=input_2 
	//    #pragma HLS ARRAY_RESHAPE variable=input_2 complete dim=0
    //#pragma HLS ARRAY_PARTITION variable=layer16_out complete dim=0


#ifndef __SYNTHESIS__
    static bool loaded_weights = false;
    if (!loaded_weights) {
        // hls-fpga-machine-learning insert load weights
        // nnet::load_weights_from_txt<weight2_t, 288>(w2, "w2.txt");
        // nnet::load_weights_from_txt<bias2_t, 32>(b2, "b2.txt");
        // nnet::load_weights_from_txt<norm_1_scale_t, 32>(s4, "s4.txt");
        // nnet::load_weights_from_txt<norm_1_bias_t, 32>(b4, "b4.txt");
        // nnet::load_weights_from_txt<weight7_t, 18432>(w7, "w7.txt");
        // nnet::load_weights_from_txt<bias7_t, 64>(b7, "b7.txt");
        // nnet::load_weights_from_txt<norm_2_scale_t, 64>(s9, "s9.txt");
        // nnet::load_weights_from_txt<norm_2_bias_t, 64>(b9, "b9.txt");
        // nnet::load_weights_from_txt<weight13_t, 98304>(w13, "w13.txt");
        // nnet::load_weights_from_txt<bias13_t, 128>(b13, "b13.txt");
        // nnet::load_weights_from_txt<weight16_t, 512>(w16, "w16.txt");
        // nnet::load_weights_from_txt<bias16_t, 4>(b16, "b16.txt");
        // loaded_weights = true;
        load_weights_from_txt<weight2_t, 36>(w2, "w2.txt");
        nnet::load_weights_from_txt<bias2_t, 4>(b2, "b2.txt");
        nnet::load_weights_from_txt<norm_1_scale_t, 4>(s4, "s4.txt");
        nnet::load_weights_from_txt<norm_1_bias_t, 4>(b4, "b4.txt");
        nnet::load_weights_from_txt<weight7_t, 2304>(w7, "w7.txt");
        nnet::load_weights_from_txt<bias7_t, 8>(b7, "b7.txt");
        nnet::load_weights_from_txt<norm_2_scale_t, 8>(s9, "s9.txt");
        nnet::load_weights_from_txt<norm_2_bias_t, 8>(b9, "b9.txt");
        nnet::load_weights_from_txt<weight13_t, 98304>(w13, "w13.txt");
        nnet::load_weights_from_txt<bias13_t, 128>(b13, "b13.txt");
        nnet::load_weights_from_txt<weight16_t, 512>(w16, "w16.txt");
        nnet::load_weights_from_txt<bias16_t, 4>(b16, "b16.txt");
        loaded_weights = true;
    }
#endif

    // ****************************************
    // NETWORK INSTANTIATION
    // ****************************************

    // hls-fpga-machine-learning insert layers

    auto& layer_in = input_2;
    layer2_t layer2_out[OUT_HEIGHT_2*OUT_WIDTH_2*N_FILT_2];
    #pragma HLS ARRAY_PARTITION variable=layer2_out complete dim=0
    nnet::conv_2d_cl<input_t, layer2_t, config2>(layer_in, layer2_out, w2, b2); // q_conv2d

    layer4_t layer4_out[OUT_HEIGHT_2*OUT_WIDTH_2*N_FILT_2];
    #pragma HLS ARRAY_PARTITION variable=layer4_out complete dim=0
    nnet::normalize<layer2_t, layer4_t, config4>(layer2_out, layer4_out, s4, b4); // batch_normalization

    layer5_t layer5_out[OUT_HEIGHT_2*OUT_WIDTH_2*N_FILT_2];
    #pragma HLS ARRAY_PARTITION variable=layer5_out complete dim=0
    nnet::relu<layer4_t, layer5_t, relu_config5>(layer4_out, layer5_out); // q_activation

    layer6_t layer6_out[OUT_HEIGHT_6*OUT_WIDTH_6*N_FILT_6];
    #pragma HLS ARRAY_PARTITION variable=layer6_out complete dim=0
    nnet::pooling2d_cl<layer5_t, layer6_t, config6>(layer5_out, layer6_out); // average_pooling2d

    // layer7_t layer7_out[OUT_HEIGHT_7*OUT_WIDTH_7*N_FILT_7];
    // #pragma HLS ARRAY_PARTITION variable=layer7_out complete dim=0
    // nnet::conv_2d_cl<layer6_t, layer7_t, config7>(layer6_out, layer7_out, w7, b7); // q_conv2d_1

    // layer9_t layer9_out[OUT_HEIGHT_7*OUT_WIDTH_7*N_FILT_7];
    // #pragma HLS ARRAY_PARTITION variable=layer9_out complete dim=0
    // nnet::normalize<layer7_t, layer9_t, config9>(layer7_out, layer9_out, s9, b9); // batch_normalization_1

    // layer10_t layer10_out[OUT_HEIGHT_7*OUT_WIDTH_7*N_FILT_7];
    // #pragma HLS ARRAY_PARTITION variable=layer10_out complete dim=0
    // nnet::relu<layer9_t, layer10_t, relu_config10>(layer9_out, layer10_out); // q_activation_1

    // layer11_t layer11_out[OUT_HEIGHT_11*OUT_WIDTH_11*N_FILT_11];
    // #pragma HLS ARRAY_PARTITION variable=layer11_out complete dim=0
    // nnet::pooling2d_cl<layer10_t, layer11_t, config11>(layer10_out, layer11_out); // average_pooling2d_1

    auto& layer12_out = layer6_out; //OG 11 OUT
    layer13_t layer13_out[N_LAYER_13];
    #pragma HLS ARRAY_PARTITION variable=layer13_out complete dim=0
    nnet::dense<layer11_t, layer13_t, config13>(layer12_out, layer13_out, w13, b13); // q_dense

    layer15_t layer15_out[N_LAYER_13];
    #pragma HLS ARRAY_PARTITION variable=layer15_out complete dim=0
    nnet::relu<layer13_t, layer15_t, relu_config15>(layer13_out, layer15_out); // q_activation_2

    nnet::dense<layer15_t, result_t, config16>(layer15_out, layer16_out, w16, b16); // q_dense_1

}
