# -*- coding: utf-8 -*-
"""
Created on Mon Mar 3 2025

@author: byunguk park
"""

import sys
import os
from Bio import PDB
from Bio.PDB.PDBList import PDBList


##########
# Inputs #
##########

PDB_DIR             = sys.argv[1]
input_file          = sys.argv[2]
filtered_pdb_list   = sys.argv[3]
outlier_pdb_list    = sys.argv[4]

#############
# Functions #
#############

def get_pdb_files(pdb_ids, pdb_dir="pdb_files"):
    """Download PDB files given a list of PDB IDs."""
    os.makedirs(pdb_dir, exist_ok=True)
    pdbl = PDBList()
    
    for pdb_id in pdb_ids:
        pdb_file = os.path.join(pdb_dir, f"{pdb_id}.pdb")
        if not os.path.exists(pdb_file):
            pdbl.retrieve_pdb_file(pdb_id, pdir=pdb_dir, file_format="pdb")

def has_unmodeled_residues(pdb_file):
    """Check if a PDB file contains unmodeled residues in the middle of the sequence."""
    parser = PDB.PDBParser(QUIET=True)
    structure = parser.get_structure("PDB", pdb_file)

    for model in structure:
        for chain in model:
            residues = [res for res in chain if PDB.is_aa(res, standard=True)]
            if len(residues) < 2:
                continue  # Skip chains with less than 2 residues
            
            # Check for gaps in residue numbering
            prev_res = residues[0]
            for res in residues[1:]:
                prev_id, current_id = prev_res.id[1], res.id[1]
                if current_id - prev_id > 1:  # Gap detected
                    return True
                prev_res = res

    return False

def filter_pdb_ids(pdb_dir, input_file, output_file, outlier_file):
    """Read a list of PDB IDs, filter out those with unmodeled residues in the middle."""
    with open(input_file, "r") as f:
        pdb_ids = [line.strip() for line in f if line.strip()]

    filtered_pdb_ids = []
    outlier_pdb_ids = []
    for pdb_id in pdb_ids:
        pdb_file = os.path.join(pdb_dir, f"{pdb_id}.pdb")
        try:
            os.path.exists(pdb_file)
        except:
            print(f"Error: {pdb_id} not found")
            continue
        # Filter out PDBs with unmodeled residues in the middle
        if not has_unmodeled_residues(pdb_file):
            filtered_pdb_ids.append(pdb_id)
        else:
            outlier_pdb_ids.append(pdb_id)
    with open(output_file, "w") as f:
        for pdb_id in filtered_pdb_ids:
            f.write(f"{pdb_id}\n")
    with open(outlier_file, "w") as f:
        for pdb_id in outlier_pdb_ids:
            f.write(f"{pdb_id}\n")
    
    print(f"Filtered PDB IDs saved to {output_file}")
    print(f"Outlier PDB IDs saved to {outlier_file}")

##################
# Execute script #
##################

if __name__ == "__main__":
    filter_pdb_ids(PDB_DIR, input_file, filtered_pdb_list, outlier_pdb_list)
