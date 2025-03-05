#!/bin/bash 

# CHANGE THIS LINE to point to your own threadmpi/GMXRC file. threadmpi is more efficient for single-node communication than the mpi version.

#######################################
########## UPDATE PARAMETERS ##########
#######################################

WORKING_DIR=$1
INPUT_PATH=$2

# Check if the directory exists
if [ ! -d "$WORKING_DIR" ]; then
    # If it doesn't exist, create it
    mkdir -p "$WORKING_DIR"
    echo "Directory '$WORKING_DIR' created."
fi

# Read the txt file line by line
while IFS= read -r line; do
    PDB_CHAIN_ID=$(echo "$line" | tr -d '\r\n')
    traj_dir=${WORKING_DIR}/${PDB_CHAIN_ID}/prod
    # remove PBC condition, center the protein
    gmx_mpi trjconv -f ${traj_dir}/output_wrapped.xtc \
                    -s ${traj_dir}/structure.pdb \
                    -pbc mol -center \
                    -o ${traj_dir}/output_wrapped_centered.xtc <<< $'Protein\nSystem'
    # rotational + translational fitting & center the protein
    gmx_mpi trjconv -f ${traj_dir}/output_wrapped_centered.xtc \
                    -s ${traj_dir}/structure.pdb \
                    -fit rot+trans -center \
                    -o ${traj_dir}/output_wrapped_centered_fit.xtc <<< $'Protein\nProtein\nSystem'
done < "$INPUT_PATH"


# clean up
# rm -fr *.cpt *.gro \#* *.tpr

exit;
