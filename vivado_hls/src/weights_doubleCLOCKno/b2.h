//Numpy array shape [4]
//Min -0.500000000000
//Max 0.000000000000
//Number of zeros 2

#ifndef B2_H_
#define B2_H_

#ifndef __SYNTHESIS__
bias2_t b2[4];
#else
bias2_t b2[4] = {-0.25, 0.00, 0.00, -0.50};
#endif

#endif
