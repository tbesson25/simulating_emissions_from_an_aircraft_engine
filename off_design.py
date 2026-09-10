#General off-design calculation method, taking into account the engine areas
from cycle_functions import *
R = 287  # Gas constant for air in J/kg.K

def run_cumpsty_off_design(
  FPR,
  M_off,
  Ta_off,
  Pa_off,
  T04_off,
  design,
  engine,
  areas
):

  # Engine parameters
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

  kt = design["kt"]
  khp = design["k_hp"]

  # Fixed engine geometry
  A4 = areas["A4"]
  A45 = areas["A45"]
  A19 = areas["A19"]
  A9 = areas["A9"]

  # Station 02
  u = M_off*(gammaD*R*Ta_off)**0.5
  T02 = Ta_off * (
      1 + ((gammaD - 1) / 2) * M_off**2
  )
  P02 = calculate_stagnation_pressure(
      etaD,
      gammaD,
      Pa_off,
      Ta_off,
      T02
  )

  # Station 13 - Fan
  T013 = calculate_stagnation_temperature(
      etaF,
      gammaF,
      T02,
      FPR
  )
  P013 = FPR * P02
  u_jb = calculate_velocity(
          etaBN,
          gammaF,
          Cpf,
          T013,
          P013,
          Pa_off
      )

  # Station 23 - Booster
  T023 = T02 + kt * (T013 - T02)
  FBPR = (
      etaC * ((T023 / T02) - 1) + 1
  ) ** (gammaC / (gammaC - 1))
  FBPR = (T023/T02)**((etaPC*gammaC)/(gammaC-1))
  P023 = P02 * FBPR

# Fuel-air ratio
  LCV = engine["LCV"] 
  
    
  # Station 03 - HPC
  T03 = (
      khp * T04_off * (Cpt/ Cpc)
      + T023
  )
  f = Cp * (T04_off - T03) / LCV
    
  HPCPR = (
      etaC * ((T03 / T023) - 1) + 1
  ) ** (gammaC / (gammaC - 1))
  HPCPR = (T03/T023)**((etaPC*gammaC)/(gammaC-1))
  CPR = FBPR * HPCPR
  P03 = P02 * CPR

  # Station 04
  P04 = P03
    
  # Station 45 - HPT
  T045 = T04_off * (1 - khp)
  P045 = P04 * (
      1
      + (1/etaT) * ((T045 / T04_off) - 1)
  ) ** (gammaT / (gammaT - 1))
  P045 = P04 * (T045/T04_off)**((gammaT)/(etaPT*(gammaT-1)))
  P045 = P04 * (A4/A45)**((2*gammaT)/(2*gammaT-etaPT*(gammaT-1)))

  # Core mass flow from A4
  norm_m_core_A4 = calculate_nozzle_normalised_mass_flow(
      P04,
      P045,
      gammaT
  )
  mass_flow_core_A4 = calculate_mass_flow_rate_from_area(
      A4,
      norm_m_core_A4,
      P04,
      T04_off,
      Cpt
  )

  # Bypass mass flow from A19
  norm_m_bypass = calculate_nozzle_normalised_mass_flow(
      P013,
      Pa_off,
      gammaF
  )
  mass_flow_bypass_A19 = calculate_mass_flow_rate_from_area(
      A19,
      norm_m_bypass,
      P013,
      T013,
      Cp
  )

  # Bypass ratio
  BPR = mass_flow_bypass_A19 / mass_flow_core_A4

  T045min = (Cpc / Cpt) * (T023 - T02) + BPR * (Cp/Cpt) * (T013 - T02) + T04_off*(Pa_off/P04)**(etaT*(gammaT-1)/gammaT)

  # Station 05 - LPT
  T05 = (
      T045
      - (
          (Cp * BPR + Cpc * kt) / (Cpt)
      ) * (T013 - T02)
  )
  P05 = P045 * (
      1
      - (1 / etaT) * (1 - T05 / T045)
  ) ** (gammaT / (gammaT - 1))
  P05 = P045 * (T05 / T045) ** (gammaT / (etaPT * (gammaT - 1)))

  u_jc = calculate_velocity(
          etaN,
          gammaN,
          Cpn,
          T05,
          P05,
          Pa_off
      )

  

  # Specific Thrust
  ST_off = calculate_ST(
      f,
      u_jb,
      u_jc,
      u,
      BPR
    )

  TSFC = calculate_TSFC(f, ST_off, BPR)
    
  # Core mass flow from A9
  norm_m_core_A9 = calculate_nozzle_normalised_mass_flow(
      P05,
      Pa_off,
      gammaN
  )
  mass_flow_core_A9 = calculate_mass_flow_rate_from_area(
      A9,
      norm_m_core_A9,
      P05,
      T05,
      Cpn
  )
  mass_flow_air = mass_flow_core_A9 * (1+BPR)
  Thrust_off = mass_flow_air * ST_off    
  fuel_mass_flow = f * mass_flow_core_A9

  n_p = calculate_propulsive_efficiency_2S(f, u, u_jc, u_jb, BPR)
  n_th = calculate_thermal_efficiency_2stream(f, u_jc, u_jb, u, BPR, LCV)
  n_o = calculate_overall_efficiency(n_th, n_p)
 
  return {
      "FPR": FPR,

      "T02": T02,
      "P02": P02,

      "T013": T013,
      "P013": P013,
      "u_jb": u_jb,

      "T023": T023,
      "P023": P023,
      "FBPR": FBPR,

      "T03": T03,
      "P03": P03,
      "HPCPR": HPCPR,
      "CPR": CPR,

      "T04": T04_off,
      "P04": P04,

      "T045": T045,
      "T045min": T045min,
      "P045": P045,

      "T05": T05,
      "P05": P05,
      "u_jc": u_jc,

      "BPR": BPR,

      "f": f,

      "mass_flow_core_A4": mass_flow_core_A4,
      "mass_flow_core_A9": mass_flow_core_A9,
      "mass_flow_bypass_A19": mass_flow_bypass_A19,
      "fuel_mass_flow": fuel_mass_flow,

      # performance
      "u_jb": u_jb,
      "u_jc": u_jc,
      "ST": ST_off,
      "TSFC": TSFC,
      "Thrust": Thrust_off,
      "n_p": n_p,
      "n_th": n_th,
      "n_o": n_o,
      
  }
