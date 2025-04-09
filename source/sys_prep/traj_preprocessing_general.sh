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
    # unwrap the trajectory
    gmx trjconv -f ${traj_dir}/output.xtc \
                    -s ${traj_dir}/structure.pdb \
                    -o ${traj_dir}/unwrapped.xtc -pbc nojump <<< $'System'
    # center the protein
    gmx trjconv -f ${traj_dir}/unwrapped.xtc \
                    -s ${traj_dir}/structure.pdb \
                    -center -pbc mol -ur compact \
                    -o ${traj_dir}/centered.xtc <<< $'Protein\nSystem'
    # rotational + translational fitting & center the protein
    gmx trjconv -f ${traj_dir}/centered.xtc \
                    -s ${traj_dir}/structure.pdb \
                    -fit rot+trans -center \
                    -o ${traj_dir}/centered_fit.xtc <<< $'Protein\nProtein\nSystem'
    # wrap the trajectory
    # gmx trjconv -f ${traj_dir}/centered_fit.xtc \
    #                 -s ${traj_dir}/structure.pdb \
    #                 -pbc mol -ur compact \
    #                 -o ${traj_dir}/output_wrapped_centered.xtc <<< $'System'
    cp ${traj_dir}/centered_fit.xtc ${traj_dir}/output_wrapped_centered_fit.xtc

    # clean up
    rm -f ${traj_dir}/unwrapped.xtc \
          ${traj_dir}/centered.xtc \
          ${traj_dir}/centered_fit.xtc
done < "$INPUT_PATH"


# clean up
# rm -fr *.cpt *.gro \#* *.tpr

exit;
