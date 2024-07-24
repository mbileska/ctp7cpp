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
#define OUT_HEIGHT_8 6
#define OUT_WIDTH_8 4
#define N_FILT_8 4
#define N_SIZE_0_9 96
#define N_LAYER_10 16
#define N_LAYER_10 16
#define N_LAYER_16 2

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
typedef ap_fixed<16,6> layer10_t;
typedef ap_fixed<8,2> weight10_t;
typedef ap_fixed<8,2> bias10_t;
typedef ap_uint<1> layer10_index;
typedef ap_fixed<16,6> layer12_t;
typedef ap_fixed<18,8> relu_2_table_t;
typedef ap_fixed<16,6> result_t;
typedef ap_fixed<8,2> weight13_t;
typedef ap_fixed<8,2> bias13_t;
typedef ap_uint<1> layer13_index;

#endif
