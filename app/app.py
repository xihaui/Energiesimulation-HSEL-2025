import warnings
warnings.filterwarnings("ignore")
# Dash
from dash import Dash, html, dcc, Input, Output, State, callback_context,ctx
from dash.exceptions import PreventUpdate
# Dash community libraries
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
# Data management
import pandas as pd
import numpy as np
import numpy_financial as npf
from bslib import bslib as bsl
from hplib import hplib as hpl
# Plots
import plotly_express as px

from utils.calc_szenarios import calc_kpi
from utils.calc_szenarios import calc_costs_strom
from utils.calc_szenarios import calc_costs_gas
from utils.calc_szenarios import calc_bs_peakshaving


# App configuration
# Icons from iconify, see https://icon-sets.iconify.design

app = Dash(__name__,
          suppress_callback_exceptions=True, 
          external_stylesheets=[dbc.themes.BOOTSTRAP,{'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css','rel': 'stylesheet','integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf','crossorigin': 'anonymous'}],
          meta_tags=[{'name': 'viewport', 'inhalt': 'width=device-width, initial-scale=1'},
          ],
          )
server = app.server

# App configuration
# Icons from iconify, see https://icon-sets.iconify.design

app = Dash(__name__,
          suppress_callback_exceptions=True, 
          external_stylesheets=[dbc.themes.BOOTSTRAP,{'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css','rel': 'stylesheet','integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf','crossorigin': 'anonymous'}],
          meta_tags=[{'name': 'viewport', 'inhalt': 'width=device-width, initial-scale=1'},
          ],
          )
server = app.server

app.title = 'Szenarienvergleich'

wetter_typ=['Jetzt Normal']

button_info = dbc.Button(
    html.Div(id='button_info_content',children=[DashIconify(icon='ph:info',width=50,height=30,),html.Div('Info')]),
    id='button_info',
    outline=False,
    color='light',
    style={'text-transform': 'none',
        'border': 'none',
        'background': 'none',
        'color': 'white',
        'cursor': 'pointer'
    },
)
button_calc1 = dbc.Button(
    html.Div(children=[DashIconify(icon='ph:info',width=50,height=30,),html.Div('Berechne Ausgangssystem')]),
    id='start_calc',
    color='secondary',
    outline=True,
    style={"borderWidth": "2px"}
)

header=dbc.Navbar(
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.Div([
                     html.Img(src="assets/Allgemeines_Logo.ico",)
                    ],
                    )
                ],
                align='center',
                ),
            ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H4('Energiesystem HS-Emden-Leer'),
                    ],
                    id='app-title'
                    )
                ],
                align='left',
                ),
            ]),
        dbc.Row([
            dbc.Col([
                dbc.NavbarToggler(id='navbar-toggler'),
                dbc.Collapse(
                    dbc.Nav([
                        dbc.NavItem(button_info),
                        dcc.ConfirmDialog(id='info_dialog'),
                        ],
                        navbar=True,
                        ),
                    id='navbar-collapse',
                    navbar=True,
                    ),
                ],
                
                ),
            ],
            align='right',
            ),
        ],
        fluid=True,
        ),
    dark=True,
    color='#9cc5ce',
    sticky='top'
    )


container_system=dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("Ausgangssystem"),
                        dbc.Label("PV-Größe Ost(kWp)"),
                        dcc.Slider(min=0,max=500,step=10,id="pv-size-input_east",marks={40: '40 kWp', 500: '500 kWp'} ,persistence='local', tooltip={"placement": "bottom", "always_visible": False}),
                        
                        dbc.Label("PV-Größe Süd(kWp)"),
                        dcc.Slider(min=40,max=1000,step=10,id="pv-size-input_süd",marks={40: '40 kWp', 500: '500 kWp'} ,persistence='local', tooltip={"placement": "bottom", "always_visible": False}),
                        
                        dbc.Label("PV-Größe West(kWp)"),
                        dcc.Slider(min=0,max=500,step=10,id="pv-size-input_west",marks={40: '40 kWp', 500: '500 kWp'} ,persistence='local', tooltip={"placement": "bottom", "always_visible": False}),
                        
                        
                        dbc.Label("Windkraftanlage"),
                         dcc.Dropdown(id='wka-dropdown',
                            options=['Aus', 'Ein'],
                            placeholder='Wähle eine Option', persistence='local'),

                        dbc.Label("BHKW Regelung"),
                        dcc.Dropdown(id='dropdown',
                            options=['Aus', 'An','kurze Sommerabschaltung', 'verlängerte Sommerabschaltung','Lastspitzenkappung', 'stromgeführt', 'bedarfsorientiert'],
                            placeholder='Wähle eine Option', persistence='local'),
                        
                        dbc.Label("Wärmepumpe"),
                        dcc.Dropdown(id='wp',
                            value='Aus',
                            options=[
                                'Aus', 'Luft/Wasser 200', 'Luft/Wasser 400',
                                'Luft/Wasser 688', 'Luft/Wasser 800', 'Luft/Wasser 1000',
                                'Sole/Wasser 200', 'Sole/Wasser 400', 'Sole/Wasser 600',
                                'Sole/Wasser 800', 'Sole/Wasser 1000'],
                            placeholder='Wähle eine Option', persistence='local'),
                            
                        dbc.Label("Wärmebedarfssenkung [%]"),html.Br(),
                        dcc.Input(
                            id='wärmebedarfssenkung',
                            type='number',
                            value=0,  # Beispielwert für die Vorlauftemperatur
                            min=0,
                            max=50,
                            step=5),
                        html.Br(),
                        dbc.Label("Batteriegröße in kWh"),html.Br(),
                        dcc.Slider(min=100,max=1700,step=100,id="bs-size",marks={100: '100 kWh', 1500: '1500 kWh'} ,persistence='local', tooltip={"placement": "bottom", "always_visible": False}),                      
                        html.Br(),
                        html.Br(),
                        button_calc1
                    ],
                    width=6,
                ),
                dbc.Col(html.Div(id='result_df'), width=12)
            ],
        ),
    ],
    fluid=False,
)


layout = html.Div(id='app-page-content',children=[header,html.Br(),container_system])
app.layout=layout


@app.callback(
    Output('result_df', 'children'),
    State('pv-size-input_east', 'value'),
    State('pv-size-input_süd', 'value'),
    State('pv-size-input_west', 'value'),
    State('wka-dropdown', 'value'),
    State('dropdown', 'value'),
    State('wp', 'value'),
    State('wärmebedarfssenkung', 'value'),
    State('bs-size', 'value'),
    Input('start_calc', 'n_clicks')
    )

def calc_system1(pv_east, pv_süd, pv_west, wka, bhkw, wp, wärmebedarfssenkung,bs_size,n):
    if n==None:
        raise PreventUpdate
    effizienz_gastherme=90
    min_cop=1.5
    df=pd.read_csv('Output_data/Eingangsdaten_simulation_2024.csv', index_col=0, decimal=',')
    df = df.apply(pd.to_numeric, errors='coerce')
    df.index=pd.date_range(start='01/01/2022', end='01/01/2023',freq='15min')[0:35040]
    for weather_typ in wetter_typ:
        if weather_typ.startswith('Jetzt'):
            wetter_time='2015'
            emissionen_strom=150/1_000_000
        else:
            wetter_time='2045'
            emissionen_strom=17/1_000_000
        if weather_typ.endswith('l'):
            weather_type='a_'
        elif weather_typ.endswith('t'):
            weather_type='w_'
        elif weather_typ.endswith('m'):
            weather_type='s_'
        weather=pd.read_csv('Input_data/Wetterdaten/TRY_1_'+weather_type+wetter_time+'_15min.csv', index_col=0)
        weather.index=pd.date_range(start='01/01/2022', end='01/01/2023',freq='15min')[0:35040]
        df['PV_Süd [W]']=weather['PV_Süd [W]']
        df['PV_West [W]']=weather['PV_West [W]']
        df['PV_Ost [W]']=weather['PV_Ost [W]']
        df['PV - Vorhanden [W]']=weather['PV - Vorhanden [W]']
        weather_day=weather.resample('D').mean()
        df['Temperatur Luft [°C]']=weather['temperature [degC]']
        for day in weather_day.index:
            df.loc[str(day.date()),'Tages-Durchschnittstemperatur [°C]']=df.loc[str(day.date()),'Temperatur Luft [°C]'].mean()
        df.loc[df['Tages-Durchschnittstemperatur [°C]']>11.1, 'Raumwämebedarf [W]']=0
        df.loc[df['Tages-Durchschnittstemperatur [°C]']<=15, 'Raumwämebedarf [W]']=(15-df.loc[df['Tages-Durchschnittstemperatur [°C]']<=15, 'Temperatur Luft [°C]'])*35910#43733
        df.loc[df['Tages-Durchschnittstemperatur [°C]']<11.1, 'Raumwämebedarf [W]']=(20-df.loc[df['Tages-Durchschnittstemperatur [°C]']<11.1, 'Temperatur Luft [°C]'])*35910+ 140_000#43733 
        #df['Raumwämebedarf [W]']=df['Raumwämebedarf [W]']+df['BHKW Strom [W]']*1.386
        df['Raumwämebedarf [W]']=df['Raumwämebedarf [W]']*(1-wärmebedarfssenkung/100)
        new_df=pd.DataFrame(index=df.index)
        new_df['Stromverbrauch [W]']=df['Gesamtverbrauch Hochschule [W]']#-10000
        new_df['Raumwämebedarf [W]']=df['Raumwämebedarf [W]']
        if wka=='Aus':
            new_df['WKA-Leistung [W]']=0
        else:
            new_df['WKA-Leistung [W]']=df['WKA-Leistung [W]']
        new_df['PV [W]']=(df['PV - Vorhanden [W]']*1000+df['PV_Süd [W]']/143.370*pv_süd+df['PV_Ost [W]']/166.860*pv_east+df['PV_West [W]']/179.820*pv_west)
        if (bhkw=='An'):
            P_el_chp = []
            for timestamp in df.index:
                P_el_chp.append(df.loc[timestamp,'BHKW Strom [W]'])
                #wärmebedarf=df.loc[timestamp,'Raumwämebedarf [W]']
                #if (wärmebedarf > 0):
                #    P_el_chp.append(np.minimum(wärmebedarf, 101_000*1.386)/1.386)
                #else:
                #    P_el_chp.append(0)
            new_df['BHKW Strom [W]']=P_el_chp
        elif (bhkw=='bedarfsorientiert') and (wp=='Aus'):
            P_el_chp = []
            for timestamp in df.index:
                wärmebedarf=df.loc[timestamp,'Raumwämebedarf [W]']
                strombedarf=df.loc[timestamp,'Gesamtverbrauch Hochschule [W]']-new_df.loc[timestamp, 'WKA-Leistung [W]'] - new_df.loc[timestamp, 'PV [W]']
                if (strombedarf> 0) and (wärmebedarf > 0):
                    P_el_chp.append(np.minimum(np.minimum(wärmebedarf, 101_000*1.386)/1.386, strombedarf))
                else:
                    P_el_chp.append(0)
            new_df['BHKW Strom [W]']=P_el_chp
        elif bhkw=='stromgeführt':
            P_el_chp = []
            for timestamp in df.index:
                strombedarf=df.loc[timestamp,'Gesamtverbrauch Hochschule [W]']-new_df.loc[timestamp, 'WKA-Leistung [W]'] - new_df.loc[timestamp, 'PV [W]']
                if (strombedarf > 0):
                    P_el_chp.append(np.minimum(101_000, strombedarf))
                else:
                    P_el_chp.append(0)
            new_df['BHKW Strom [W]']=P_el_chp
        elif bhkw=='Aus':
            new_df['BHKW Strom [W]']=0
        elif (bhkw=='verlängerte Sommerabschaltung'):
            P_el_chp = []
            for timestamp in df.index:
                wärmebedarf=df.loc[timestamp,'Raumwämebedarf [W]']
                if (timestamp > pd.Timestamp('2022-03-15')) & (timestamp < pd.Timestamp('2022-10-09')):
                    P_el_chp.append(0)
                else:
                    P_el_chp.append(101_000)
            new_df['BHKW Strom [W]']=P_el_chp
        elif (bhkw=='kurze Sommerabschaltung'):
            P_el_chp = []
            for timestamp in df.index:
                wärmebedarf=df.loc[timestamp,'Raumwämebedarf [W]']
                if (timestamp > pd.Timestamp('2022-06-04')) & (timestamp < pd.Timestamp('2022-09-15')):
                    P_el_chp.append(0)
                else:
                    P_el_chp.append(101_000)
            new_df['BHKW Strom [W]']=P_el_chp
        elif (bhkw=='Lastspitzenkappung'):
            P_el_chp = []
            for timestamp in df.index:
                strombedarf=df.loc[timestamp,'Gesamtverbrauch Hochschule [W]']-new_df.loc[timestamp, 'WKA-Leistung [W]'] - new_df.loc[timestamp, 'PV [W]']
                #if (timestamp < pd.Timestamp('2022-03-15')) or (timestamp > pd.Timestamp('2022-09-15')):
                #    P_el_chp.append(101_000)
                #else:
                #    P_el_chp.append(0)
                if (strombedarf > 230_000):
                    P_el_chp.append(np.minimum(101_000, strombedarf-230000))
                else:
                    P_el_chp.append(0)
            new_df['BHKW Strom [W]']=P_el_chp
        elif (bhkw=='15.Mai-15.Sept und März bis Oktober 19:00-7:00'):
            P_el_chp = []
            for timestamp in df.index:
                wärmebedarf=df.loc[timestamp,'Raumwämebedarf [W]']
                if (timestamp > pd.Timestamp('2022-06-04')) & (timestamp < pd.Timestamp('2022-09-15')):
                    P_el_chp.append(0)
                elif (timestamp > pd.Timestamp('2022-03-15')) & (timestamp < pd.Timestamp('2022-10-15')):
                    if timestamp.hour >= 19 or timestamp.hour < 7:
                        P_el_chp.append(101_000)
                    else:
                        P_el_chp.append(0)
                else:
                    P_el_chp.append(101_000)
            new_df['BHKW Strom [W]']=P_el_chp
        if wp!='Aus':
            brine=hpl.HeatingSystem()
            if wp.startswith('Luft'):
                group_id=1
            else:
                group_id=5
            P_el_hp = []
            P_th_hp = []
            P_el_chp = []
            heat_pump=hpl.HeatPump(hpl.get_parameters('Generic',group_id,6,55,int(wp.split(' ')[1])*1000))
            
            for timestamp in df.index:
                #print(df.loc[timestamp,'Raumwämebedarf [W]'])#,
                #print((new_df.dtypes))#.loc[timestamp, 'BHKW Strom [W]']))#*1.386)
                try:
                    wärmebedarf=df.loc[timestamp,'Raumwämebedarf [W]']-new_df.loc[timestamp, 'BHKW Strom [W]']*1.386
                    strombedarf=df.loc[timestamp,'Gesamtverbrauch Hochschule [W]'] - new_df.loc[timestamp, 'BHKW Strom [W]']-new_df.loc[timestamp, 'WKA-Leistung [W]'] - new_df.loc[timestamp, 'PV [W]']
                    bhkw_on=1
                except:
                    wärmebedarf=df.loc[timestamp,'Raumwämebedarf [W]']
                    strombedarf=df.loc[timestamp,'Gesamtverbrauch Hochschule [W]']-new_df.loc[timestamp, 'WKA-Leistung [W]'] - new_df.loc[timestamp, 'PV [W]']
                    bhkw_on=0
                if group_id==5:
                    t_in=brine.calc_brine_temp(df.loc[timestamp,'Tages-Durchschnittstemperatur [°C]'])
                else:
                    t_in=df.loc[timestamp,'Temperatur Luft [°C]']
                if wärmebedarf>0:
                    vorlauf_temp=np.maximum(75-2.6*df.loc[timestamp,'Tages-Durchschnittstemperatur [°C]'],36)
                    res=heat_pump.simulate(t_in,vorlauf_temp,df.loc[timestamp,'Temperatur Luft [°C]'])
                    #res['COP']=2.33 + (3.2 - 2.33) * (df.loc[timestamp,'Temperatur Luft [°C]'] +7) / (19)
                    if res['COP']>=min_cop: # Wärmegestehung eigentlich Bedingung ökonomisch zu betrachten (if strompreis/cop < gaspreis/wirkungsgrad brenner :)
                        p_th_hp=np.minimum(wärmebedarf, res['P_th'])
                        p_th_hp=np.minimum(np.maximum((350000-strombedarf)*res['COP'],0),p_th_hp)
                    else:
                        if strombedarf<0: # Überschussstrom zu Wärme
                            p_th_hp=np.minimum(np.minimum(wärmebedarf, strombedarf*-1*res['COP']),res['P_th'])
                        else:
                            p_th_hp=0
                            res['P_el']=0      
                    p_el_hp=p_th_hp/res['COP']
                    p_el_hp_hp_dif=p_el_hp-res['P_el']
                    strombedarf+=p_el_hp
                    wärmebedarf=wärmebedarf-p_th_hp
                else:
                    p_th_hp=0
                    p_el_hp=0
                    p_el_hp_hp_dif=0
                #if (strombedarf+p_el_hp_hp_dif > 0) and (wärmebedarf > 0):
                #    P_el_chp.append(np.minimum(np.minimum(wärmebedarf, 101_000*1.386)/1.386, strombedarf+p_el_hp_hp_dif))
                #    strombedarf=strombedarf-np.minimum(np.minimum(wärmebedarf, 101_000*1.386)/1.386, strombedarf+p_el_hp_hp_dif)
                #    wärmebedarf=wärmebedarf-(np.minimum(np.minimum(wärmebedarf, 101_000*1.386)/1.386, strombedarf+p_el_hp_hp_dif))*1.386
                #    if wärmebedarf>0:
                #        p_el_hp=p_el_hp + np.minimum(p_el_hp_hp_dif*-1, wärmebedarf/res['COP'])
                #        p_th_hp = p_th_hp + np.minimum(p_el_hp_hp_dif*-1*res['COP'], wärmebedarf)
                #else:
                P_el_chp.append(0)
                P_el_hp.append(p_el_hp)
                P_th_hp.append(p_th_hp)
            new_df['Wärmepumpe Strom [W]']=P_el_hp
            new_df['Wärmepumpe Wärme [W]']=P_th_hp
            if bhkw_on==0:
                new_df['BHKW Strom [W]']=P_el_chp
        else:
            new_df['Wärmepumpe Strom [W]']=0
            new_df['Wärmepumpe Wärme [W]']=0
        new_df['BHKW Wärme [W]']=new_df['BHKW Strom [W]']*1.386
        new_df['Gaskessel [W]'] = new_df['Raumwämebedarf [W]']-new_df['BHKW Wärme [W]']-new_df['Wärmepumpe Wärme [W]']
        new_df.loc[new_df['Gaskessel [W]']<0,'Gaskessel [W]']=0
        new_df['Gasverbrauch [W]'] = new_df['Gaskessel [W]']/(90/100) + new_df['BHKW Strom [W]']/0.3232
        new_df['Stromproduktion']=new_df['BHKW Strom [W]']+new_df['PV [W]']+new_df['WKA-Leistung [W]']
        new_df['p_diff']=new_df['Stromproduktion']-new_df['Stromverbrauch [W]']-new_df['Wärmepumpe Strom [W]']
        p_el_max, E_ne, E_nb, E_gas,p_gas_max=calc_kpi(new_df['Stromverbrauch [W]']+new_df['Wärmepumpe Strom [W]'],new_df['Stromproduktion'],new_df['Gasverbrauch [W]'])
        print('Normal: ',calc_costs_strom(p_el_max,E_nb,E_ne)+calc_costs_gas(p_gas_max,E_gas,new_df['BHKW Strom [W]'].mean()*8.76/101))
        peak_shaving, P_gs_peak_shaving=calc_bs_peakshaving((new_df['Stromverbrauch [W]']+new_df['Wärmepumpe Strom [W]']-new_df['Stromproduktion'])/1000, bs_size)
        print('Peak_shaving: ',calc_costs_strom(peak_shaving['P_gs_max'],E_nb,E_ne)+calc_costs_gas(p_gas_max,E_gas,new_df['BHKW Strom [W]'].mean()*8.76/101))
        BAT_soc = []
        BAT_P_bs = []
        BAT = bsl.ACBatMod(system_id='SG1',
            p_inv_custom=bs_size*1000,
            e_bat_custom=bs_size)
        res = BAT.simulate(p_load=0, soc=0, dt=900)
        for p_diff in new_df['p_diff'].values:
            res = BAT.simulate(p_load=p_diff, soc=res[2], dt=900)
            BAT_soc.append(res[2])
            BAT_P_bs.append(res[0])
        BAT_soc=np.asarray(BAT_soc)
        BAT_P_bs=np.asarray(BAT_P_bs)
        new_df['SOC']=BAT_soc
        new_df['P_gs'] = -np.minimum(0, (new_df['p_diff'].values-BAT_P_bs))
        new_df['P_gf'] = np.maximum(0, (new_df['p_diff'].values-BAT_P_bs))
        p_el_max_bat, E_ne_bat, E_nb_bat = new_df['P_gs'].max()/1000,new_df['P_gf'].mean()*8.76,new_df['P_gs'].mean()*8.76
        print('Autarkie: ',calc_costs_strom(p_el_max_bat,E_nb_bat,E_ne_bat)+calc_costs_gas(p_gas_max,E_gas,new_df['BHKW Strom [W]'].mean()*8.76/101))
        new_df['P_gs_peak_shaving']=P_gs_peak_shaving*1000
        fig=px.line(new_df, title='Gesamtkosten: '+ str(round(calc_costs_strom(p_el_max, E_nb,E_ne)+calc_costs_gas(p_gas_max,E_gas,new_df['BHKW Strom [W]'].mean()*8.76/101))) + '; Mit Batteriespeicher: '+ str(round(calc_costs_strom(peak_shaving['P_gs_max'], E_nb_bat,E_ne_bat)+calc_costs_gas(p_gas_max,E_gas, new_df['BHKW Strom [W]'].mean()*8.76/101))))
        
        #new_df.to_csv('Peak_shaving.csv')
        #new_df3.to_csv('2g_gasdaten.csv')
        #new_df3 = new_df.resample('H').mean()
        #new_df3 = new_df3.resample('M').sum()
        
        #new_df3.to_csv('2g_gasdaten.csv')
        start_date = "2022-03-15"
        end_date = "2022-03-30"

        # Filter für den Datumsbereich (nur Monat und Tag)
        #df_filtered = new_df[(new_df.index > start_date) & (new_df.index < end_date)]
        # Werte um genau 09:00 Uhr filtern
        #df_9am = df_filtered[df_filtered.index.time == pd.to_datetime("10:00").time()]

        # Den niedrigsten Wert um 09:00 Uhr ermitteln
        #print(df_9am['PV [W]'].quantile(0.1))
    return html.Div([dcc.Graph(figure=fig), ' Volllaststunden: ',round(E_nb/p_el_max), 'mit Batterie: ', round(E_nb_bat/p_el_max_bat), ' CO2-Emissionen: ', round((E_nb_bat*0.323+E_gas*0.18139-E_ne_bat*0.323)/1000), ' Netzbezug: ', round(E_nb_bat), 'Spitzenlast: ', round(p_el_max), 'mit Spitzenlastkappung: ', peak_shaving['P_gs_max'], 'Netzeinspeisung: ', round(E_ne_bat), 'Gasbezug: ', round(E_gas)])

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
