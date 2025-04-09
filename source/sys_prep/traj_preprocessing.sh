#!/bin/bash 

# CHANGE THIS LINE to point to your own threadmpi/GMXRC file. threadmpi is more efficient for single-node communication than the mpi version.

cdygen_root=$(git rev-parse --show-toplevel)
cdygen_source=$cdygen_root/source/
export PYTHONPATH=$PYTHONPATH:$cdygen_source

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
                    -o ${traj_dir}/output_centered_fit.xtc <<< $'Protein\nProtein\nSystem'
    # wrap the trajectory
    # python -W ignore ${cdygen_source}/sys_prep/wrap_traj.py -i ${traj_dir}/centered_fit.xtc \
    #                                                         -o ${traj_dir}/structure.pdb


    # clean up
    rm -f ${traj_dir}/unwrapped.xtc \
          ${traj_dir}/centered.xtc \
        #   ${traj_dir}/centered_fit.xtc
done < "$INPUT_PATH"


# clean up
# rm -fr *.cpt *.gro \#* *.tpr

exit;
