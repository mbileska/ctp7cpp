//Numpy array shape [4]
//Min -0.015625000000
//Max 0.062500000000
//Number of zeros 0

#ifndef B8_H_
#define B8_H_

#ifndef __SYNTHESIS__
bias8_t b8[4];
#else
bias8_t b8[4] = {0.062500, -0.015625, 0.062500, 0.062500};
#endif

#endif
