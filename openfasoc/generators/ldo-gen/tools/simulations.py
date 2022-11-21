import math
import os
import re
import shutil
import sys
import subprocess as sp


def matchNetlistCell(cell_instantiation):
    """returns true if the input contains as a pin (as a substring) one of the identified cells to remove for partial simulations"""
    removeIfFound = """vref_gen_nmos_with_trim"""
    removeIfFound = removeIfFound.split("\n")
    # names may not be exactly the same, but as long as part of the name matches then consider true
    # naming will automatically include some portion of the standard cell of origin name in the pin name
    for name in removeIfFound:
        for pin in cell_instantiation:
            if name in pin:
                return True
    # if tested all cells and none are true then false
    return False


def partial_remove_from_spice(netlist):
    """Comments out identified cells in matchNetlistCell and adds VREF/VREG to toplevel subckt def."""
    # comment out identified cells
    cells_array = netlist.split("\n")
    for cell in cells_array:
        if cell != "":
            cellPinout = cell.split(" ")
            cell_commented = cell
        if matchNetlistCell(cellPinout):
            cell_commented = "*" + cell
        netlist = netlist.replace(cell, cell_commented)
    # prepare toplevel subckt def (assumes VDD VSS last two in pin out)
    netlist = netlist.replace("VDD VSS", "VDD VSS VREF VREG", 1)
    return netlist


def configure_simulation(
    directories,
    designName,
    simType,
    arrSize,
    pdk_path,
    simTool="ngspice",
    model_corner="tt",
):
    """Prepare simulation run by configuring sim template."""
    # ensure specialized run directories are present
    try:
        os.mkdir(directories["simDir"] + "/run")
    except OSError as error:
        print("mkdir returned the following error:")
        print(error)
        print("Ignoring this error and continuing.")
    specialized_run_name = simType + "_PT_cells_" + str(arrSize)
    specialized_run_dir = directories["simDir"] + "/run/" + specialized_run_name
    os.mkdir(
        specialized_run_dir
    )  # throws if these simulations (i.e. dir) already exist
    # copy spice file and template
    flow_spice_dir = (
        directories["flowDir"] + "/objects/sky130hvl/ldo/base/netgen_lvs/spice/"
    )
    if simType == "prePEX":
        target_spice = designName + ".spice"
    elif simType == "postPEX":
        print("Unsupported simtype. postPEX currently not supported.")
        exit(1)
        # target_spice = designName+"_lvsmag.spice"
    else:
        print("Invalid simtype, specify either prePEX or postPEX.")
        exit(1)
    # prepare and copy spice file into sim dir
    with open(flow_spice_dir + target_spice, "r") as spice_in:
        spice_out = partial_remove_from_spice(spice_in.read())
    with open(specialized_run_dir + "/ldo_sim.spice", "w") as spice_prep:
        spice_prep.write(spice_out)
    # prepare spice control script
    template_sim_spice = "ldoInst_" + simTool + ".sp"
    shutil.copy(directories["simDir"] + "/templates/.spiceinit", specialized_run_dir)
    # copy spiceinit into run dir
    if simTool == "ngspice":
        shutil.copy(directories["simDir"] + "/templates/", specialized_run_dir)
    # configure sim template
    with open(specialized_run_dir + "/" + template_sim_spice, "r") as sim_spice:
        sim_template = sim_spice.read()
    sim_template = sim_template.replace(
        "@model_file", pdk_path + "/libs.tech/" + simTool + "/sky130.lib.spice"
    )
    sim_template = sim_template.replace("@model_corner", model_corner)
    sim_template = sim_template.replace("@design_nickname", designName)
    with open(specialized_run_dir + "/" + template_sim_spice, "w") as sim_spice:
        sim_spice.write(sim_template)
