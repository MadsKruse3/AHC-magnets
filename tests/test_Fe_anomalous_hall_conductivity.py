import pytest
from gpaw import GPAW, PW, FermiDirac
from ase.build import bulk
from ase.units import Bohr
from gpaw.response.berryology import get_hall_conductivity

@pytest.mark.response
def test_Fe_bcc(in_tmp_dir, gpw_files):
    calc_file = gpw_files['fe_pw_wfs']

    ## Check results with default options (with the magnetization pointing along the z-direction). 
    sigma_xy_w_so, sigma_yz_w_so, sigma_zx_w_so = get_hall_conductivity(calc_file)

    print(sigma_xy_w_so)
    print(sigma_yz_w_so)
    print(sigma_zx_w_so)

    # ------------------ Check results without spin-orbit coupling. -----------------------#
    sigma_xy_wo_so, sigma_yz_wo_so, sigma_zx_wo_so = get_hall_conductivity(calc_file, scale=0.0)

    

    # ------------------ Check results when M is oriented along the x-axis. -----------------------#
    sigma_xy_M_x, sigma_yz_M_x, sigma_zx_M_x = get_hall_conductivity(calc_file, theta=90, phi=0)

    # ------------------ Check results when M is oriented along the y-axis. -----------------------#
    sigma_xy_M_y, sigma_yz_M_y, sigma_zx_M_z = get_hall_conductivity(calc_file, theta=90, phi=90)

    #----------------- Test counting only contributions of 2 bands (occupied or unoccupied) ---------------------#
    #n1 = 1
    #n2 = 4
    #sigma_xy_wo_so, sigma_yz_wo_so, sigma_zx_wo_so = get_hall_conductivity(calc_file, n1=n1, n2=n2)

    #----------------- Test results with only 2 occupied bands ---------------------#
    #mi = 2
    #mf = 3
    #sigma_xy_wo_so, sigma_yz_wo_so, sigma_zx_wo_so = get_hall_conductivity(calc_file, mi=mi, mf=mf)


