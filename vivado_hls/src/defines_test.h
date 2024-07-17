#ifndef DEFINES_H_
#define DEFINES_H_

#include "ap_fixed.h"
#include "ap_int.h"
#include "nnet_utils/nnet_types.h"
#include <cstddef>
#include <cstdio>

// hls-fpga-machine-learning insert numbers
// #define N_INPUT_1_1 18
// #define N_INPUT_2_1 14
// #define N_INPUT_3_1 1
#define N_INPUT_1_1 252

#define OUT_HEIGHT_2 18
#define OUT_WIDTH_2 14
#define N_FILT_2 4
#define OUT_HEIGHT_2 18
#define OUT_WIDTH_2 14
#define N_FILT_2 4
#define OUT_HEIGHT_2 18
#define OUT_WIDTH_2 14
#define N_FILT_2 4
#define OUT_HEIGHT_6 9
#define OUT_WIDTH_6 7
#define N_FILT_6 4
#define N_SIZE_0_7 252
#define N_LAYER_8 4
#define N_LAYER_8 4
#define N_LAYER_16 4

// hls-fpga-machine-learning insert layer-precision
typedef ap_uint<10> input_t;
typedef ap_fixed<16,6> model_default_t;
typedef ap_fixed<16,6> layer2_t;
typedef ap_fixed<8,2> weight2_t;
typedef ap_fixed<8,2> bias2_t;
typedef ap_fixed<16,6> layer4_t;
typedef ap_fixed<16,6> norm_2_scale_t;
typedef ap_fixed<16,6> norm_2_bias_t;
typedef ap_fixed<16,6> layer5_t;
typedef ap_fixed<18,8> relu_2_table_t;
typedef ap_fixed<16,6> layer6_t;
typedef ap_fixed<16,6> layer8_t;
typedef ap_fixed<8,2> weight8_t;
typedef ap_fixed<8,2> bias8_t;
typedef ap_uint<1> layer8_index;
typedef ap_fixed<16,6> layer10_t;
typedef ap_fixed<18,8> relu_3_table_t;
typedef ap_fixed<16,6> result_t;
typedef ap_fixed<8,2> weight11_t;
typedef ap_fixed<8,2> bias11_t;
typedef ap_uint<1> layer11_index;

#endif
