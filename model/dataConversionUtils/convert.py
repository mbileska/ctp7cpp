
import argparse
import awkward as ak
import h5py
import numpy as np
import uproot
import os
import vector

from pathlib import Path
from typing import List, Optional
from utils import IsReadableDir, IsValidFile

eta_low_bound = [-2.5 , -2.172 , -1.392 , -1.044, -0.696, -0.348, 0.001, 0.348, 0.696, 1.044, 1.392 , 1.74, 2.172, 2.5]


central_phi = [ 0.000 , #0th region
			    0.349, #1st region
				0.698, #2nd region

				1.047, #/.... 
				1.396,
				1.744,
				2.093,
				2.442,
				2.791,
				-3.14159,
				-2.791,
				-2.442,
				-2.093,
				-1.744,
				-1.396,
				-1.047,
				-0.698,
				-0.349]

central_phi = np.array(central_phi)

def eta_to_Rct(eta: float ):
    ieta =-1 
    n = 0
    while (eta > eta_low_bound[n]): 
        ieta = ieta + 1 
        n = n + 1 
        if n == len(eta_low_bound):
            return -1
    return ieta

   # [-2.5 , -2.172 , -1.392 , -1.044, -0.696, -0.348, 0.001, 0.348, 0.696, 1.044, 1.392 , 1.74, 2.172, 2.5]  These are the lower bounds 


def phi_to_Rct(phi: float):  

    
    mask =  abs(phi - central_phi) < 0.174
    # print(mask)
    for index , ele in enumerate(mask): 
        if ele == True: return index
    return -1 #if no index is chosen then the phi corresponds to the upper half of region 9 

def extract_data_from_root(input_root_file, output_h5_file, tree_name, branches):
    with uproot.open(input_root_file) as file:
        tree = file[tree_name]

        data = {}
        for branch in branches:
            data[branch] = tree[branch].array()

        # Filter events where genId == 25 and genEta_1 and genPhi_1 >= 0
        # mask = (data["genId"] == 25) & (data["genPhi_1"] >= 0) & (data["genEta_1"] >= 0)
        for branch in branches:
            data[branch] = data[branch]

        if "cregions" in data:
            cregions_data = data["cregions"].to_numpy()
            data["cregions"] = cregions_data.reshape(-1, 18, 14)

        if "genId" in data:
            truthArray = data["genId"].to_numpy()
            for n in range(len(truthArray)):
                truthArray[n] = truthArray[n] == 25
            data["genId"] = truthArray

        if "genEta_1" in data:
            array = data["genEta_1"].to_numpy()
            for n in range(len(array)):
                array[n] = eta_to_Rct(array[n])
            data["genEta_1"] = array

        if "genPhi_1" in data:
            array = data["genPhi_1"].to_numpy()
            for n in range(len(array)):
                array[n] = phi_to_Rct(array[n])
            data["genPhi_1"] = array

        # Open an HDF5 file and write the data
        with h5py.File(output_h5_file, "w") as h5_file:
            for branch, array in data.items():
                h5_file.create_dataset(branch, data=array)


if __name__ == "__main__":
    
    input_root_file = "l1TNtuple-ggHBB.root"  # Change with filename
    output_h5_file = "data.h5" # Change with output
    tree_name = "l1NtupleProducer/efficiencyTree;1"
    
    
    branches = ["genId", "genEta_1", "genPhi_1", "cregions"]

    
    extract_data_from_root(input_root_file, output_h5_file, tree_name, branches)
