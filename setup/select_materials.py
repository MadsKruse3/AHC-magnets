from ase.db import connect

""" 
Pick out materials from the latest version of the C2DB database. 
Materials are picked on the condition that they are:
- dynamically stable (phonons and stiffness)
- magnetic
- metallic
"""

db = connect('c2db-first-class-20220327.db')

stable_magnetic_metal_rows = []
all_rows = []
for row in db.select():
    all_rows.append(row)

for row in all_rows:
    dynstab_phonon = row.get('dynamic_stability_phonons')
    dynstab_stiff = row.get('dynamic_stability_stiffness')
    magnetic = row.get('is_magnetic')
    gap = row.get('gap')
    if dynstab_phonon == 'high' and dynstab_stiff == 'high':
        if magnetic:
            if gap < 0.001:
                stable_magnetic_metal_rows.append(row)

print(len(stable_magnetic_metal_rows))

with connect('c2db_magnetic_metals.db') as polardb:
    for row in stable_magnetic_metal_rows:
        polardb.write(atoms=row.toatoms(), key_value_pairs=row.key_value_pairs, data=row.data)
