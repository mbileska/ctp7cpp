# WOMBAT Project
---
![logo](assets/WOMBATlogoMini.png)

---
A wombat, of the family Vombatidae, known for its burrowing prowess, efficiently uncovers hidden structures beneath the surface. 

**Wide Object ML Boosted Algorithm Trigger** (WOMBAT) is designed to identify boosted jets using low-level calorimeter data from the Compact Muon Solenoid (CMS) experiment trigger system. This process employs a convolutional neural network to discern boosted jet substructures in proton-proton collisions at the Large Hadron Collider (LHC). WOMBAT integrates Quantization Aware Training to achieve sub-500 nanosecond inference latency on Field-Programmable Gate Arrays (FPGAs).

## Table of contents
  - [Contact Us](#Contact-Us)
- [Setup Environment](#Setup-Environment)
  - [Access to Datasets](#Access-to-Datasets)
  - [Converting ROOT to H5](#Converting-ROOT-to-H5)
- [Training](#Training)
- [Compilation](#Compilation)
- [CTP7cpp](#CTP7cpp)
---

### Contact Us

You could email us at [mbileska@cern.ch](mailto:cicada-project@cern.ch). 

---
## Setup Environment

We suggest using `conda` to setup the environment as follows:
```
conda create -n "wombat" python=3.9.16 numpy==1.26.0
conda activate wombat
python3 -m pip install -r misc/requirements.txt
```
---
**Additional Libraries for Quantization-Aware Training + HLS Conversion**: you will also need to install QKeras and hls4ml:
```
python3 -m pip install git+https://github.com/julesmuhizi/qkeras.git@qdense_batchnorm
python3 -m pip install git+https://github.com/AdrianAlan/hls4ml.git@cicada
```
---
## Datasets

### Access to Datasets
Data is currently not publically accesible. To request access email: [mbileska@cern.ch](mailto:mbileska@cern.ch) with the title *WOMBAT Data access request for [Your Name]*.

---
### Converting ROOT to H5
If you still wish to convert the `root` files to `h5` yourself, you can do it as follows:
```
python3 model/dataConversionUtils/convert.py 
```
Make sure to edit: 
```
    input_root_file = "l1TNtuple-ggHBB.root"  # Change with filename
    output_h5_file = "data.h5" # Change with output
```
with your root filename.

Other utilities include:
- displayHDFS.py: Displays contents of .h5 file
- displayRoot.py: Displays contents of .root file
- printH5.py: Prints the data from an .h5 file to output.txt


---
## Training
For training there are 3 models (in model/wombat-v1-*) summarized below:
- WOMBAT Master: Complex model with no quantization, highest performance and no significant limitations on resource usage, used for comparison, not implemented in FPGAs.
- WOMBAT Apprentice: Model intended to run on FPGAs under tight latency and resource usage constraints. In vivado_hls only the weights produced by this model are to be used since custom layers are applied.
- WOMBAT Apprentica Skeleton: The skeleton of the Apprentice model, excluding custom layers. Used for generating the WOMBAT.cpp, WOMBAT.h, parameters.h, and definitions.h files for FPGA implementation. Weights are not to be used from this model.


---
## Compilation and CTP7cpp
The main compilation files are already present in ctp7cpp/vivado_hls. To train a new model use the WOMBAT Apprentice code and move the weights folder generated by hlsModel.py in vivado_hls/src/, replacing the pre-existing one. A modification of WOMBAT Skeleton will require following a range of steps to integrate, which is not recommended. 

---
