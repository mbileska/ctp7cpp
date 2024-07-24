//Numpy array shape [5, 5, 4, 8]
//Min -0.328125000000
//Max 0.343750000000
//Number of zeros 32

#ifndef W8_H_
#define W8_H_

#ifndef __SYNTHESIS__
weight8_t w8[800];
#else
weight8_t w8[800] = {0.031250, 0.015625, -0.031250, 0.046875, -0.140625, -0.281250, -0.187500, -0.093750, -0.062500, 0.015625, -0.046875, 0.000000, -0.109375, -0.109375, -0.234375, 0.000000, 0.156250, 0.062500, 0.078125, 0.125000, -0.140625, 0.000000, 0.000000, 0.062500, 0.000000, 0.000000, -0.125000, -0.062500, -0.171875, 0.015625, -0.078125, -0.031250, -0.328125, 0.218750, 0.046875, -0.109375, -0.062500, -0.156250, 0.031250, -0.046875, -0.187500, 0.031250, -0.234375, -0.234375, 0.156250, 0.062500, 0.015625, 0.078125, 0.187500, 0.078125, -0.312500, 0.015625, -0.109375, 0.078125, -0.015625, 0.250000, 0.109375, -0.031250, -0.156250, 0.109375, 0.078125, 0.046875, -0.156250, 0.265625, 0.046875, 0.015625, -0.265625, -0.296875, 0.093750, 0.031250, 0.062500, -0.171875, -0.281250, -0.140625, 0.078125, 0.156250, -0.062500, 0.031250, -0.218750, 0.015625, -0.093750, 0.250000, -0.109375, -0.031250, -0.125000, 0.000000, 0.171875, -0.093750, -0.046875, 0.250000, -0.062500, 0.093750, 0.078125, 0.109375, 0.171875, -0.015625, -0.140625, -0.234375, 0.187500, 0.000000, -0.062500, -0.062500, 0.140625, 0.203125, 0.140625, 0.093750, -0.062500, 0.250000, 0.015625, 0.187500, -0.187500, -0.109375, -0.062500, -0.109375, -0.046875, -0.093750, 0.265625, 0.171875, -0.109375, -0.031250, -0.296875, -0.093750, 0.046875, 0.265625, 0.093750, -0.015625, -0.156250, -0.031250, -0.218750, -0.140625, 0.218750, -0.078125, -0.140625, -0.062500, -0.093750, 0.234375, 0.156250, 0.078125, 0.328125, 0.031250, 0.156250, -0.093750, 0.078125, -0.125000, -0.015625, -0.109375, -0.078125, -0.312500, 0.062500, 0.187500, -0.078125, 0.265625, -0.125000, -0.015625, 0.187500, -0.171875, -0.078125, -0.031250, -0.171875, -0.125000, 0.031250, 0.062500, -0.125000, 0.171875, -0.015625, 0.031250, 0.093750, 0.046875, 0.171875, 0.000000, -0.062500, 0.000000, -0.015625, 0.171875, -0.250000, -0.250000, 0.078125, -0.218750, 0.203125, 0.000000, 0.015625, 0.343750, -0.031250, 0.203125, 0.031250, -0.015625, -0.218750, -0.203125, 0.156250, 0.093750, -0.234375, -0.046875, -0.109375, -0.078125, 0.000000, -0.140625, 0.171875, -0.062500, 0.187500, 0.078125, -0.281250, 0.171875, 0.078125, -0.109375, -0.109375, 0.171875, -0.109375, -0.031250, -0.234375, 0.062500, 0.171875, -0.140625, 0.171875, 0.156250, 0.093750, 0.000000, 0.140625, -0.125000, -0.156250, 0.046875, -0.125000, -0.046875, 0.250000, 0.156250, -0.015625, 0.109375, -0.203125, 0.218750, -0.156250, -0.062500, 0.031250, 0.171875, -0.093750, 0.078125, 0.000000, 0.250000, -0.031250, -0.265625, 0.078125, 0.140625, -0.078125, 0.078125, -0.046875, -0.078125, 0.109375, -0.093750, 0.156250, -0.187500, -0.046875, 0.093750, 0.187500, 0.171875, -0.203125, 0.062500, 0.156250, 0.203125, -0.109375, 0.109375, -0.265625, 0.078125, -0.234375, 0.078125, -0.015625, 0.296875, -0.062500, -0.031250, 0.015625, 0.125000, -0.062500, 0.031250, -0.062500, 0.062500, 0.234375, -0.171875, 0.015625, -0.218750, -0.093750, 0.125000, -0.109375, -0.062500, 0.109375, 0.156250, 0.125000, -0.203125, -0.140625, -0.093750, 0.125000, -0.125000, 0.078125, 0.203125, 0.093750, 0.296875, -0.171875, 0.125000, -0.062500, -0.281250, -0.062500, 0.234375, 0.203125, 0.062500, 0.078125, -0.093750, -0.046875, -0.140625, -0.171875, 0.250000, -0.078125, -0.140625, -0.109375, 0.093750, 0.078125, -0.140625, 0.109375, 0.031250, 0.062500, 0.062500, 0.265625, -0.156250, 0.156250, -0.265625, 0.109375, -0.171875, 0.078125, 0.046875, 0.046875, -0.093750, 0.218750, -0.109375, -0.078125, 0.031250, 0.062500, -0.250000, -0.015625, -0.109375, 0.062500, 0.187500, 0.296875, 0.171875, -0.031250, 0.093750, 0.250000, 0.093750, -0.109375, 0.187500, 0.203125, -0.062500, -0.265625, 0.203125, -0.187500, -0.140625, 0.031250, -0.031250, 0.031250, 0.125000, -0.187500, 0.078125, -0.046875, -0.250000, 0.140625, -0.140625, 0.062500, 0.078125, -0.265625, 0.265625, -0.171875, 0.015625, 0.234375, -0.156250, 0.109375, 0.078125, -0.093750, 0.046875, 0.031250, -0.046875, -0.156250, -0.062500, 0.015625, -0.234375, -0.093750, -0.125000, -0.171875, -0.015625, 0.156250, -0.031250, 0.156250, 0.265625, -0.296875, 0.078125, -0.062500, 0.234375, 0.125000, -0.093750, -0.234375, 0.156250, -0.234375, -0.125000, -0.062500, -0.140625, 0.312500, 0.281250, 0.062500, -0.109375, -0.250000, -0.187500, 0.062500, 0.109375, -0.218750, 0.187500, 0.000000, -0.109375, -0.062500, 0.046875, 0.015625, 0.156250, 0.046875, 0.187500, -0.140625, 0.234375, -0.171875, -0.046875, 0.140625, 0.046875, 0.031250, 0.093750, 0.125000, -0.156250, 0.000000, 0.046875, -0.156250, 0.203125, 0.078125, -0.109375, 0.109375, 0.078125, -0.125000, -0.093750, -0.109375, 0.093750, 0.265625, 0.140625, -0.109375, 0.156250, 0.265625, -0.171875, 0.218750, -0.078125, 0.015625, -0.250000, -0.234375, -0.312500, 0.062500, -0.015625, -0.156250, -0.109375, -0.156250, -0.031250, 0.031250, -0.125000, 0.046875, -0.187500, -0.015625, 0.203125, -0.078125, 0.140625, 0.000000, -0.015625, -0.078125, 0.218750, -0.078125, 0.015625, 0.296875, 0.031250, -0.015625, 0.171875, 0.062500, 0.234375, 0.265625, 0.015625, -0.125000, 0.187500, 0.281250, -0.109375, 0.171875, 0.015625, 0.171875, -0.078125, 0.000000, 0.093750, -0.156250, 0.000000, 0.281250, -0.171875, -0.187500, -0.109375, 0.187500, 0.218750, 0.078125, -0.062500, 0.046875, 0.125000, 0.078125, 0.093750, -0.046875, -0.015625, -0.093750, 0.000000, 0.015625, 0.062500, -0.078125, 0.218750, 0.015625, 0.109375, 0.171875, 0.187500, -0.062500, 0.078125, -0.062500, 0.203125, 0.109375, 0.031250, 0.328125, -0.046875, -0.171875, -0.015625, -0.031250, 0.171875, 0.062500, 0.093750, 0.046875, 0.187500, 0.093750, 0.031250, 0.031250, -0.156250, -0.171875, -0.109375, -0.281250, 0.187500, -0.218750, 0.187500, 0.156250, 0.109375, 0.078125, -0.171875, 0.250000, -0.015625, 0.265625, -0.109375, 0.156250, 0.015625, -0.078125, -0.171875, 0.203125, -0.062500, -0.140625, -0.093750, 0.062500, -0.062500, 0.046875, -0.078125, -0.031250, 0.265625, -0.156250, 0.140625, 0.171875, -0.078125, -0.187500, -0.187500, -0.093750, 0.078125, -0.171875, -0.078125, 0.250000, -0.015625, 0.000000, -0.093750, -0.250000, -0.015625, 0.031250, -0.078125, -0.125000, -0.125000, -0.093750, 0.015625, 0.015625, -0.015625, 0.140625, 0.140625, -0.296875, -0.109375, 0.062500, -0.203125, 0.156250, -0.296875, 0.343750, -0.046875, 0.062500, -0.218750, 0.000000, -0.015625, -0.093750, -0.015625, 0.078125, 0.000000, -0.203125, 0.281250, -0.328125, -0.218750, 0.187500, -0.171875, 0.109375, 0.015625, -0.140625, 0.125000, -0.109375, -0.015625, -0.015625, -0.140625, -0.234375, 0.125000, -0.046875, 0.296875, 0.046875, 0.109375, -0.140625, 0.125000, -0.171875, 0.062500, 0.265625, 0.046875, 0.312500, -0.031250, -0.156250, 0.000000, 0.000000, 0.031250, 0.171875, 0.078125, 0.156250, 0.125000, -0.078125, 0.265625, 0.093750, -0.140625, 0.156250, 0.140625, 0.187500, 0.109375, -0.046875, 0.031250, 0.093750, -0.031250, -0.093750, -0.234375, -0.140625, 0.109375, 0.140625, 0.250000, 0.078125, -0.015625, 0.140625, -0.171875, 0.015625, -0.125000, -0.046875, 0.031250, -0.125000, -0.109375, 0.250000, -0.046875, 0.140625, -0.078125, -0.125000, 0.078125, 0.265625, 0.000000, 0.187500, -0.062500, -0.218750, 0.125000, 0.125000, 0.109375, 0.203125, -0.031250, 0.000000, 0.125000, 0.218750, 0.203125, 0.125000, -0.187500, 0.000000, 0.140625, 0.125000, 0.234375, 0.046875, -0.265625, 0.250000, -0.062500, 0.171875, -0.031250, -0.046875, 0.187500, -0.250000, 0.093750, -0.093750, 0.031250, 0.296875, -0.140625, -0.171875, 0.109375, 0.062500, -0.156250, -0.109375, -0.078125, -0.046875, 0.093750, 0.187500, 0.296875, -0.046875, 0.156250, -0.234375, -0.296875, 0.093750, -0.187500, 0.015625, -0.203125, -0.187500, 0.015625, -0.031250, 0.125000, -0.078125, -0.156250, 0.093750, -0.125000, -0.187500, 0.140625, 0.171875, 0.171875, 0.000000, 0.046875, -0.156250, -0.046875, 0.125000, -0.125000, 0.062500, 0.000000, 0.109375, -0.078125, -0.156250, 0.062500, 0.093750, -0.062500, -0.218750, 0.093750, -0.171875, 0.046875, -0.078125, 0.015625, 0.046875, -0.109375, -0.156250, -0.265625, -0.109375, -0.109375, 0.093750, -0.031250, 0.265625, 0.171875, -0.031250, -0.109375, 0.203125, 0.031250, -0.078125, -0.031250, 0.046875, -0.031250, 0.093750, -0.062500, -0.062500, -0.093750, 0.109375, 0.046875, 0.109375, -0.328125, 0.093750, 0.015625, 0.000000, 0.046875, 0.281250, 0.046875, -0.203125, -0.171875, -0.093750, 0.093750, -0.046875, 0.000000, -0.062500, -0.031250, -0.234375, -0.109375};
#endif

#endif
