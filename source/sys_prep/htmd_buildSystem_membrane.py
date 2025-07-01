# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 2025
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
from htmd.membranebuilder.build_membrane import listLipids, buildMembrane
from htmd.home import home

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

def membrane_prep(dimensions=[100, 100], ratioupper={'popc': 10, 'chl1': 0}, ratiolower={'popc': 10, 'chl1': 0}):
    memb = buildMembrane(dimensions, ratioupper, ratiolower)
    memb.set('segid', 'M')
    return memb

def protein_prep(PDB_DIR, PDB_ID):
    pdb = f"{PDB_DIR}/{PDB_ID}.pdb"
    prot = Molecule(pdb)
    prot.filter("protein")
    prot_op = systemPrepare(prot)
    prot_seg = autoSegment(prot_op, sel="protein")
    prot_seg.set("segid", "W", sel="water")
    prot_seg.reps.add(sel='segid P0', style='NewCartoon', color=1)
    return prot_seg

def concat_system(memb, prot, z_offset_multiplier=16):
    ## center the membrane onto the protein center
    pcenter = np.mean(prot.get('coords','protein'),axis=0)
    mcenter = np.mean(memb.get('coords'),axis=0)
    # print(f"====> pcenter: {pcenter}, mcenter: {mcenter}")
    delta_v = pcenter - mcenter
    memb.moveBy((delta_v[0], delta_v[1], delta_v[2]*z_offset_multiplier))
    # print(f"====> membrane moved by {(delta_v[0], delta_v[1], delta_v[2]*16)}")
    ## embedding
    mol = prot.copy()
    mol.append(memb, collisions=True)
    return mol

def sys_prep(WORKING_DIR, PDB_DIR, PDB_ID, PRM_DIR):
    # membrane preparation
    memb = membrane_prep(dimensions=[100, 100],
                         ratioupper={'popc': 10, 'chl1': 0},
                         ratiolower={'popc': 10, 'chl1': 0}
                         )
    # protein preparation
    prot = protein_prep(PDB_DIR, PDB_ID)
    # system preparation
    mol = concat_system(memb, prot, z_offset_multiplier=16)
    # solvation
    coord = mol.get('coords','noh and (lipids or protein)')
    m = np.min(coord, axis=0) #+ [0, 0, -5]
    M = np.max(coord, axis=0) #+ [0, 0, 20]
    mol_solv = solvate(mol, minmax=np.vstack((m,M)))
    # CHARMM36 forcefield application
    os.makedirs(f'{WORKING_DIR}/{PDB_ID}/build-charmm')
    # mol_charmm = charmm.build(mol_solv, outdir=f'{WORKING_DIR}/{PDB_ID}/build-charmm',)
    mol_charmm = charmm.build(mol_solv,
                              caps=ptn_caps,
                              outdir=f'{WORKING_DIR}/{PDB_ID}/build-charmm',
                              )
    # CHARMM36 parameters update from forcefield source directory
    shutil.copy(PRM_DIR, f'{WORKING_DIR}/{PDB_ID}/build-charmm/parameters')


def sys_equil(WORKING_DIR, PDB_ID, PRM_DIR, equilt_t=1, constantratio=False):
    # Equilibration protocol setup
    os.makedirs(f'{WORKING_DIR}/{PDB_ID}/equil')
    md = Equilibration()
    md.runtime = equilt_t
    md.timeunits = 'ns'
    md.temperature = 298.15
    md.acemd.barostat = "on"
    md.acemd.barostatpressure = 1.0
    md.useconstantratio = constantratio                  # only for membrane sims
    md.write(f'{WORKING_DIR}/{PDB_ID}/build-charmm', f'{WORKING_DIR}/{PDB_ID}/equil')    
    
    # CHARMM36 parameters update from forcefield source directory
    shutil.copy(PRM_DIR, f'{WORKING_DIR}/{PDB_ID}/equil/parameters')
    # equilibration run
    local = LocalGPUQueue()
    local.submit(f'{WORKING_DIR}/{PDB_ID}/equil')
    local.wait()
    print(f"====> Equilibration run Done\n")

def sys_prod(WORKING_DIR, PDB_ID, PRM_DIR, prod_t=10, constantratio=False):
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
    md.useconstantratio = constantratio                 # only for membrane sims
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
        sys_equil(WORKING_DIR, PDB_ID, PRM_DIR, equilt_t=equil_time, constantratio=True)
        sys_prod(WORKING_DIR, PDB_ID, PRM_DIR, prod_t=prod_time, constantratio=True)
        output_dir = f"{WORKING_DIR}/{PDB_ID}/prod"
        # traj_wrap(output_dir, "protein")
        
        toc = timeit.default_timer()
        print(f"====> Total Time: {toc - tic:.2f} sec\n\n")

toc_total = timeit.default_timer()
total_simul_t = equil_time + prod_time

print("==========================================")
print("=== HTMD Simulation Statistics Summary ===")
print("==========================================\n")
print(f"Total Time for {total_simul_t:.1f}ns NPT HTMD runs of {len(PDB_IDs)} PDB IDs: {toc_total - tic_total:.2f} sec or {(toc_total - tic_total)/3600:.2f} hours")
print(f"Average Simulation Performance per Protein: {total_simul_t/(toc_total - tic_total)/3600/len(PDB_IDs):.2f} ns/hours\n\n")

