## Ausgangsdaten

- Die Ausgangsdaten zeigen, die wichtigsten energetischen Daten, welche aus der Simulation erzeugt wurden.
- Folgende Parameter sind in der Tabelle vorhanden:

| Zeilen| Bedeutung                                                | Werte|
|---------------------------|----------------------------------------------------------------|-|
| Windkraftanlage_options   | Optionen für Windkraftanlagen auf dem Campus                  |Aus, Ein|
| Bhkw_options              | Optionen für das Blockheizkraftwerk auf dem Campus             |Aus, Ein, bedarfsorientierte Regelung|
| Pv_options                | Optionen für Photovoltaikanlagen auf dem Campus                |40 kWp, 500 kWp, 1000 kWp, 1500 kWp|
| Waermepumpe_options        | Optionen für Wärmepumpen auf dem Campus                         | Aus, Luft/Wasser 200 bis Luft/Wasser 1000, Sole/Wasser 200 bis Sole/Wasser 1000|
| Gastherme_options         | Optionen für Gasthermen auf dem Campus                         |Normal weiter, Sauerstoffregelung|
| Waermebedarfssenkung_options | Optionen zur Senkung des Wärmebedarfs auf dem Campus          |0%|
| Vorlauf_temp_options      | Optionen für die Vorlauftemperatur für Heizsysteme             |0, 45, 55, 65, 75|
| Wetter_typ                | Art des simulierten Wetters                                    |bis 2030/ab 2030 mit jeweils extremer Winter, extremer Sommer oder normalem Wetter|
| Netzbezug                 | Strombezug vom Netz                                           | in kWh|
| Netzeinspeisung           | Strom, der ins Netz eingespeist wird                           |in kWh|
| Gasbezug                 | Gasbezug für Wärmebereitstellung                               |in kWh|
| max_gas                   | Maximale Gasmengen                                            |in kW|
| max_p_el                  | Maximale elektrische Leistung des Blockheizkraftwerks (BHKW)   |in kW|
| Volllaststunden_bhkw      | Anzahl der Volllaststunden des Blockheizkraftwerks (BHKW)      |in h|
| Cop                       | Leistungszahl (COP) der Wärmepumpe                            ||
| Stromproduktion           | Produzierte Strommenge                                        |in kWh|
| Stromverbrauch_hp         | Stromverbrauch der Wärmepumpe                                 |in kWh|
