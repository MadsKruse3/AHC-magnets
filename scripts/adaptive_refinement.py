from gpaw import GPAW, kpt_descriptor
from gpaw import typing
import numpy as np

""" Module for adaptive refinement. 
    Import the 'adaptive_refinement' function.
"""

def adaptive_refinement_grid(kpts_old, 
                             size):
    """Construct a uniform Gamma centered grid suited for adaptive refinement a given size and 
    rescale this such that it can be substituted or added to an older k-point grid"""
    
    original_grid = kpt_descriptor.KPointDescriptor(kpts_old, 2).N_c
    
    if np.less_equal(size, 0).any():
        raise ValueError('Illegal size: %s' % list(size))
    
    kpts = np.indices(size).transpose((1, 2, 3, 0)).reshape((-1, 3))
    monkhorst_pack_grid = (kpts + 0.5) / size - 0.5 ## Formula for monkhorst packgrid, but with dimensions desired for the adaptive refinement grid    
    gamma_centered_grid = (kpts + 0.5) / size  - 0.5 ## Formula for Gamma-centered grid, but with dimensions desired for the adaptive refinement grid
    for ik in np.arange(0, len(size)):
        if size[ik] % 2 == 0:
            gamma_centered_grid[:,ik] = gamma_centered_grid[:,ik] - 0.5/size[i]

    if [0, 0, 0] not in gamma_centered_grid:
        raise ValueError('Grid not gamma-centered!')

    scale_factor = np.ndarray((1,3), dtype=float)  ## The new grid must be downscaled such that it fills out the area around one k-point that is replaced with a new k-grid
    for i in np.arange(0, len(scale_factor)):
        if size[i] == 1:
            scale_factor[i] = 1
        else:
            scale_factor[i] = 1/(original_grid[i]-1)

    rescaled_grid = gamma_centered_grid*scale_factor
    
    return rescaled_grid

def select_refinement_points(calculated_property, 
                             threshold=None):

    """Find the points where the calculated property exceeds a certain threshold
     defined with respect to the point where the calculated property is highest"""

    max_p = np.max(abs(calculated_property))

    if threshold is None:
        threshold = 0.1

    cutoff = max_p*threshold
    selected_points = []
    for x in np.arange(0,len(calculated_property)):
        if abs(calculated_property[x]) > cutoff:
            selected_points.append(x)

    return selected_points

def get_new_kpts(selected_points, 
                 kpts_old, 
                 refinement_grid):

    "Construct a new non-uniform k-point grid that contains refinement grids centered at the selected points.
    !! Note that these grids still contain the selected point, so this has to be removed elsewhere if double
    counting becomes an issue!!"
    
    point_displacements = []
    for i in selected_points:
        point_displacements.append(kpts_old[i])

    new_grids = []
    for i in np.arange(0, len(point_displacements)):
        new_grids.append(point_displacements[i] + refinement_grid)
    
    new_kpts = []
    for i in new_grids:
        for j in i:
            new_kpts.append(j)

    new_kpts = np.array(new_kpts)
    return new_kpts

def update_weights(selected_points, kpts, size):
    weights = np.ones(len(kpts))
    for i in selected_points:
        weights[i] = 1/(size[0]*size[1]*size[2])
    
    return weights
    
def adaptive_refinement(calculated_property: 1DArray = None, 
                        kpts_old: 3DArray = None, 
                        size: Array1D = None, 
                        threshold: float = None) -> 3DArray:

    """ Main function. This function carries out the refinement procedure and returns:
    - A new non-uniform refined k-point grid that contains refined grids around the selected points.
    - An array containing new weights, where the old points such that the points if needed for integration
    have a lower weight to compensate for the change in grid sampling.
    Required input:
    - An old set of k-points on which the relevant calculated property was evaluated.
    - The desired size of each refinement grid. 
    """

    refinement_grid = adaptive_refinement_grid(kpts_old, size)
    selected_points = select_refinement_points(calculated_property, threshold=threshold)
    kpts_new = get_new_kpts(selected_points, kpts_old, refinement_grid)
    new_weights = update_weights(selected_points, kpts, size)

    return kpts_new








