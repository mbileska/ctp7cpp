#ifndef DEFINES_H_
#define DEFINES_H_

#include "ap_fixed.h"
#include "ap_int.h"
#include "nnet_utils/nnet_types.h"
#include <cstddef>
#include <cstdio>

// hls-fpga-machine-learning insert numbers
#define N_INPUT_1_1 252
#define N_LAYER_2 16
#define N_LAYER_2 16
#define N_LAYER_5 1
#define N_LAYER_5 1

// hls-fpga-machine-learning insert layer-precision
typedef ap_uint<10> input_t;
typedef ap_fixed<26,20> dense1_accum_t;
typedef ap_fixed<26,20> layer2_t;
typedef ap_fixed<8,2> weight2_t;
typedef ap_fixed<8,4> bias2_t;
typedef ap_uint<1> layer2_index;
typedef ap_ufixed<10,6,AP_RND_CONV,AP_SAT> layer4_t;
typedef ap_fixed<18,8> relu1_table_t;
typedef ap_fixed<26,14> dense2_accum_t;
typedef ap_fixed<26,14> layer5_t;
typedef ap_fixed<12,4> weight5_t;
typedef ap_uint<1> bias5_t;
typedef ap_uint<1> layer5_index;
typedef ap_ufixed<16,8,AP_RND_CONV,AP_SAT> result_t;
typedef ap_fixed<18,8> outputs_table_t;

#endif
