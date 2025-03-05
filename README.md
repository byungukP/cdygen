# CDyGen
Conformational Dynamics Generator. Run HTMD and CLoNe to generate multiple representative conformations from MD trajectories. The final release will contain functions for raw pdb file download from PDB, extraction of specific chain of interest from the complex, and protonation of residues.

## Quickstart
```sh
git clone -b main https://github.com/byungukP/CDyGen.git
cd cdygen
bash submit_master.sh ${INPUT_LIST_PATH} ${PDB_RAW_DIR} ${equil_t} ${prod_t}
```
- INPUT_LIST_PATH: path to the txt file of list of PDB_CHAIN_IDs
- PDB_RAW_DIR: path to the directory that contains pdb files with format of "{PDB}_{CHAIN}" for the format
- equilt_t: equilibration time in ns
- prod_t: production time in ns
- ex)
```sh
bash submit_master.sh data/lists/pmp_5cv_trainset_high_auc_100.txt data/01-benchmark_pdbs 1 10
```
