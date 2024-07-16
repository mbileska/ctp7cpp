#ifndef DEFINES_H_
#define DEFINES_H_

#include "ap_fixed.h"
#include "ap_int.h"
#include "nnet_utils/nnet_types.h"
#include <cstddef>
#include <cstdio>

// hls-fpga-machine-learning insert numbers
#define N_INPUT_1_1 252
#include <cstdio>

// hls-fpga-machine-learning insert numbers
// #define N_INPUT_1_1 18
// #define N_INPUT_2_1 14
// #define N_INPUT_3_1 1
#define OUT_HEIGHT_2 18
#define OUT_WIDTH_2 14
#define N_FILT_2 32
#define OUT_HEIGHT_2 18
#define OUT_WIDTH_2 14
#define N_FILT_2 32
#define OUT_HEIGHT_2 18
#define OUT_WIDTH_2 14
#define N_FILT_2 32
#define OUT_HEIGHT_6 9
#define OUT_WIDTH_6 7
#define N_FILT_6 32
#define OUT_HEIGHT_7 9
#define OUT_WIDTH_7 7
#define N_FILT_7 64
#define OUT_HEIGHT_7 9
#define OUT_WIDTH_7 7
#define N_FILT_7 64
#define OUT_HEIGHT_7 9
#define OUT_WIDTH_7 7
#define N_FILT_7 64
#define OUT_HEIGHT_11 4
#define OUT_WIDTH_11 3
#define N_FILT_11 64
#define N_SIZE_0_12 768
#define N_LAYER_13 128
#define N_LAYER_13 128
#define N_LAYER_16 4

// hls-fpga-machine-learning insert layer-precision
typedef ap_uint<10> input_t;
typedef ap_fixed<16,6> model_default_t;
typedef ap_fixed<16,6> layer2_t;
typedef ap_fixed<8,2> weight2_t;
typedef ap_fixed<8,2> bias2_t;
typedef ap_fixed<16,6> layer4_t;
typedef ap_fixed<16,6> norm_1_scale_t;
typedef ap_fixed<16,6> norm_1_bias_t;
typedef ap_fixed<16,6> layer5_t;
typedef ap_fixed<18,8> relu_1_table_t;
typedef ap_fixed<16,6> layer6_t;
typedef ap_fixed<16,6> layer7_t;
typedef ap_fixed<8,2> weight7_t;
typedef ap_fixed<8,2> bias7_t;
typedef ap_fixed<16,6> layer9_t;
typedef ap_fixed<16,6> norm_2_scale_t;
typedef ap_fixed<16,6> norm_2_bias_t;
typedef ap_fixed<16,6> layer10_t;
typedef ap_fixed<18,8> relu_2_table_t;
typedef ap_fixed<16,6> layer11_t;
typedef ap_fixed<16,6> layer13_t;
typedef ap_fixed<8,2> weight13_t;
typedef ap_fixed<8,2> bias13_t;
typedef ap_uint<1> layer13_index;
typedef ap_fixed<16,6> layer15_t;
typedef ap_fixed<18,8> relu_3_table_t;
typedef ap_fixed<16,6> result_t;
typedef ap_fixed<8,2> weight16_t;
typedef ap_fixed<8,2> bias16_t;
typedef ap_uint<1> layer16_index;

#endif
