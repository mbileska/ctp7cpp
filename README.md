# CTP7cpp
Source for generating CTP7 IP containing CICADA (anomaly detection) and WOMBAT (boosted jets identification).

### Running
To execute
```
cd projects
vitis_hls -f run_hls.tcl "reset=1 synth=1 csim=1 cosim=1 validation=0 export=1 vsynth=0"
```
Make sure, `vitis_hls` is sourced. On `cmstrigger01.hep.wisc.edu` you can run `source /opt/Xilinx/Vivado/2021.1/settings64.sh`.

### Test vectors
For making realistic test vectors from any EDM files, use: https://github.com/pallabidas/L1TRegionDumper to create an input root file.

Run the maketv.C inside scripts as usual with root.
