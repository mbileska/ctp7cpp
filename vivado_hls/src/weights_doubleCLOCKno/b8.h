//Numpy array shape [16]
//Min 0.000000000000
//Max 0.250000000000
//Number of zeros 4

#ifndef B8_H_
#define B8_H_

#ifndef __SYNTHESIS__
bias8_t b8[16];
#else
bias8_t b8[16] = {0.00, 0.25, 0.25, 0.00, 0.25, 0.00, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.00, 0.25};
#endif

#endif
