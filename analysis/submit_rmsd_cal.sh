#!/bin/bash 

# ByungUk Park UW-Madison, 2024


# CHANGE THIS LINE to point to your own threadmpi/GMXRC file. threadmpi is more efficient for single-node communication than the mpi version.

#######################################
########## UPDATE PARAMETERS ##########
#######################################

HTMD_DIR=/mnt/e/masif_docker/pmp/htmd/output_files/traj_fit_test
INPUT=/mnt/e/masif_docker/pmp/htmd/lists/whole_list.txt
# INPUT=$1

#######################################
###### ACTUAL RUN COMMAND LINES #######
#######################################

# # Check if the directory exists
# if [ ! -d "$OUTPUT_DIR" ]; then
#     # If it doesn't exist, create it
#     mkdir -p "$OUTPUT_DIR"
#     echo "Directory '$OUTPUT_DIR' created."
# fi

if [ -f "$INPUT" ]; then
   # INPUT is a path to a list of pdb_chain_id
   echo "PDB_CHAIN_ID list as an input"

   while IFS= read -r pdb_id; do
      pdb_id=$(echo "$pdb_id" | tr -d '\r' | tr -d '\n')
      echo "Processing: $pdb_id"
      mkdir ${HTMD_DIR}/${pdb_id}/prod/rmsd_check
      gmx_mpi rms -s ${HTMD_DIR}/${pdb_id}/prod/structure.pdb \
                  -f ${HTMD_DIR}/${pdb_id}/prod/output_wrapped_centered_fit.xtc \
                  -fit rot+trans \
                  -o ${HTMD_DIR}/${pdb_id}/prod/rmsd_check/rmsd.xvg \
                  <<< $'Protein\nProtein'
   done < $INPUT

else
   # INPUT is a single string word of pdb_chain_id
   echo "PDB_CHAIN_ID as an input"
   mkdir ${HTMD_DIR}/${pdb_id}/prod/rmsd_check
   gmx_mpi rms -s ${HTMD_DIR}/${pdb_id}/prod/structure.pdb \
               -f ${HTMD_DIR}/${pdb_id}/prod/output_wrapped_centered_fit.xtc \
               -fit rot+trans \
               -o ${HTMD_DIR}/${pdb_id}/prod/rmsd_check/rmsd.xvg \
               <<< $'Protein\nProtein'
fi


## cleaning
# rm ${OUTPUT_DIR}/\#*
# rm \#*

exit;
