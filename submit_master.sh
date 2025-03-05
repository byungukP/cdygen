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

INPUT_PATH=$1
PDB_RAW_DIR=$2
PDB_EDIT_DIR=data/01-benchmark_pdbs4htmd-tmp
PRM_DIR=$cdygen_source/forcefield/parameters
WORKING_DIR=data/01-benchmark_htmd
equil_t=$3           # ns
prod_t=$4            # ns

###############
# MAIN SCRIPT #
###############

# Define the output files
TXT_DIR=${INPUT_PATH%.txt}
filtered_pdb_list=${TXT_DIR}_filtered.txt
outlier_pdb_list=${TXT_DIR}_unmodeledResid.txt

# Check if the directory exists
if [ ! -d "$WORKING_DIR" ]; then
    # If it doesn't exist, create it
    mkdir -p "$WORKING_DIR"
    echo "Directory '$WORKING_DIR' created." > $WORKING_DIR/prep.log
fi

# 0. Filter out the pdb_chain_ids with unmodeled residues in the middle of the amino acid sequence
python -W ignore $cdygen_source/pdb_preprocess/filter_unmodeled_residues.py $PDB_RAW_DIR \
                                                                            $INPUT_PATH \
                                                                            $filtered_pdb_list \
                                                                            $outlier_pdb_list >> $WORKING_DIR/prep.log

# 1. Run HTMD to generate conformational ensemble of the given PDB files
bash $cdygen_source/submit_htmd_buildSystem.sh $WORKING_DIR \
                                               $filtered_pdb_list \
                                               $PDB_RAW_DIR \
                                               $PDB_EDIT_DIR \
                                               $PRM_DIR \
                                               $equil_t \
                                               $prod_t >> $WORKING_DIR/prep.log

# # 2. Run CLoNe to cluster the conformational ensemble into representative conformers
# bash $cdygen_source/submit_clone.sh /mnt/e/masif_docker/pmp/htmd/lists/pmp_low_auc.txt

# clean up
# rm -fr *.cpt *.gro \#* *.tpr
# rm -fr $PDB_EDIT_DIR

exit;
