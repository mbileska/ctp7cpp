#ifndef DEFINES_H_
#define DEFINES_H_

#include "ap_fixed.h"
#include "ap_int.h"
#include "nnet_utils/nnet_types.h"
#include <cstddef>
#include <cstdio>

// hls-fpga-machine-learning insert numbers
#define N_INPUT_1_1 252
#define OUT_HEIGHT_3 20
#define OUT_WIDTH_3 14
#define N_CHAN_3 1
#define OUT_HEIGHT_4 20
#define OUT_WIDTH_4 14
#define N_FILT_4 4
#define OUT_HEIGHT_4 20
#define OUT_WIDTH_4 14
#define N_FILT_4 4
#define OUT_HEIGHT_4 20
#define OUT_WIDTH_4 14
#define N_FILT_4 4
#define OUT_HEIGHT_8 20
#define OUT_WIDTH_8 14
#define N_FILT_8 8
#define OUT_HEIGHT_8 20
#define OUT_WIDTH_8 14
#define N_FILT_8 8
#define OUT_HEIGHT_8 20
#define OUT_WIDTH_8 14
#define N_FILT_8 8
#define OUT_HEIGHT_12 6
#define OUT_WIDTH_12 4
#define N_FILT_12 8
#define N_SIZE_0_13 192
#define N_LAYER_14 16
#define N_LAYER_14 16
#define N_LAYER_17 2

// hls-fpga-machine-learning insert layer-precision
typedef ap_uint<10> input_t;
typedef ap_fixed<16,6> layer2_t;
typedef ap_fixed<18,8> relu30_1_table_t;
typedef ap_fixed<16,6> layer3_t;
typedef ap_fixed<16,6> model_default_t;
typedef ap_fixed<16,6> layer4_t;
typedef ap_fixed<8,2> weight4_t;
typedef ap_fixed<8,2> bias4_t;
typedef ap_fixed<16,6> layer6_t;
typedef ap_fixed<16,6> norm_1_scale_t;
typedef ap_fixed<16,6> norm_1_bias_t;
typedef ap_fixed<16,6> layer7_t;
typedef ap_fixed<18,8> relu_1_table_t;
typedef ap_fixed<16,6> layer8_t;
typedef ap_fixed<8,2> weight8_t;
typedef ap_fixed<8,2> bias8_t;
typedef ap_fixed<16,6> layer10_t;
typedef ap_fixed<16,6> norm_2_scale_t;
typedef ap_fixed<16,6> norm_2_bias_t;
typedef ap_fixed<16,6> layer11_t;
typedef ap_fixed<18,8> relu_3_table_t;
typedef ap_fixed<16,6> layer12_t;
typedef ap_fixed<16,6> layer14_t;
typedef ap_fixed<8,2> weight14_t;
typedef ap_fixed<8,2> bias14_t;
typedef ap_uint<1> layer14_index;
typedef ap_fixed<16,6> layer16_t;
typedef ap_fixed<18,8> relu_2_table_t;
typedef ap_fixed<16,6> result_t;
typedef ap_fixed<8,2> weight17_t;
typedef ap_fixed<8,2> bias17_t;
typedef ap_uint<1> layer17_index;

#endif
