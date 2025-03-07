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
HTMD_DIR=data/01-benchmark_htmd
CLONE_RAW_DIR=data/02-benchmark_clone-tmp
CLONE_DIR=data/02-benchmark_cluster
equil_t=$3                            # ns
prod_t=$4                             # ns
pdc_dist=4                            # param for cluster distance cutoff, default 4

# function
function check_dir ()
{ 
    # If input_dir doesn't exist, create it
    input_dir="$1";
    if [ ! -d "$input_dir" ]; then
        mkdir -p "$input_dir"
        echo "Directory '$input_dir' created." > $input_dir/log.txt
    fi
}

###############
# MAIN SCRIPT #
###############

# Define the output files
TXT_DIR=${INPUT_PATH%.txt}
filtered_pdb_list=${TXT_DIR}_filtered.txt
outlier_pdb_list=${TXT_DIR}_unmodeledResid.txt


# 0. Filter out the pdb_chain_ids with unmodeled residues in the middle of the amino acid sequence
check_dir $HTMD_DIR
python -W ignore $cdygen_source/pdb_preprocess/filter_unmodeled_residues.py $PDB_RAW_DIR \
                                                                            $INPUT_PATH \
                                                                            $filtered_pdb_list \
                                                                            $outlier_pdb_list >> $HTMD_DIR/log.txt

# 1. Run HTMD to generate conformational ensemble of the given PDB files
bash $cdygen_source/submit_htmd_buildSystem.sh $HTMD_DIR \
                                               $filtered_pdb_list \
                                               $PDB_RAW_DIR \
                                               $PDB_EDIT_DIR \
                                               $PRM_DIR \
                                               $equil_t \
                                               $prod_t >> $HTMD_DIR/log.txt

# 2. Run CLoNe to cluster the conformational ensemble into representative conformers
check_dir $CLONE_RAW_DIR
bash $cdygen_source/submit_clone.sh $filtered_pdb_list \
                                    $HTMD_DIR \
                                    $CLONE_RAW_DIR \
                                    $pdc_dist >> $CLONE_RAW_DIR/log.txt

# check_dir $CLONE_DIR
# python -W ignore $cdygen_source/cluster.py $CLONE_RAW_DIR \
#                                            $CLONE_DIR >> $CLONE_DIR/log.txt

# clean up
# rm -fr *.cpt *.gro \#* *.tpr
rm -fr $PDB_EDIT_DIR
# rm -fr $CLONE_RAW_DIR

exit;
