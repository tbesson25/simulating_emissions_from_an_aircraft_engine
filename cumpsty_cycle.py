from cycle_functions import *

R = 287  # Gas constant for air in J/kg.K
tref = 298

# def run_cumpsty_cycle(M, Ta, Pa, T04, engine, Thrust=None):


def run_cumpsty_cycle(M, Ta, Pa, T04, engine, Thrust):
    # unpack parameters
    etaD = engine["etaD"]
    etaF = engine["etaF"]
    etaC = engine["etaC"]
    etaT = engine["etaT"]
    etaN = engine["etaN"]
    etaBN = engine["etaBN"]
    etaPC = engine["etaPC"]
    etaPT = engine["etaPT"]

    gammaD = engine["gammaD"]
    gammaF = engine["gammaF"]
    gammaC = engine["gammaC"]
    gammaT = engine["gammaT"]
    gammaN = engine["gammaN"]

    Cp = engine["Cp"]
    Cpf = engine["Cpf"]
    Cpc = engine["Cpc"]
    Cpb = engine["Cpb"]
    Cpt = engine["Cpt"]
    Cpn = engine["Cpn"]

    FPR = engine["FPR"]
    FBPR = engine["FBPR"]
    CPR = engine["CPR"]
    BPR = engine["BPR"]

    A = engine["A"]
    # jai suppr les A4, A9, A19

    LCV = engine["LCV"]

    results = {}

    # Calculations
    # Station 2
    u = M * (gammaD * R * Ta) ** 0.5
    direct_air_flow = (
        (Pa / (R * Ta)) * u * A
    )  # freestream mass-flow estimate/ capture flow
    T02 = Ta * (1 + ((gammaD - 1) / 2) * M**2)
    P02 = calculate_stagnation_pressure(etaD, gammaD, Pa, Ta, T02)

    T02_ref = 288.15
    P02_ref = 101325
    teta = T02 / T02_ref
    delta = P02 / P02_ref
    direct_air_flow_corrected = direct_air_flow * (teta**0.5) / delta
    results["T02"] = T02
    results["P02"] = P02
    results["u"] = u
    # direct_air_flow = direct_air_flow_corrected
    results["direct_air_flow"] = direct_air_flow
    # results["direct_air_flow_corrected"] = direct_air_flow_corrected

    # Station 13 - Bypass stream leaving the fan
    T013 = calculate_stagnation_temperature(etaF, gammaF, T02, FPR)
    P013 = FPR * P02
    u_jb = calculate_velocity(etaBN, gammaF, Cpf, T013, P013, Pa)
    deltaT_bystream = T013 - T02
    results["T013"] = T013
    results["P013"] = P013
    results["u_jb"] = u_jb
    results["deltaT_bystream"] = deltaT_bystream

    # Station 23 - Leaving booster
    T023 = calculate_stagnation_temperature(etaC, gammaC, T02, FBPR)
    P023 = P02 * FBPR
    T023 = calculate_stagnation_temperature_polytropic_compressor(
        gammaC, etaPC, T02, P02, P023
    )
    kt = (T023 - T02) / (T013 - T02)
    results["T023"] = T023
    results["P023"] = P023
    results["kt"] = kt

    # Station 3 - Leaving HPC
    etaPC = etaC
    HPCPR = CPR / FBPR
    T03 = calculate_stagnation_temperature(etaPC, gammaC, T023, HPCPR)
    P03 = P02 * CPR
    T03 = calculate_stagnation_temperature_polytropic_compressor(
        gammaC, etaPC, T023, P023, P03
    )
    results["T03"] = T03
    results["P03"] = P03

    # Station 4 - Leaving combustor
    burnerPR = 1.0
    P04 = burnerPR * P03
    T04min = (Cp * (T03 - T023) + Cpc * (T023 - T02) + BPR * Cp * (T013 - T02)) / (
        Cpt * etaT * (1 - (Pa / P04) ** ((gammaT - 1) / gammaT))
    ) #only if use adiab efficiency (build on)
    results["P04"] = P04
    results["T04"] = T04
    results["T04min"] = T04min

    # Fuel-air ratio
    f_cumpsty = (Cp * (T04 - T03)) / LCV
    #f_cumpsty = (Cpt *T04 - Cpc*T03) / (LCV)
    f_cumpsty_t04min = Cp * (T04min - T03) / LCV
    # f_cumpsty = (Cpt*(T04-tref)-Cpc*(T03-tref))/(LCV-Cpt*(T04-tref))

    results["f_cumpsty"] = f_cumpsty
    results["f_cumpsty_t04min"] = f_cumpsty_t04min

    # Station 45 - Leaving HPT
    T045 = T04 - (Cpc / Cpt) * (T03 - T023)
    P045 = calculate_stagnation_pressure(1 / etaT, gammaT, P04, T04, T045)
    P045 = calculate_stagnation_pressure_polytropic_turbine(
        gammaT, etaT, P04, T04, T045
    )
    T045min = (Cpc / Cpt) * (T023 - T02) + BPR * (Cp/Cpt) * (T013 - T02) + T04*(Pa/P04)**(etaT*(gammaT-1)/gammaT)
    k_hp = 1 - (T045 / T04)
    results["T045"] = T045
    results["T045min"] = T045min
    results["P045"] = P045
    results["k_hp"] = k_hp
    HPT_power = Cpt * (T04 - T045)  # Check on HPT power balance
    HPC_power = Cpc * (T03 - T023)
    results["HPT_power"] = HPT_power
    results["HPC_power"] = HPC_power

    # Station 5 - Leaving LPT
    T05 = T045 - (Cpc / Cpt) * (T023 - T02) - (Cp / Cpt) * BPR * (T013 - T02)
    P05 = calculate_stagnation_pressure(1 / etaT, gammaT, P045, T045, T05)
    P05 = calculate_stagnation_pressure_polytropic_turbine(
        gammaT, etaPT, P045, T045, T05
    )
    deltaT_LPT = T045 - T05
    results["T05"] = T05
    results["P05"] = P05
    results["deltaT_LPT"] = deltaT_LPT
    power_balance_LPT = Cpt * (T045 - T05)  # Check on LPT power balance
    power_balance_LPC = Cp * BPR * (T013 - T02) + Cpc * (T023 - T02)
    results["LPT_power"] = power_balance_LPT
    results["LPC_power"] = power_balance_LPC

    # Station 9 - Core nozzle
    u_jc = calculate_velocity(etaN, gammaN, Cpn, T05, P05, Pa)
    results["u_jc"] = u_jc
    results["P05_Pa"] = P05 / Pa

    # Performance
    ST = calculate_ST(f_cumpsty, u_jb, u_jc, u, BPR)
    results["ST"] = ST
    direct_thrust = ST * direct_air_flow
    results["direct_thrust"] = direct_thrust

    direct_core_mass_flow = direct_air_flow / (1 + BPR)
    direct_bypass_mass_flow = BPR * direct_core_mass_flow
    direct_fuel_mass_flow = f_cumpsty * direct_core_mass_flow
    results["direct_core_mass_flow"] = direct_core_mass_flow
    results["direct_bypass_mass_flow"] = direct_bypass_mass_flow
    results["direct_fuel_mass_flow"] = direct_fuel_mass_flow

    TSFC = calculate_TSFC(f_cumpsty, ST, BPR)
    results["TSFC"] = TSFC

    n_p = calculate_propulsive_efficiency_2S(f_cumpsty, u, u_jc, u_jb, BPR)
    results["eta_propulsive"] = n_p

    n_th = calculate_thermal_efficiency_2stream(f_cumpsty, u_jc, u_jb, u, BPR, LCV)
    results["eta_thermal"] = n_th

    n_o = calculate_overall_efficiency(n_th, n_p)
    results["eta_overall"] = n_o

    # For mass flow calculation
    if Thrust is not None:
        Thrust = 0.7 * Thrust
        total_air_mass_flow = Thrust / ST
        core_mass_flow = total_air_mass_flow / (1 + BPR)
        bypass_mass_flow = (BPR * total_air_mass_flow) / (1 + BPR)
        fuel_mass_flow = (f_cumpsty / (1 + BPR)) * total_air_mass_flow
        # total_air_mass_flow = core_mass_flow * (1 + BPR)
        bypass_mass_flow_bis = BPR * core_mass_flow
        # fuel_mass_flow = f_cumpsty * core_mass_flow

        Thrust = direct_thrust
        total_air_mass_flow = direct_air_flow
        core_mass_flow = direct_core_mass_flow
        bypass_mass_flow = direct_bypass_mass_flow
        fuel_mass_flow = direct_fuel_mass_flow

        results["Thrust"] = Thrust
        results["core_mass_flow"] = core_mass_flow
        results["total_air_mass_flow"] = total_air_mass_flow
        results["bypass_mass_flow"] = bypass_mass_flow
        results["bypass_mass_flow_bis"] = bypass_mass_flow_bis

        results["fuel_mass_flow"] = fuel_mass_flow

    return results
