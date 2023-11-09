from myqueue.task import task as mqtask
from myqueue.task import State
from pathlib import Path
from asr.core import read_json, chdir, write_json
from ase.io import read
import numpy as np
import os, re
from gpaw.response.berryology import get_optical_conductivity

def get_old_magmoms(folder):
    magmoms = read_json(f'{folder}/results-asr.magstate.json')["magmoms"]
    return magmoms

def get_new_magmoms(folder):
    magmoms = read_json(f'{folder}/results-asr.anomalous_hall_conductivity.json')['magmoms']
    return magmoms


#def get_new_magmoms(folder):
    
#    atoms = read(f"{folder}/structure.json")
    #magnetic_atoms = []

    #TM3d_atoms = ['V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu']
    
#    atoms = np.arange(0,len(atoms))
    #for atom in atoms:
    #    if atom.symbol in TM3d_atoms:
    #        magnetic_atoms.append(1)
    #    else:
    #        magnetic_atoms.append(0)
                
    #magnetic_atoms_upper_layer = magnetic_atoms[:len(magnetic_atoms)//2]
    #mag_atoms = [x for x, z in enumerate(magnetic_atoms) if z == 1]

#    lines = []
#    magmoms = []
#    with open(f'{folder}/gs.txt', 'r') as read_obj:
#        for line in read_obj:

#            line = line.strip()
#            lines.append(line)
#            if line == 'Local magnetic moments:': 
#                mag_line_fm = line
                    
        #if not 'mag_line_fm' in locals():
        #    read_obj.close()
        #    magmoms = 'None'
        #    return None

#    read_obj.close()
#    start_line = lines.index(mag_line_fm)
#    maglines = [start_line + 1 + x for x in atoms]

#    for line in lines:
#        if lines.index(line) in maglines:
#            newline = str(str(line).split("(")[-1]).split(",")[-1]
#            magmoms.append(str(newline).split(")")[0])
    
#    magmoms = [float(x) for x in magmoms]
        
#    return magmoms

def get_deviation_matrix(comparative_matrix, magmoms):

    deviation_matrix = []
    for i in np.arange(0, len(magmoms)):
        row = []
        for j in np.arange(0, len(magmoms)):
            if comparative_matrix[i][j] == 1:
                try:
                    row.append( (abs(magmoms[i]) - abs(magmoms[j]) )/ abs(magmoms[j]) )
                except:
                    row.append(1)
            else:
                row.append(0)
        deviation_matrix.append(row)

                
    deviation_matrix = np.array(deviation_matrix)
    #except:
    #    deviation_matrix = np.array([1])
    
    return deviation_matrix

def get_comparative_matrix(folder):
    TM3d_atoms = ['V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu']

    info = read_json(f'{folder}/results-asr.structureinfo.json')
    eq_atoms = info["spglib_dataset"]["equivalent_atoms"] 
    structure = read(f'{folder}/structure.json')
    atoms = structure.symbols
    
    #eq_mag_atoms = []
    #mag_atoms = []
    #mag_atoms_index = []
    #for i in np.arange(0, len(atoms)):
    #    if atoms[i] in TM3d_atoms:
    #        eq_mag_atoms.append(eq_atoms[i])
    #        mag_atoms.append(atoms[i])
    #        mag_atoms_index.append(i)

    comparative_matrix = []
    for i in np.arange(0, len(atoms)):
        row = []
        for j in np.arange(0, len(atoms)):
            if atoms[i] in TM3d_atoms and atoms[j] in TM3d_atoms:
                if eq_atoms[i] == eq_atoms[j]:
                    row.append(1)
                else:
                    row.append(0)
            else:
                row.append(0)
        comparative_matrix.append(row)

    return comparative_matrix 

def check_FM(folder):
    structure = read(f'{folder}/structure.json')
    magmoms = read_json(f'{folder}/results-asr.anomalous_hall_conductivity.json')['magmoms']
    atoms = structure.symbols
    #print(atoms)
    #print(magmoms)
    mag_atoms = ['Y', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu']
    relevant_magmoms = []
    for i in np.arange(0, len(atoms)):
        if atoms[i] in mag_atoms:
            relevant_magmoms.append(magmoms[i])
            
    #print(relevant_magmoms)
    if all(1 == relevant_magmom for relevant_magmom in np.sign(relevant_magmoms)):
        #if np.logical_and(np.sign(relevant_magmoms) == 1 and np.sign(relevant_magmoms) == 1).all():
        return True
    if not all(1 == relevant_magmom for relevant_magmom in np.sign(relevant_magmoms)):
        #if not np.logical_and(np.sign(relevant_magmoms) == 1 and not np.logical_and(np.sign(relevant_magmoms) == 1).all():
        return False

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("folders", nargs="*", help="Monolayer folders to analyse.")

    args = parser.parse_args()
    
    if len(args.folders) > 0:
        folders = [Path(x).absolute() for x in args.folders]
    else:
        folders = [Path(".").absolute()]

    #total_number = []
    #finished = []
    failed_calculations = []
    for folder in folders:
        #try:
        #    magmoms = read_json(f'{folder}/results-asr.anomalous_hall_conductivity.json')["magmoms"]
        #except:
        #    failed_calculations.append(folder)
        #    print(folder)

        #total_number.append(folder)
        #try:
        #    ahc = read_json(f'{folder}/results-asr.anomalous_hall_conductivity.json')
        #    finished.append(folder)
        #except:
        #    print(folder)
        #    pass

        magmoms_old = get_old_magmoms(folder)
        magmoms_new = get_new_magmoms(folder)
        comparative_matrix = get_comparative_matrix(folder)
        if check_FM(folder):
            deviation_matrix = get_deviation_matrix(comparative_matrix, magmoms_new)
            if np.any([[x > 0.1 for x in y] for y in deviation_matrix]):
                #print(folder)
                #print(deviation_matrix)
                failed_calculations.append(folder)
                
        else:
            print('non-FM state')
            print(folder)

    #print(len(finished))
    #print(len(total_number))
    print(len(failed_calculations))



    
    
