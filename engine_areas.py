#Calculate engine areas from a chosen design point (here: beginning of cruise?)

# engine_areas.py

from cycle_functions import nozzle_area_calculation, calculate_area_from_normalised_mass_flow_rate,calculate_normalised_mass_flow_rate
from engine_parameters import *

def calculate_engine_areas(
    design,
    engine,
    Pa,
    verbose=True
):

    # -------------------------
    # Unpack engine parameters
    # -------------------------
    gamma = engine["gammaD"]
    gammaT = engine["gammaT"]
    gammaN = engine["gammaN"]
    Cp = engine["Cp"]
    Cpt = engine["Cpt"]
    Cpn = engine["Cpn"]
    etaT = engine["etaT"]
    # -------------------------
    # Unpack design-point data
    # -------------------------
    #Pa = design["Pa"]
    P04 = design["P04"]
    T04 = design["T04"]
    P045 = design["P045"]
    T045 = design["T045"]
    P05 = design["P05"]
    T05 = design["T05"]
    P013 = design["P013"]
    T013 = design["T013"]

    core_mass_flow = design["core_mass_flow"]
    bypass_mass_flow = design["bypass_mass_flow"]
  
    # -------------------------
    # Core nozzle
    # -------------------------
    core_nozzle = nozzle_area_calculation(
        name="Core nozzle",
        P0in=P05,
        T0in=T05,
        Pout=Pa,
        mass_flow=core_mass_flow,
        gamma=gammaN,
        Cp=Cpn,
        calculate_exit=True,
    )

    # -------------------------
    # Bypass nozzle
    # -------------------------

    bypass_nozzle = nozzle_area_calculation(
        name="Bypass nozzle",
        P0in=P013,
        T0in=T013,
        Pout=Pa,
        mass_flow=bypass_mass_flow,
        gamma=gamma,
        Cp=Cp,
        calculate_exit=False,
    )

    # -------------------------
    # HPT nozzle
    # -------------------------
    '''
    HPT_nozzle = nozzle_area_calculation(
        name="HPT nozzle",
        P0in=P04,
        T0in=T04,
        Pout=P045,
        mass_flow=core_mass_flow,
        gamma=gammaT,
        Cp=Cpt,
        calculate_exit=False,
    )'''
    HPT_norm_m = calculate_normalised_mass_flow_rate(1, gammaT)
    HPT_nozzle_area = calculate_area_from_normalised_mass_flow_rate(core_mass_flow,HPT_norm_m,P04,T04,Cpt)
#area = calculate_area_from_normalised_mass_flow_rate(mass_flow,norm_m,P0in,T0in,Cp)
#HPT_norm_m = calculate_normalised_mass_flow_rate(1, gamma)
    
    # -------------------------
    # LPT nozzle
    # -------------------------
    '''
    LPT_nozzle = nozzle_area_calculation(
        name="LPT nozzle",
        P0in=P045,
        T0in=T045,
        Pout=P05,
        mass_flow=core_mass_flow,
        gamma=gammaT,
        Cp=Cpt,
        calculate_exit=False,
    )'''
    LPT_norm_m = calculate_normalised_mass_flow_rate(1, gammaT)
    LPT_nozzle_area = calculate_area_from_normalised_mass_flow_rate(core_mass_flow,LPT_norm_m,P045,T045,Cpt)

    # -------------------------
    # Turbine area ratio check
    # -------------------------

    ratio_check_direct = HPT_nozzle_area / LPT_nozzle_area
    '''
    ratio_check_direct = (
        HPT_nozzle["area"] /
        LPT_nozzle["area"]
    )
    '''
    '''
    ratio_check_fromT_corrected = (
        HPT_nozzle["normalised_mass_flow"]
        / LPT_nozzle["normalised_mass_flow"]
        * (T045 / T04)**0.5
        * (
            1 + (1/etaT) * ((T045 / T04) - 1)
        ) ** (gammaT / (1 - gammaT))
    )'''

    '''
    if verbose:
      print("")
      print("===================================")
      print("Engine nozzle areas")
      print("===================================")
      print("A4:", HPT_nozzle["area"])
      print("A45:", LPT_nozzle["area"])
      print("A9:", core_nozzle["area"])
      print("A19:", bypass_nozzle["area"])
      print("A4/A45:", ratio_check_direct)
      print("A4/A45 check:", 1 / ratio_check_fromT_corrected)
      print("===================================")
      print("")
    '''
    
    # -------------------------
    # Return all area results
    # -------------------------
    return {
        "A4": HPT_nozzle_area,
        "A45": LPT_nozzle_area,
        "A9": core_nozzle["area"],
        "A19": bypass_nozzle["area"],

        #"norm_m_4": HPT_nozzle["normalised_mass_flow"],
        #"norm_m_45": LPT_nozzle["normalised_mass_flow"],
        "norm_m_9": core_nozzle["normalised_mass_flow"],
        "norm_m_19": bypass_nozzle["normalised_mass_flow"],

        #"choked_4": HPT_nozzle["choked"],
        #"choked_45": LPT_nozzle["choked"],
        "choked_9": core_nozzle["choked"],
        "choked_19": bypass_nozzle["choked"],

        "M_exit_9": core_nozzle["Mexit"],
        "T_static_exit_9": core_nozzle["T_static_exit"],
        "area_ratio_HPT_LPT": ratio_check_direct,
        #"area_ratio_HPT_LPT_check": 1 / ratio_check_fromT_corrected,
    }