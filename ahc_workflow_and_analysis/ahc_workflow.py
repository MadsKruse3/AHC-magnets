"""
Workflow for calculating the dc (omega=0) component of the anomalous hall conductivity
of all metallic magnets in C2DB. 
The workflow is factored into the following components:

  - New groudnstate calculation with a dense k-point grid ()... 
    as well as tighter convergence criteria.
  - A sanity check of the groundstate calculations (magnet moments, magnetic configuration etc.)
  - A calculation of the anomalous hall conductivity.

"""

from myqueue.task import task as mqtask
from myqueue.task import State
from pathlib import Path
from asr.core import read_json, chdir, write_json
from ase.io import read
import numpy as np
import os, re
from gpaw.response.berryology import get_optical_conductivity

VERBOSE = os.environ.get('MQVERBOSE', False)

def new_gs_calculate(folder):
    tasks = []

    #magstate = check_magnetic_state(folder)
    #if magstate == 'FM':
    #    continue
    #if magstate == 'AFM':
    #    setup_new_structure(folder)

    tasks += [task(f"asr.gs@calculate",
                   resources="40:2d", 
                   folder=folder)]
    return tasks

def new_gs(folder):
    tasks = []
    tasks += [task(f"asr.gs",
                   resources="40:2d", 
                   folder=folder)]
    return tasks

def ahc(folder):
    tasks = []

    tasks += [task(f"asr.anomalous_hall_conductivity",
                   resources="40:2d", 
                   folder=folder)]

    return tasks 

def task(*args, **kwargs):
    """Get MyQueue task instance."""
    name = kwargs.get("name") or args[0]
    if "creates" not in kwargs:
        kwargs["creates"] = [f"results-{name}.json"]
    return mqtask(*args, **kwargs)

def all_done(list_of_tasks):
    """Determine if all tasks in list_of_tasks are done."""
    return all([task.read_state_file() == State.done for task in list_of_tasks])

def return_tasks(tasks):
    """Wrap function for returning tasks."""
    if VERBOSE:
        print(get_cwd(), tasks)
    return tasks

def verbose_print(*args):
    """Only print if VERBOSE."""
    if VERBOSE:
        print(*args)

def get_cwd():
    """Get current working directory."""
    return Path('.').absolute()

def create_tasks():
    """Create MyQueue Task list for the ahc workflow.

    Note that this workflow relies on the folder layout so be
    careful.
    """
    tasks = []

    verbose_print(get_cwd())
    folder = Path('.')
    tasks += new_gs_calculate(folder)
    if not all_done(tasks):
       return tasks
    #tasks += new_gs(folder)
    #if not all_done(tasks):
    #    return tasks
    tasks += ahc(folder)        
    ## AR + ahc once more.
    return tasks
  

if __name__ == '__main__':
    tasks = create_tasks()

    for ptask in tasks:
        print(ptask, ptask.is_done())
