#ifndef DEFINES_H_
#define DEFINES_H_

#include "ap_fixed.h"
#include "ap_int.h"
#include "nnet_utils/nnet_types.h"
#include <cstddef>
#include <cstdio>

// hls-fpga-machine-learning insert numbers
#define N_INPUT_1_1 252


#define OUT_HEIGHT_3 18
#define OUT_WIDTH_3 14
#define N_FILT_3 4
#define OUT_HEIGHT_3 18
#define OUT_WIDTH_3 14
#define N_FILT_3 4
#define OUT_HEIGHT_3 18
#define OUT_WIDTH_3 14
#define N_FILT_3 4
#define OUT_HEIGHT_7 9
#define OUT_WIDTH_7 7
#define N_FILT_7 4
#define N_SIZE_0_8 252
#define N_LAYER_9 16
#define N_LAYER_9 16
#define N_LAYER_16 2

// hls-fpga-machine-learning insert layer-precision
typedef ap_uint<10> input_t;
typedef ap_fixed<16,6> layer2_t;
typedef ap_fixed<18,8> relu30_1_table_t;
typedef ap_fixed<16,6> model_default_t;
typedef ap_fixed<16,6> layer3_t;
typedef ap_fixed<8,2> weight3_t;
typedef ap_fixed<8,2> bias3_t;
typedef ap_fixed<16,6> layer5_t;
typedef ap_fixed<16,6> norm_1_scale_t;
typedef ap_fixed<16,6> norm_1_bias_t;
typedef ap_fixed<16,6> layer6_t;
typedef ap_fixed<18,8> relu_1_table_t;
typedef ap_fixed<16,6> layer7_t;
typedef ap_fixed<16,6> layer9_t;
typedef ap_fixed<8,2> weight9_t;
typedef ap_fixed<8,2> bias9_t;
typedef ap_uint<1> layer9_index;
typedef ap_fixed<16,6> layer11_t;
typedef ap_fixed<18,8> relu_2_table_t;
typedef ap_fixed<16,6> result_t;
typedef ap_fixed<8,2> weight12_t;
typedef ap_fixed<8,2> bias12_t;
typedef ap_uint<1> layer12_index;

#endif
