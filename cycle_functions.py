#All functions used in the calculation model


#General/ main functions
def calculate_velocity(eta, gamma, Cp, T0, P0, Pa):
  u_j = (2 * eta * Cp * T0 * (1 - (Pa / P0) ** ((gamma - 1) / gamma))) ** 0.5
  return u_j

def calculate_stagnation_temperature(eta, gamma, T0in, PR):
  T0out = T0in * (1 + (1 / eta) * (PR ** ((gamma - 1) / gamma) - 1))
  return T0out

def calculate_stagnation_pressure(eta, gamma, P0in, T0in, T0out):
  P0out = P0in * ((1 + (eta) * ((T0out / T0in) - 1)) ** (gamma / (gamma - 1)))
  return P0out

def calculate_stagnation_pressure_polytropic_turbine(gamma,eta, P0in, T0in, T0out):
    P0out = P0in * ((T0out / T0in) ** (gamma / (eta*(gamma - 1))))
    return P0out

def calculate_stagnation_temperature_polytropic_compressor(gamma,eta, T0in, P0in, P0out):
    T0out = T0in * ((P0out / P0in) ** ((gamma - 1) / (eta*gamma)))
    return T0out
    


#Thrust
def thrust_bare(m_a, f, u_e, u_ef, u, BPR):
  thrust_bare = m_a * ((1 + f) * u_e + BPR * u_ef - (1 + BPR) * u)
  return thrust_bare

def thrust(T_bare, BPR):  # Thrust
  thrust = T_bare / (1.04 + 0.01 * (BPR**1.2))
  return thrust

#Specific Thrust
def calculate_specific_thrust_1S(u, u_j, f):
  ST = (1 + f) * u_j - u  # from p84 Cumpsty book
  return ST #1 stream (cf turbojet)

# Calculate thrust per unit flow i.e. specific thrust
def calculate_ST(f, u_fanexit, u_exit, uentry,BPR):
    ST = ((1 + f) * u_exit + BPR * u_fanexit - (1 + BPR) * uentry) / (1+BPR)  # Peterson eq 5.47
    return ST #2 streams

def calculate_TSFC(f, ST, BPR):
  TSFC = f / ((1+BPR)*ST)  # general definition
  return TSFC

# Efficiencies
def calculate_overall_efficiency_fromTSFC(u, LCV, TSFC,BPR):
    n_o = u / (LCV *(1+BPR)* TSFC)
    return n_o

# Propulsive efficiency definition
def calculate_propulsion_efficiency_1S(u, u_e):
    n_p = (2 * u) / (u + u_e)  # because f<<1
    return n_p


def calculate_propulsive_efficiency_2S(f, u, u_e, u_ef,BPR):
    n_p = (u * ((1 + f) * u_e + BPR * u_ef - (1 + BPR) * u)) / (
        0.5 * ((1 + f) * u_e**2 + BPR * u_ef**2 - (1 + BPR) * u**2)
    )
    return n_p


# from Cumpsty definition Cycle efficiency definition
def calculate_cycle_efficiency(etaT, etaC, T04, T03,T02, r, gamma):
    n_cy = (
        etaT * T04 * (1 - r ** ((1 - gamma) / gamma))
        - ((1 / etaC) * (T02 * (r ** ((gamma - 1) / gamma) - 1)))
    ) / (T04 - T03)  #cumpsty eq derivation
    return n_cy


# 1S Thermal efficiency definition
def calculate_thermal_efficiency_1stream(f, u_e, u,QR):
    n_th = (0.5 * ((1 + f) * (u_e**2) - (u**2))) / (f * QR)  # peterson eq 5.10
    return n_th


# 2S Thermal efficiency definition
def calculate_thermal_efficiency_2stream(f, u_e, u_ef, u,BPR,QR):
    n_th = (
        0.5
        * (((1 + f) * (u_e**2)) + (BPR * (u_ef**2)) - ((1 + BPR) * (u**2)))
        / (f * QR)
    )
    return n_th  


# Overall efficiency definition from th x p
def calculate_overall_efficiency(n_th, n_p):
    n_o = n_th * n_p
    return n_o


# Mass flow rate
def maximum_mass_flow_rate_from_unit_area_of_inlet(P02, T02, Pa_sl, Ta_sl, D):
    A = 3.14159 * ((D / 2) ** 2)
    gamma0 = P02 / Pa_sl  # _sl =02ref in book
    teta0 = T02 / Ta_sl
    m = A * 231.8 * (gamma0 / (teta0**0.5))
    return m  # mass flow rate kg/s

def calculate_air_mass_flow_rate(m, BPR):
    m_a = m / (1 + BPR)  # through core
    return m_a

def calculate_fuel_mass_flow_rate(f, m_a):
    m_f = f * m_a
    return m_f


# Normalised mass flow rates
def calculate_normalised_mass_flow_rate(M, gamma):
    norm_m = (
        M
        * (gamma / ((gamma - 1) ** 0.5))
        * (1 + ((gamma - 1) / 2) * M**2) ** (-(gamma + 1) / (2 * (gamma - 1)))
    )
    return norm_m

def calculate_isen_normalised_mass_flow_rate(gamma, P, P0in):
    ratio_P = P / P0in
    isen_norm_m = (gamma / (gamma - 1)) * (
        (2 * (ratio_P ** (2 / gamma) - ratio_P ** ((gamma + 1) / gamma))) ** 0.5
    )
    return isen_norm_m

def calculate_area_from_normalised_mass_flow_rate(m_a, norm_m, P0, T0, Cp):
    area = (m_a * ((Cp * T0) ** 0.5)) / (P0 * norm_m)
    return area

def definition_normalised_mass_flow_rate(m_a, Cp, T0, P0, A):
    normalised_mass_flow = m_a * ((Cp * T0) ** 0.5) / (P0 * A)
    return normalised_mass_flow

def calculate_choked_pressure_ratio(gamma):  # P/P0
    choked_ratio_P = (2 / (gamma + 1)) ** (gamma / (gamma - 1))
    inv_choked_ratio_P = 1 / choked_ratio_P
    return inv_choked_ratio_P  # p75 cumpsty

#Areas calculation 
def nozzle_area_calculation(name,P0in,T0in,Pout,mass_flow,gamma,Cp,calculate_exit=False):
  print(f"{name}:")
  print("-" * len(name))
  pressure_ratio = P0in / Pout
  choking_ratio = calculate_choked_pressure_ratio(gamma)
  print(f"P0/Pout = {pressure_ratio:.4f}")
  print(f"Choking ratio = {choking_ratio:.4f}")
  # Choking check
  if pressure_ratio > choking_ratio:
      norm_m = calculate_normalised_mass_flow_rate(1, gamma)
      choked = True
      print("Nozzle is CHOKED")
  else:
      norm_m = calculate_isen_normalised_mass_flow_rate(gamma,Pout,P0in)
      choked = False
      print("Nozzle is UNCHOKED")
  print(f"Normalised mass flow = {norm_m}")
  # Area calculation
  area = calculate_area_from_normalised_mass_flow_rate(mass_flow,norm_m,P0in,T0in,Cp)
  print(f"Area = {area:.6f} m²")

  Mexit = None
  T_static_exit = None
  # Only required for the core nozzle
  if calculate_exit:
      Mexit = ((2 / (gamma - 1))* (pressure_ratio**((gamma - 1) / gamma) - 1)) ** 0.5
      T_static_exit = T0in / (1 + ((gamma - 1) / 2) * Mexit**2)
      print(f"Mexit = {Mexit:.4f}")
      print(f"T_static_exit = {T_static_exit:.2f} K")
  print()

  return {
      "area": area,
      "normalised_mass_flow": norm_m,
      "choked": choked,
      "Mexit": Mexit,
      "T_static_exit": T_static_exit,
  }


def calculate_mass_flow_rate_from_area(area, norm_m, P0, T0, Cp):
  mass_flow_rate = (area * norm_m * P0) / ((Cp * T0) ** 0.5)
  return mass_flow_rate

def calculate_nozzle_normalised_mass_flow(P0in, P0out, gamma):
  pressure_ratio = P0in / P0out
  choking_ratio = calculate_choked_pressure_ratio(gamma)
  if pressure_ratio > choking_ratio:
      return calculate_normalised_mass_flow_rate(1, gamma)
  else:
      return calculate_isen_normalised_mass_flow_rate(gamma,P0out,P0in)


