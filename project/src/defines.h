#ifndef DEFINES_H_
#define DEFINES_H_

#include "ap_fixed.h"
#include "ap_int.h"
#include "nnet_utils/nnet_types.h"
#include <cstddef>
#include <cstdio>

// hls-fpga-machine-learning insert numbers
#define N_INPUT_1_1 252
#define N_LAYER_2 15
#define N_LAYER_2 15
#define N_LAYER_2 15
#define N_LAYER_6 1
#define N_LAYER_6 1

// hls-fpga-machine-learning insert layer-precision
typedef ap_ufixed<10,10> input_t;
typedef ap_fixed<15,14> dense1_accum_t;
typedef ap_fixed<14,13> layer2_t;
typedef ap_fixed<2,1> weight2_t;
typedef ap_uint<1> bias2_t;
typedef ap_uint<1> layer2_index;
typedef ap_fixed<13,7,AP_RND,AP_SAT,AP_SAT> layer4_t;
typedef ap_fixed<16,1> qbn1_scale_t;
typedef ap_fixed<10,2> qbn1_bias_t;
typedef ap_ufixed<5,2,AP_RND,AP_SAT,AP_SAT> layer5_t;
typedef ap_fixed<18,8> relu1_table_t;
typedef ap_fixed<22,16> output_accum_t;
typedef ap_fixed<16,8> layer6_t;
typedef ap_fixed<4,1> weight6_t;
typedef ap_uint<1> bias6_t;
typedef ap_uint<1> layer6_index;
typedef ap_ufixed<16,8,AP_RND,AP_SAT,AP_SAT> result_t;
typedef ap_fixed<18,8> outputs_table_t;

#endif
