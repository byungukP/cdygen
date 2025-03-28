# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 2024
Updated on Thr Nov 07 2024

@author: byunguk park
"""

###########
# Imports #
###########

import sys
import os
import shutil
import timeit
import numpy as np
from htmd.ui import *
import subprocess
from htmd.protocols.equilibration_v3 import Equilibration
from htmd.protocols.production_v6 import Production

##########
# Inputs #
##########

WORKING_DIR = sys.argv[1]
input_file  = sys.argv[2]
PDB_DIR     = sys.argv[3]
PRM_DIR     = sys.argv[4]
equil_time  = float(sys.argv[5])
prod_time   = float(sys.argv[6])

## add runtime, temperature, etc. as input arguments later

ptn_caps = {'P': ['first NTER', 'last CTER']}
# ptn_caps = {'P': ['first ACE', 'last CT2']}

# Mapping from various residue caps to charmm patches
R"""
CHARMM patches:
# N-terminus patches
NTER         1.00 ! standard N-terminus
GLYP         1.00 ! Glycine N-terminus
PROP         1.00 ! Proline N-Terminal
ACE          0.00 ! acetylated N-terminus
ACED         0.00 ! acetylated N-terminus (to create dipeptide)
ACP          0.00 ! acetylated N-terminus for proline
ACPD         0.00 ! acetylated N-terminus for proline (to create dipeptide)
NNEU         0.00 ! neutral N-terminus; charges from LSN
# C-Terminus patches
CTER        -1.00 ! standard C-terminus
CNEU         0.00 ! protonated (neutral) C-terminu, charges from ASPP
CTP          0.00 ! protonated C-terminus
CT1          0.00 ! methylated C-terminus from methyl acetate
CT2          0.00 ! amidated C-terminus
CT3          0.00 ! N-Methylamide C-terminus
"""

#############
# Functions #
#############

def sys_prep(WORKING_DIR, PDB_DIR, PDB_ID, PRM_DIR):
    os.makedirs(f'{WORKING_DIR}/{PDB_ID}/build-charmm')
    pdb = f"{PDB_DIR}/{PDB_ID}.pdb"
    mol = Molecule(pdb)
    mol.filter("protein")
    print(f"====> system preparation done")
    mol_op = systemPrepare(mol)
    mol_seg = autoSegment(mol_op)
    print(f"====> auto segmentation done")
    mol_solv = solvate(mol_seg,pad=10)
    print(f"====> system solvation done")
    # mol_charmm = charmm.build(mol_solv, outdir=f'{WORKING_DIR}/{PDB_ID}/build-charmm',)   # for neutral N-terminus and C-terminus
    mol_charmm = charmm.build(mol_solv,
                              caps=ptn_caps,
                              outdir=f'{WORKING_DIR}/{PDB_ID}/build-charmm',
                              )
    print(f"====> CHARMM36 forcefield applied")
    # CHARMM36 parameters update from forcefield source directory
    shutil.copy(PRM_DIR, f'{WORKING_DIR}/{PDB_ID}/build-charmm/parameters')

def sys_equil(WORKING_DIR, PDB_ID, PRM_DIR, equilt_t=1):
    # Equilibration protocol setup
    os.makedirs(f'{WORKING_DIR}/{PDB_ID}/equil')
    md = Equilibration()
    md.runtime = equilt_t
    md.timeunits = 'ns'
    md.temperature = 298.15
    md.acemd.barostat = "on"
    md.acemd.barostatpressure = 1.0
    md.useconstantratio = False                  # only for membrane sims
    md.write(f'{WORKING_DIR}/{PDB_ID}/build-charmm', f'{WORKING_DIR}/{PDB_ID}/equil')    
    
    # CHARMM36 parameters update from forcefield source directory
    shutil.copy(PRM_DIR, f'{WORKING_DIR}/{PDB_ID}/equil/parameters')
    # equilibration run
    local = LocalGPUQueue()
    local.submit(f'{WORKING_DIR}/{PDB_ID}/equil')
    local.wait()
    print(f"====> Equilibration run Done\n")

def sys_prod(WORKING_DIR, PDB_ID, PRM_DIR, prod_t=10):
    # Production protocol setup
    # for manual: https://software.acellera.com/htmd/htmd.mdengine.acemd.acemd.html
    os.makedirs(f'{WORKING_DIR}/{PDB_ID}/prod')
    md = Production()
    md.runtime = prod_t
    md.timeunits = 'ns'
    md.acemd.timestep = 2                       # 2fs/step
    md.acemd.trajectoryperiod = 25000           # frame/25000steps
    md.acemd.switching = "on"
    md.acemd.switchdistance = 10
    md.acemd.cutoff = 12
    # thermostat
    md.temperature  = 298.15
    md.useconstantratio = False                 # only for membrane sims
    # barostat
    md.acemd.barostat = "on"
    md.acemd.barostatpressure = 1.0
    md.acemd.barostatconstratio = "off"
    md.acemd.barostatconstxy = "off"
    md.acemd.slowperiod = 1                     # Barostat cannot be used if "slowperiod" > 1
    md.acemd.bincoordinates = 'output.coor'
    md.acemd.extendedsystem  = 'output.xsc'
    md.write(f'{WORKING_DIR}/{PDB_ID}/equil',f'{WORKING_DIR}/{PDB_ID}/prod')

    # CHARMM36 parameters update from forcefield source directory
    shutil.copy(PRM_DIR, f'{WORKING_DIR}/{PDB_ID}/prod/parameters')
    # production run
    local = LocalGPUQueue()
    local.submit(f'{WORKING_DIR}/{PDB_ID}/prod')
    local.wait()
    print(f"====> Production run Done\n")

def traj_wrap(output_dir, wrap_center):
    mol = Molecule(f"{output_dir}/structure.psf")     # Can also read PSF topology files
    mol.read(f"{output_dir}/output.xtc")              # Can also read DCD trajectories
    mol.wrap(wrap_center)                             # Wrap the box around the average protein coordinates
    mol.write(f"{output_dir}/output_wrapped.xtc")     # Writes out the wrapped simulation to a new XTC file

# =====================================================================================================

# Executable part

tic_total = timeit.default_timer()
with open(f"{input_file}") as f:
    PDB_IDs = f.readlines()
    for PDB_ID in PDB_IDs:
        PDB_ID = PDB_ID.strip()
        print(f"============ {PDB_ID} ============")
        tic = timeit.default_timer()

        sys_prep(WORKING_DIR, PDB_DIR, PDB_ID, PRM_DIR)
        sys_equil(WORKING_DIR, PDB_ID, PRM_DIR, equilt_t=equil_time)
        sys_prod(WORKING_DIR, PDB_ID, PRM_DIR, prod_t=prod_time)
        output_dir = f"{WORKING_DIR}/{PDB_ID}/prod"
        traj_wrap(output_dir, "protein")
        
        toc = timeit.default_timer()
        print(f"====> Total Time: {toc - tic:.2f} sec\n\n")

toc_total = timeit.default_timer()
total_simul_t = equil_time + prod_time

print("==========================================")
print("=== HTMD Simulation Statistics Summary ===")
print("==========================================\n")
print(f"Total Time for {total_simul_t:.1f}ns NPT HTMD runs of {len(PDB_IDs)} PDB IDs: {toc_total - tic_total:.2f} sec or {(toc_total - tic_total)/3600:.2f} hours")
print(f"Average Simulation Performance per Protein: {total_simul_t/(toc_total - tic_total)/3600/len(PDB_IDs):.2f} ns/hours\n\n")

# # =====================================================================================================

# legacy code

# more explicit version of charmm.build() --> didn't work well as expected though, need more debugging & source code check

    # mol_charmm = charmm.build(mol_solv,
    #                           caps=ptn_caps,
    #                           ionize=True,
    #                           saltconc=0,
    #                           saltanion="CL",
    #                           saltcation="NA",
    #                           outdir=f'{WORKING_DIR}/{PDB_ID}/build-charmm',
    #             )

# when running HTMD simulation using subprocess instead of using LocalGPUQueue()

    # # need to run it from inside the folder. Just chdir into that folder and it will work
    # os.chdir(f'{WORKING_DIR}/{PDB_ID}/prod')
    # # production run
    # cmd = f'bash run.sh'
    # # Use subprocess.run() to execute the command
    # result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # # Print the standard output and standard error of the command
    # print(result.stdout.decode())
    # print(result.stderr.decode())
