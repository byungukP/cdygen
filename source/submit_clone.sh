#!/bin/bash 

# -*- coding: utf-8 -*-
# Created on Mon Mar 3 2025
# @author: byunguk park

# Master script for running CLoNe clustering with text file of PDB_CHAIN_IDs as input

cdygen_root=$(git rev-parse --show-toplevel)
cdygen_source=$cdygen_root/source/
cluster_source=$cdygen_source/clustering/
export PYTHONPATH=$PYTHONPATH:$cluster_source

##########
# Inputs #
##########

INPUT=$1                                                                 # Path to a list of pdb_chain_id or a single pdb_chain_id
HTMD_DIR=$2
OUTPUT_DIR=$3                                                            # Directory path to save results. Default is current directory
pdc_dist=$4                                                              # param for cluster distance cutoff, default 4
traj_type=_wrapped_centered_fit                                          # trajectory file type, default _wrapped_centered_fit.xtc

###############
# MAIN SCRIPT #
###############

# argument check
if [ -z "$INPUT" ]; then
    echo "Please provide a path to a list of pdb_chain_id or a single pdb_chain_id"
    exit;
fi
if [ -z "$OUTPUT_DIR" ]; then
    echo "Please provide a path to a output directory to save results"
    exit;
fi

# Run CLoNe
if [ -f "$INPUT" ]; then
   # INPUT is a path to a list of pdb_chain_id
   echo "PDB_CHAIN_ID list as an input"

   while IFS= read -r pdb_id; do
      pdb_id=$(echo "$pdb_id" | tr -d '\r' | tr -d '\n')
      echo "Processing: $pdb_id"
      echo 2 | python -W ignore ${cluster_source}/run_structural.py -id ${pdb_id} \
                                                                    -traj ${HTMD_DIR}/${pdb_id}/prod/output${traj_type}.xtc \
                                                                    -topo ${HTMD_DIR}/${pdb_id}/prod/structure.pdb \
                                                                    -pdc ${pdc_dist} \
                                                                    -at_sel "name CA" \
                                                                    -pca 2 \
                                                                    -o ${OUTPUT_DIR}
   done < $INPUT
else
   # INPUT is a single string word of pdb_chain_id
   echo "PDB_CHAIN_ID as an input"
   echo 2 | python -W ignore ${cluster_source}/run_structural.py -id ${INPUT} \
                                                                 -traj ${HTMD_DIR}/${INPUT}/prod/output${traj_type}.xtc \
                                                                 -topo ${HTMD_DIR}/${INPUT}/prod/structure.pdb \
                                                                 -pdc ${pdc_dist} \
                                                                 -at_sel "name CA" \
                                                                 -pca 2 \
                                                                 -o ${OUTPUT_DIR}
fi

# clean up
rm ${OUTPUT_DIR}/\#*
rm \#*
# rm -rf ${OUTPUT_DIR}

exit;
