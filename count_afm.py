from myqueue.task import task as mqtask
from myqueue.task import State
from pathlib import Path
from asr.core import read_json, chdir, write_json
from ase.io import read
#from ase.build import make_supercell
import numpy as np
import os, re
#from gpaw.gpaw.optical_conductivity import get_optical_conductivity
from gpaw.response.berryology import get_optical_conductivity

def check_magnetic_state(folder):
    try:
        data = read_json(f"{folder}/results-asr.exchange.json")
        J = data["J"]
    except:
        J = 1

    magstate = None
    if J > 0:
        magstate = 'FM'
    if J < 0:
        magstate = 'AFM'
    return magstate

def change_magnetic_state(folder):
    structure = read(f"{folder}/structure.json")
    magmoms = structure.get_magnetic_moments()
    
    TM3d_atoms = ['Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Os']
    FM_syms = structure.get_chemical_symbols()
    j = 0
    for x in [i for i, e in enumerate(FM_syms) if e in TM3d_atoms]:
        j += 1
        if (j % 2):
            continue
        else:
            magmoms[x] = -magmoms[x]
    structure.set_initial_magnetic_moments(magmoms)
    #structure.write("structure.json")
    return 

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("folders", nargs="*", help="Monolayer folders to analyse.")

    args = parser.parse_args()
    
    if len(args.folders) > 0:
        folders = [Path(x).absolute() for x in args.folders]
    else:
        folders = [Path(".").absolute()]

    #plt.rcParams['font.family'] = 'serif'
    #plt.rcParams['font.serif'] = ['Times New Roman'] + plt.rcParams['font.serif']
    #plt.rcParams['axes.labelsize'] = 'large'

    AFM_states = []
    FM_states = []
    for folder in folders:
        magstate = check_magnetic_state(folder)
        if magstate == 'FM':
            FM_states.append(magstate)
        if magstate == 'AFM':
            AFM_states.append(magstate)
            change_magnetic_state(folder)
 
    print(len(FM_states))
    print(len(AFM_states))
