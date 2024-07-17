//Numpy array shape [16]
//Min -0.109375000000
//Max 0.531250000000
//Number of zeros 0

#ifndef B8_H_
#define B8_H_

#ifndef __SYNTHESIS__
bias8_t b8[16];
#else
bias8_t b8[16] = {0.328125, 0.390625, 0.531250, 0.375000, 0.390625, 0.421875, -0.109375, 0.265625, 0.468750, 0.328125, 0.453125, 0.484375, 0.437500, 0.218750, 0.406250, 0.015625};
#endif

#endif
