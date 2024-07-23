#ifndef PARAMETERS_H_
#define PARAMETERS_H_

#include "ap_fixed.h"
#include "ap_int.h"

#include "nnet_utils/nnet_code_gen.h"
#include "nnet_utils/nnet_helpers.h"
// hls-fpga-machine-learning insert includes
#include "nnet_utils/nnet_activation.h"
#include "nnet_utils/nnet_activation_stream.h"
#include "nnet_utils/nnet_batchnorm.h"
#include "nnet_utils/nnet_batchnorm_stream.h"
#include "nnet_utils/nnet_conv2d.h"
#include "nnet_utils/nnet_conv2d_stream.h"
#include "nnet_utils/nnet_dense.h"
#include "nnet_utils/nnet_dense_compressed.h"
#include "nnet_utils/nnet_dense_stream.h"
#include "nnet_utils/nnet_padding.h"
#include "nnet_utils/nnet_padding_stream.h"
#include "nnet_utils/nnet_pooling.h"
#include "nnet_utils/nnet_pooling_stream.h"

// hls-fpga-machine-learning insert weights
#include "weights/w4.h"
#include "weights/b4.h"
#include "weights/s6.h"
#include "weights/b6.h"
#include "weights/w10.h"
#include "weights/b10.h"
#include "weights/w13.h"
#include "weights/b13.h"

// hls-fpga-machine-learning insert layer-config
// relu30_1
struct relu_config2 : nnet::activ_config {
    static const unsigned n_in = 252;
    static const unsigned table_size = 1024;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 2;
    typedef relu30_1_table_t table_t;
};

// zero_padding
struct config3 : nnet::padding2d_config {
    static const unsigned in_height = 18;
    static const unsigned in_width = 14;
    static const unsigned n_chan = 1;
    static const unsigned out_height = 20;
    static const unsigned out_width = 14;
    static const unsigned pad_top = 1;
    static const unsigned pad_bottom = 1;
    static const unsigned pad_left = 0;
    static const unsigned pad_right = 0;
};

// conv_1
struct config4_mult : nnet::dense_config {
    static const unsigned n_in = 25;
    static const unsigned n_out = 4;
    static const unsigned reuse_factor = 1;
    static const unsigned strategy = nnet::resource;
    static const unsigned n_zeros = 4;
    static const unsigned multiplier_limit = DIV_ROUNDUP(n_in * n_out, reuse_factor) - n_zeros / reuse_factor;
    typedef model_default_t accum_t;
    typedef bias4_t bias_t;
    typedef weight4_t weight_t;
    template<class x_T, class y_T>
    using product = nnet::product::mult<x_T, y_T>;
};

struct config4 : nnet::conv2d_config {
    static const unsigned pad_top = 2;
    static const unsigned pad_bottom = 2;
    static const unsigned pad_left = 2;
    static const unsigned pad_right = 2;
    static const unsigned in_height = 20;
    static const unsigned in_width = 14;
    static const unsigned n_chan = 1;
    static const unsigned filt_height = 5;
    static const unsigned filt_width = 5;
    static const unsigned kernel_size = filt_height * filt_width;
    static const unsigned n_filt = 4;
    static const unsigned stride_height = 1;
    static const unsigned stride_width = 1;
    static const unsigned out_height = 20;
    static const unsigned out_width = 14;
    static const unsigned reuse_factor = 1;
    static const unsigned n_zeros = 4;
    static const unsigned multiplier_limit =
        DIV_ROUNDUP(kernel_size * n_chan * n_filt, reuse_factor) - n_zeros / reuse_factor;
    static const bool store_weights_in_bram = false;
    static const unsigned strategy = nnet::resource;
    static const nnet::conv_implementation implementation = nnet::conv_implementation::linebuffer;
    static const unsigned min_height = 20;
    static const unsigned min_width = 14;
    static const ap_uint<filt_height * filt_width> pixels[min_height * min_width];
    static const unsigned n_partitions = 280;
    static const unsigned n_pixels = out_height * out_width / n_partitions;
    template<class data_T, class CONFIG_T>
    using fill_buffer = nnet::fill_buffer_2<data_T, CONFIG_T>;
    typedef model_default_t accum_t;
    typedef bias4_t bias_t;
    typedef weight4_t weight_t;
    typedef config4_mult mult_config;
    template<unsigned K, unsigned S, unsigned W>
    using scale_index_height = nnet::scale_index_unscaled<K, S, W>;
    template<unsigned K, unsigned S, unsigned W>
    using scale_index_width = nnet::scale_index_unscaled<K, S, W>;
};
const ap_uint<config4::filt_height * config4::filt_width> config4::pixels[] = {0};

// norm_1
struct config6 : nnet::batchnorm_config {
    static const unsigned n_in = OUT_HEIGHT_4*OUT_WIDTH_4*N_FILT_4;
    static const unsigned n_filt = 4;
    static const unsigned n_scale_bias = (n_filt == -1) ? n_in : n_filt;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 2;
    static const unsigned multiplier_limit = DIV_ROUNDUP(n_in, reuse_factor);
    static const bool store_weights_in_bram = false;
    typedef norm_1_bias_t bias_t;
    typedef norm_1_scale_t scale_t;
    template<class x_T, class y_T>
    using product = nnet::product::mult<x_T, y_T>;
};

// relu_1
struct relu_config7 : nnet::activ_config {
    static const unsigned n_in = 1120;
    static const unsigned table_size = 1024;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 2;
    typedef relu_1_table_t table_t;
};

// pool_1
struct config8 : nnet::pooling2d_config {
    static const unsigned in_height = 20;
    static const unsigned in_width = 14;
    static const unsigned n_filt = 4;
    static const unsigned stride_height = 3;
    static const unsigned stride_width = 3;
    static const unsigned pool_height = 3;
    static const unsigned pool_width = 3;

    static const unsigned filt_height = pool_height;
    static const unsigned filt_width = pool_width;
    static const unsigned n_chan = n_filt;

    static const unsigned out_height = 6;
    static const unsigned out_width = 4;
    static const unsigned pad_top = 0;
    static const unsigned pad_bottom = 0;
    static const unsigned pad_left = 0;
    static const unsigned pad_right = 0;
    static const bool count_pad = false;
    static const nnet::Pool_Op pool_op = nnet::Average;
    static const nnet::conv_implementation implementation = nnet::conv_implementation::linebuffer;
    static const unsigned reuse_factor = 2;
    typedef model_default_t accum_t;
};

// dense_1
struct config10 : nnet::dense_config {
    static const unsigned n_in = 96;
    static const unsigned n_out = 16;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 2;
    static const unsigned n_zeros = 64;
    static const unsigned n_nonzeros = 1472;
    static const unsigned multiplier_limit = DIV_ROUNDUP(n_in * n_out, reuse_factor) - n_zeros / reuse_factor;
    static const bool store_weights_in_bram = false;
    typedef model_default_t accum_t;
    typedef bias10_t bias_t;
    typedef weight10_t weight_t;
    typedef layer10_index index_t;
    template<class x_T, class y_T>
    using product = nnet::product::mult<x_T, y_T>;
};

// relu_2
struct relu_config12 : nnet::activ_config {
    static const unsigned n_in = 16;
    static const unsigned table_size = 1024;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned reuse_factor = 2;
    typedef relu_2_table_t table_t;
};

// dense_out
struct config13 : nnet::dense_config {
    static const unsigned n_in = 16;
    static const unsigned n_out = 2;
    static const unsigned io_type = nnet::io_parallel;
    static const unsigned strategy = nnet::latency;
    static const unsigned reuse_factor = 2;
    static const unsigned n_zeros = 1;
    static const unsigned n_nonzeros = 31;
    static const unsigned multiplier_limit = DIV_ROUNDUP(n_in * n_out, reuse_factor) - n_zeros / reuse_factor;
    static const bool store_weights_in_bram = false;
    typedef model_default_t accum_t;
    typedef bias13_t bias_t;
    typedef weight13_t weight_t;
    typedef layer13_index index_t;
    template<class x_T, class y_T>
    using product = nnet::product::mult<x_T, y_T>;
};


#endif
