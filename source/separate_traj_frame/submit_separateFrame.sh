#!/bin/bash 

# -*- coding: utf-8 -*-
# Created on Mon Mar 3 2025
# @author: byunguk park

##########
# Inputs #
##########

# main script for frame separation
# take a list of pdb_chain_id as input and separate the frames
# e.g.) bash submit_separateFrame.sh input.txt


ROOT_DIR=/mnt/e/masif_docker/pmp/htmd/clustering/CLoNe_benchmark
# WORKING_DIR=${ROOT_DIR}/frames
# INPUT_PATH=/mnt/e/masif_docker/pmp/htmd/lists/pmp_low_auc.txt
INPUT_PATH=$1
# RAW_DIR=/mnt/e/masif_docker/pmp/data_preparation/01-benchmark_pdbs
# PDB_DIR=/mnt/e/masif_docker/pmp/data_preparation/01-benchmark_pdbs4htmd

##################
# Execute script #
##################

# system preparation
if [ ! -d "$ROOT_DIR/gen_frame.log" ]; then
    # If it doesn't exist, create it
    touch $ROOT_DIR/gen_frame.log
fi

python separateFrame.py $ROOT_DIR $INPUT_PATH >> $ROOT_DIR/gen_frame.log

# clean up
# rm -fr *.cpt *.gro \#* *.tpr

exit;
