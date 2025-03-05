#!/bin/bash 

# -*- coding: utf-8 -*-
# Created on Mon Mar 3 2025
# @author: byunguk park

##########
# Inputs #
##########

PDB_DIR=$1
OUTPUT_DIR=$2
INPUT_PATH=$3
# PDB_CHAIN_ID=3DYT_A

##################
# Execute script #
##################

# Check if the directory exists
if [ ! -d "$OUTPUT_DIR" ]; then
    # If it doesn't exist, create it
    mkdir -p "$OUTPUT_DIR"
    echo "Directory '$OUTPUT_DIR' created."
fi

# Read input file line by line
while IFS= read -r PDB_ID; do
    # Update PDB_CHAIN_ID
    PDB_CHAIN_ID="${PDB_ID// /}"
    echo "Noncanonical Residues Processing: $PDB_CHAIN_ID"
    # update PDB file
    # non-canonical residues --> canonical residues

    ## 1. MSE
    sed 's/HETATM/ATOM  /g' $PDB_DIR/$PDB_CHAIN_ID.pdb > $OUTPUT_DIR/$PDB_CHAIN_ID.pdb
    sed -i 's/MSE/MET/g' $OUTPUT_DIR/$PDB_CHAIN_ID.pdb
    sed -i 's/SE   MET/ SD  MET/g' $OUTPUT_DIR/$PDB_CHAIN_ID.pdb
    sed -i 's/    SE/     S/g' $OUTPUT_DIR/$PDB_CHAIN_ID.pdb
    ## 2. ??? (add more if needed)

done < <(tr -d '\r' < $INPUT_PATH)


# clean up
# rm -fr *.cpt *.gro \#* *.tpr

exit;
