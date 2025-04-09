#!/bin/bash 

# -*- coding: utf-8 -*-
# Created on Mon Mar 3 2025
# @author: byunguk park

cdygen_root=$(git rev-parse --show-toplevel)
cdygen_source=$cdygen_root/source/
export PYTHONPATH=$PYTHONPATH:$cdygen_source

##########
# Inputs #
##########

WORKING_DIR=$1
INPUT_PATH=$2
PDB_RAW_DIR=$3
PDB_EDIT_DIR=$4
PRM_DIR=$5
equil_t=$6           # ns
prod_t=$7            # ns

###############
# MAIN SCRIPT #
###############

# 1. PDB editing: convert non-canonical residues of given PDB files to canonical residues (e.g., HETATM to ATOM, MSE to MET, SE to S) since free-ver HTMD does not support protonation of non-canonical residues during system preparation
bash $cdygen_source/pdb_preprocess/submit_pdb_edit.sh $PDB_RAW_DIR \
                                                      $PDB_EDIT_DIR \
                                                      $INPUT_PATH

# 2. HTMD system building & equilibration + production runs
python -W ignore $cdygen_source/sys_prep/htmd_buildSystem_simple_multiple_nowrap.py $WORKING_DIR \
                                                                                    $INPUT_PATH \
                                                                                    $PDB_EDIT_DIR \
                                                                                    $PRM_DIR \
                                                                                    $equil_t \
                                                                                    $prod_t

# 3. Trajectory preprocessing: wrapping, centering, PBC off, rational + tranlsational fitting
echo -e "======== Trajectory Preprocessing ========\n"
bash $cdygen_source/sys_prep/traj_preprocessing_general.sh $WORKING_DIR \
                                                           $INPUT_PATH

# clean up
# rm -fr *.cpt *.gro \#* *.tpr

exit;
