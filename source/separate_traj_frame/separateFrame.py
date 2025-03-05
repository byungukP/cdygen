# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 2024

@author: byunguk park
"""

import sys
import os
import shutil
import numpy as np
from htmd.ui import *
import subprocess

##########
# Inputs #
##########

WORKING_DIR = sys.argv[1]
input_file  = sys.argv[2]
# PARAM_PATH  = sys.argv[3]
# PDB_DIR     = sys.argv[4]

#############
# Functions #
#############

R"""
separateFrame.py
- input: traj.xtc
- output: separated frames.pdb
take a trajectory file of certain cluster and separate it into frames
separted frame.pdb files are saved in the same directory as the input file for further analysis

"""

def seperate_frame(PDB_DIR, OUTPUT_DIR):
    # Check cluster number
    cluster_num = len([f for f in os.listdir(PDB_DIR) if f.startswith("Center_")])
    print(f"Number of clusters: {cluster_num}")

    # Define output directory for frames
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i in np.arange(1, cluster_num+1):
        print(f"\nCluster {i}")
        os.makedirs(f'{OUTPUT_DIR}/Cluster_{i}', exist_ok=True)
        # Load the system and trajectory
        mol = Molecule(f'{PDB_DIR}/Center_{i}.pdb')  # Load your structure file (.pdb, .psf, etc.)
        mol.read(f'{PDB_DIR}/Cluster_{i}.xtc')  # Load the trajectory (.xtc)

        # Loop through each frame in the trajectory and save as .pdb
        for j in range(mol.numFrames):
            mol.frame = j  # Set the current frame
            output_path = os.path.join(f'{OUTPUT_DIR}/Cluster_{i}', f'frame_{j:04d}.pdb')  # Save with padded frame index
            mol.write(output_path)  # Write the frame to a pdb file
            print(f'Frame {j} saved to {output_path}')

##################
# Execute script #
##################

# Read PDB_ID list.txt
with open(f"{input_file}") as f:
    PDB_IDs = f.readlines()
    for PDB_ID in PDB_IDs:
        PDB_ID = PDB_ID.strip()
        PDB_DIR = f"{WORKING_DIR}/{PDB_ID}/cluster_results"
        OUTPUT_DIR = f"{WORKING_DIR}/{PDB_ID}/cluster_frames"
        seperate_frame(PDB_DIR, OUTPUT_DIR)


# with open(f"{input_file}") as f:
#     PDB_IDs = f.readlines()
#     for PDB_ID in PDB_IDs:
#         PDB_ID = PDB_ID.strip()
#         sys_prep(WORKING_DIR, PDB_DIR, PDB_ID)
#         sys_equil(WORKING_DIR, PARAM_PATH, PDB_ID)
#         sys_prod(WORKING_DIR, PARAM_PATH, PDB_ID)
#         post_process(WORKING_DIR, PDB_ID)



# =====================================================================================================
