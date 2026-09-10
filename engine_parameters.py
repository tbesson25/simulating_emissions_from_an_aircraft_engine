#ENGINE

#COMMON PARAMETERS
R = 287.0                 # J/(kg K)
LCV = 43e6                # J/kg 
QR = 43e6                 # J/kg QR=LCV (kept for simplicity)

# Component efficiencies /
etaD = 0.97
etaF = 0.85
etaC = 0.85
etaT = 0.90
etaBN = 0.85
etaN = 0.98

etaPC = 0.9
etaPT = 0.9

# Gas properties
gammaD = 1.40
gammaF = 1.40
gammaC = 1.37
gammaB = 1.35 #burner
gammaT = 1.33
gammaN = 1.36
'''
gammaC =1.4
gammaT=1.3
gammaN=1.3'''

# Specific heats
Cp = gammaD / (gammaD - 1) * R
Cpf = gammaF / (gammaF - 1) * R
Cpc = gammaC / (gammaC - 1) * R
Cpb = gammaB / (gammaB - 1) * R
Cpt = gammaT / (gammaT - 1) * R
Cpn = gammaN / (gammaN - 1) * R

#distingue engines
def define_engine(
    BPR,
    CPR,
    FPR,
    FBPR,
    D,
    design_thrust,
):

    # Calculate pressure ratios
    HPCPR = CPR / FBPR
    #FPR = 1.5   # if kept fixed for all engines

    # Fan area
    A = 3.14159265 * (D / 2)**2

    engine = {

        # Common model parameters
        "etaD": etaD,
        "etaF": etaF,
        "etaC": etaC,
        "etaT": etaT,
        "etaN": etaN,
        "etaBN": etaBN,
        "etaPC": etaPC,
        "etaPT": etaPT,

        "gammaD": gammaD,
        "gammaF": gammaF,
        "gammaC": gammaC,
        "gammaB": gammaB,
        "gammaT": gammaT,
        "gammaN": gammaN,

        "Cp": Cp,
        "Cpf": Cpf,
        "Cpc": Cpc,
        "Cpb": Cpb,
        "Cpt": Cpt,
        "Cpn": Cpn,

        "R": R,
        "LCV": LCV,
        "QR": QR,

        # Engine-specific parameters
        "BPR": BPR,
        "CPR": CPR,
        "HPCPR": HPCPR,
        "FBPR": FBPR,
        "FPR": FPR,

        "D": D,
        "A": A,

        "design_thrust": design_thrust,
    }

    return engine

#CFM56-7B20E
CFM56_engine = define_engine(
    BPR=5.5,
    CPR=22.4,
    FPR=1.5,
    FBPR=2.5,
    D=1.55,
    design_thrust=91630,
) 

#CFM56-5B1/3
CFM56_5B_engine = define_engine(
    BPR=5.5,
    CPR=30.2,
    FPR=1.5,
    FBPR=2,
    D=1.73482,
    design_thrust=133400,
) 

#GE90-115B
GE90_115B_engine = define_engine(
    BPR=7,
    CPR=43.2,
    FPR=1.5,
    FBPR=2,
    D= 3.25,
    design_thrust=513900,
) 

#PW307A
PW307A_engine = define_engine(
    BPR=4.2,
    CPR=20.2,
    FPR=1.358,
    FBPR=2,
    D=1.0414,
    design_thrust=28500,
) 

#
TRENT970_84_engine = define_engine(
    BPR=7.5,
    CPR=39,
    FPR=1.5,
    FBPR=2.1,
    D=2.95,
    design_thrust=334700,
) 

#AS907-1-1A #out of production
AS907_1_1A_engine = define_engine(
    BPR=4.2,
    CPR=22,
    FPR=1.4,
    FBPR=2.5,
    D=0.9,
    design_thrust=33600,
) 

#JT3D-7 #out of production
JT3D_7_engine = define_engine(
    BPR=1.4,
    CPR=13.3,
    FBPR=2.5,
    FPR=1.5,
    D=1.3,
    design_thrust=84500,
) 

#M45H-01 #out of production
M45H_01_engine = define_engine(
    BPR=3,
    CPR=16.5,
    FPR=1.247,
    FBPR=2,
    D=0.909,
    design_thrust=32400,
) 