//Numpy array shape [4]
//Min -0.015625000000
//Max 0.000000000000
//Number of zeros 3

#ifndef B2_H_
#define B2_H_

#ifndef __SYNTHESIS__
bias2_t b2[4];
#else
bias2_t b2[4] = {0.000000, 0.000000, -0.015625, 0.000000};
#endif

#endif
