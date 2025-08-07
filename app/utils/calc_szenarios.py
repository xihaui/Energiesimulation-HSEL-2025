import numpy as np
import pandas as pd

def calc_kpi(p_consumtion, p_production, p_gas):
    p_dif=p_production-p_consumtion
    p_gridfeed = np.maximum(0,p_dif)
    p_gridsupply = np.minimum(0,p_dif)
    return-p_dif.min()/1000, p_gridfeed.mean()*8.76, -p_gridsupply.mean()*8.76, p_gas.mean()*8.76, p_gas.max()/1000 # maximaler Netzbezug in kW , Netzeinspeisung [kWh], Netzbezug [kWh], Gasbezug [kWh], Leistung gas[kW]
# Calculation of electrical grid supply KPIs
def calc_gs_kpi(P_gs):
    # to DataFrame
    profile = pd.DataFrame()
    profile['P_gs'] = P_gs
    # grid supply in kWh
    E_gs = round(profile['P_gs'].mean() * 8760,0)    # kWh
    # peak load
    P_gs_max = round(profile['P_gs'].max(),1)        # kW
    # annual utilization time
    t_util_a = round(E_gs / P_gs_max,0)              # h
    return E_gs, P_gs_max, t_util_a

def calc_costs_strom(p_el_max, E_nb, E_ne):
    if E_nb>1000000:
        energiekosten=E_nb*(0.164797-0.0158)+1000000*0.0158#2025:(0.098031+0.0011+0.0205+0.00277+0.00816)+1000000*0.0158
    else:
        energiekosten=E_nb*0.164797#(0.098031+0.0011+0.0205+0.00277+0.00816+0.0158)
    if E_nb/p_el_max<2500:
        netzkosten=E_nb*0.0725+p_el_max*26.62
    else:
        netzkosten=E_nb*0.0093+p_el_max*184.6
    return (netzkosten+energiekosten)*1.19 #- E_ne*0.062
def calc_costs_gas(p_gas_max, E_gas, volllaststunden_bhkw):
    energiekosten=E_gas*(6.576)/100#2025:(5.5+1.0012+0.55+0.299)/100
    if E_gas<1_500_000:
        netzkosten=E_gas*0.00595
    elif E_gas<2_000_000:
        netzkosten=8925+(E_gas-1_5000_000)*0.0055
    elif E_gas<3_000_000:
        netzkosten=11625+(E_gas-2_000_000)*0.00526
    elif E_gas<4_000_000:
        netzkosten=16935+(E_gas-3_000_000)*0.00499
    elif E_gas<5_000_000:
        netzkosten=21925+(E_gas-4_000_000)*0.00477
    elif E_gas<10_000_000:
        netzkosten=26695+(E_gas-5_000_000)*0.00439
    
    if p_gas_max<800:
        leistungskosten=p_gas_max*22.019
    elif p_gas_max<1000:
        leistungskosten=17615.2+(p_gas_max-800)*20.443
    elif p_gas_max<1500:
        leistungskosten=21703.8+(p_gas_max-1_000)*19.645
    elif p_gas_max<1900:
        leistungskosten=31526.3+(p_gas_max-1500)*18.673
    elif p_gas_max<2200:
        leistungskosten=38995.5+(p_gas_max-1900)*18.009
    elif p_gas_max<4100:
        leistungskosten=44398.2+(p_gas_max-2200)*16.687
    
    netzkosten=netzkosten+leistungskosten
    bhkw_wartungskosten=volllaststunden_bhkw*2.5
    bhkw_steuererstattung=volllaststunden_bhkw*101/0.3232*0.0055
    return (netzkosten+energiekosten+230+bhkw_wartungskosten)*1.19 #- bhkw_steuererstattung
def calc_bs_peakshaving(P_gs0, bs_size_max):
    # Start KPIs
    E_gs0, P_gs_max0, t_util0 = calc_gs_kpi(P_gs0)
    # General Parameters
    dt = 900
    eta_bat=0.95
    eta_bat2ac = 0.95
    eta_ac2bat = 0.95
    # DataFrames
    df = pd.DataFrame({'P_bs_discharge_max': [],
                        'P_bs_charge_max': [],
                        'C_bs': [],
                        'E_gs': [],
                        'P_gs_max': [],
                        'delta_P_gs': [],
                        't_util': [],
                        'E_rate': [],
                        'E_bs_charge_ac': [],
                        'E_bs_discharge_ac': [],
                        'N_full_cylces': []})
    df.loc[0] = [0, 0, 0, E_gs0, P_gs_max0, 0, t_util0, 0, 0, 0, 0]
    # Start values
    delta_P_gs_rel = 0.1
    E_rate = 5
    j = 0
    C_bs=0
    # Iteration
    while C_bs <= bs_size_max:
        j = j + 1
        # add 1% of peak shaving 
        delta_P_gs_rel = delta_P_gs_rel + 0.01     # %
        delta_P_gs = P_gs_max0 * delta_P_gs_rel     # kW
        P_gs_max = P_gs_max0 - delta_P_gs           # kW
        # calculate battery discharge and grid supply
        P_bs_discharge = P_gs0 - P_gs_max           # kW
        P_bs_discharge[P_bs_discharge < 0] = 0      # kW
        P_bs_charge = P_gs_max - P_gs0              # kW
        P_bs_charge[P_bs_charge < 0] = 0            # kW
        P_bs_set = P_bs_discharge - P_bs_charge
        # Energies
        E_bs_discharge = [int(P_bs_discharge.iloc[0])]   # kWh
        for i in range(1,len(P_bs_discharge)):
            if P_bs_discharge[i] == 0:
                if E_bs_discharge[i-1]>0:
                    E_bs_discharge.append(E_bs_discharge[i-1] - np.minimum(P_bs_charge[i],delta_P_gs)*0.25*eta_ac2bat*eta_bat2ac*eta_bat)
                else:
                    E_bs_discharge.append(0)
            else:
                if E_bs_discharge[i-1]<0:
                    E_bs_discharge.append(P_bs_discharge[i] * 0.25)
                else:
                    E_bs_discharge.append(E_bs_discharge[i-1] + P_bs_discharge[i] * 0.25)
        # Find maximum discharge period in year
        E_bs_discharge_max = max(E_bs_discharge)
        # Calculate battery capacity and KPIs
        C_bs = E_bs_discharge_max / ((eta_bat+((1-eta_bat)/2))*eta_bat2ac*0.8)
        E_rate = (delta_P_gs / eta_bat2ac) / (C_bs)
        # Calculate battery charge and soc
        P_bs = [0]
        P_bat = [0]
        SOC = [1]
        for i in range(1,len(P_bs_set)):
            if P_bs_set[i] >= 0 and SOC[i-1] > 0.2: # Entladen
                P_bs.append(P_bs_set[i])
                P_bat.append(P_bs[i] / ((eta_bat+((1-eta_bat)/2))*eta_bat2ac))
                SOC.append(SOC[i-1] - (P_bat[i] * 0.25 / C_bs))
            elif P_bs_set[i] < 0 and SOC[i-1] < 1:  # Laden
                P_bs.append((max(P_bs_set[i], delta_P_gs*-1)))
                P_bat.append(P_bs[i] * ((eta_bat+((1-eta_bat)/2))*eta_ac2bat))
                SOC.append(SOC[i-1] - (P_bat[i] * 0.25 / C_bs))
            else:
                P_bs.append(0)
                P_bat.append(0)
                SOC.append(SOC[i-1])
            if SOC[i] > 1:                          # soc correction overload
                delta_SOC = SOC[i] - 1
                delta_P = delta_SOC * C_bs / 0.25
                P_bs[i] = P_bs[i] + delta_P
                P_bat[i] = P_bs[i] * ((eta_bat+((1-eta_bat)/2))*eta_ac2bat)
                SOC[i] = 1
            if SOC[i] < 0.2:                        # soc correction deep discharge
                delta_SOC = 0.2 - SOC[i]
                delta_P = delta_SOC * C_bs / 0.25
                P_bs[i] = P_bs[i] - delta_P
                P_bat[i] = P_bs[i] / ((eta_bat+((1-eta_bat)/2))*eta_bat2ac)
                SOC[i] = 0.2
        # Grid supply
        P_gs = P_gs0 - P_bs
        E_gs, P_gs_max, t_util = calc_gs_kpi(P_gs)
        # Battery
        data = pd.DataFrame()
        data['P_bs_charge'] = P_bs
        data['P_bs_charge'][data['P_bs_charge']>0] = 0
        E_bs_charge = data['P_bs_charge'].abs().mean()*8760
        data['P_bs_discharge'] = P_bs
        data['P_bs_discharge'][data['P_bs_discharge']<0] = 0
        E_bs_discharge = data['P_bs_discharge'].mean()*8760
        data['P_bs_charge_dc'] = P_bat
        data['P_bs_charge_dc'][data['P_bs_charge_dc']>0] = 0
        E_bs_charge_dc = data['P_bs_charge_dc'].abs().mean()*8760
        data['P_bs_discharge_dc'] = P_bat
        data['P_bs_discharge_dc'][data['P_bs_discharge_dc']<0] = 0
        E_bs_discharge_dc = data['P_bs_discharge_dc'].mean()*8760
        N_full_cylces = (E_bs_charge_dc + E_bs_discharge_dc)/(2*C_bs) 

        df.loc[j] = [round(max(P_bs),1), 
                    round(-1*min(P_bs),1),
                    round(C_bs,1), 
                    round(E_gs,0), 
                    round(P_gs_max,1), 
                    round(P_gs_max0-P_gs_max,1), 
                    round(t_util,0), 
                    round(E_rate,2),
                    round(E_bs_charge,1),
                    round(E_bs_discharge,1),
                    round(N_full_cylces,1)
                    ]
    return df.iloc[j,:], P_gs
