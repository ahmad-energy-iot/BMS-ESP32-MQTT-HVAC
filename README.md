BMS / HVAC Automation with ESP32 and MQTT
ESP32 · DHT11 · Raspberry Pi · Node-RED · MQTT · Modbus TCP · FlowFuse Dashboard
Deutsch · English
🇩🇪 Deutsch
Überblick
Dieses praktische Gebäudeautomationsprojekt verbindet reale Temperatur- und Feuchtemessung mit einer BMS-/HVAC-Steuerung in Node-RED. Ein ESP32 liest einen DHT11 aus und überträgt die Messwerte per MQTT an einen Raspberry Pi. Node-RED verarbeitet die Daten, berechnet den Kühlbedarf und sendet Befehle für einen realen Lüfter über ein Relais sowie für eine LED, die ein Kühlventil repräsentiert.
Das Projekt baut auf Mini-BMS-HVAC-Automation auf. Es wird als eigenständiges Praxisprojekt dokumentiert, weil es den bisherigen Modbus-Simulationsaufbau um reale Sensorik, MQTT-Kommunikation, ESP32-Ausgänge, Feuchtevisualisierung, Alarmhistorie und Energieabschätzung erweitert.
Es handelt sich um einen Lern- und Demonstrationsaufbau, nicht um eine freigegebene Steuerung für eine produktive HVAC-Anlage.
Hauptfunktionen
- Reale Temperatur- und Feuchtemessung mit DHT11 und ESP32.
- MQTT-Messwertübertragung im Abstand von etwa zwei Sekunden.
- Temperatur-Sollwert über ein simuliertes Modbus Holding Register.
- Kühlregelung mit einer Hysterese von ±1 °C.
- AUTO- und MANUAL-Betrieb.
- Lüfterbefehl per MQTT und Relaisansteuerung am ESP32.
- Simulierte Lüfterrückmeldung über Modbus Discrete Input.
- Lüfteralarm bei ausbleibender Rückmeldung nach fünf Sekunden.
- Temperaturdaten-Watchdog mit fünf Sekunden Timeout.
- Virtuelle Kühlventillogik mit LED-Anzeige am ESP32.
- Historie der letzten drei Lüfteralarme mit Kommen-/Gehen-Zeit.
- Akkumulierte Lüfterbefehlsdauer mit dateibasiertem Context Store.
- Energieabschätzung mit einer angenommenen Leistung von 2 W.
- Zwei Live-Charts: Temperatur/Sollwert und relative Luftfeuchtigkeit.
- WiFi-/MQTT-Wiederverbindung und Abschaltlogik im ESP32-Code.
Systemarchitektur
Bereich	Datenweg	Aufgabe
Messung	DHT11 → ESP32 → MQTT → Node-RED	Reale Temperatur und relative Luftfeuchtigkeit
Regelung	Temperatur + Sollwert → Hysterese → AUTO/MANUAL	Lüfterbefehl berechnen
Lüfter	Node-RED → MQTT → ESP32 GPIO23 → Relais → Lüfter	Reale Ausgangsansteuerung
Rückmeldung	Modbus-Simulation → Node-RED	Simuliertes Fan Feedback für Überwachung und Tests
Kühlventil	Kühlbedarf + Lüfterbefehl + Feedback → MQTT → GPIO26	LED repräsentiert den Ventilbefehl
Überwachung	Zustände → Alarm, Historie, Befehlsdauer, Energieabschätzung	Diagnose und Visualisierung
Bedienung	Node-RED Inject-Nodes + FlowFuse Dashboard	Testbefehle im Editor, Anzeigen im Dashboard


Der primäre Temperaturpfad verwendet MQTT. Die Modbus-Temperatursimulation bleibt im Export erhalten, ist aber nicht als zweite Regelungsquelle angeschlossen. Modbus wird weiterhin für Sollwert, Lüfterbefehl und simulierte Rückmeldung verwendet.
Technologien und Hardware
Komponente	Verwendung
ESP32 mit MicroPython	Sensorabfrage, MQTT-Kommunikation, Ausgangsansteuerung
DHT11	Temperatur und relative Luftfeuchtigkeit
Relais, Active LOW	Lüfter schalten
Lüfter	Realer Aktor im Versuchsaufbau
LED mit Vorwiderstand	Darstellung eines virtuellen Kühlventils
Raspberry Pi	Node-RED, MQTT-Broker und Modbus-Simulation
Node-RED / JavaScript	Datenprüfung, Regelung, Zustände und Überwachung
MQTT / umqtt.simple	Messwerte und Ausgangsbefehle
node-red-contrib-modbus	Modbus-TCP-Client und Simulationsserver
FlowFuse Dashboard	Trends, Statusanzeigen und Alarmtabelle
Thonny	MicroPython-Dateien auf dem ESP32 bearbeiten
GitHub	Quellcode und Projektdokumentation


Im exportierten Flow sind folgende Paketversionen vermerkt:
- node-red-contrib-modbus: 5.60.2
- @flowfuse/node-red-dashboard: 1.32.0
Dies sind die Versionen des Exports, keine Aussage über die jeweils neueste verfügbare Version.
GPIO-Belegung
GPIO	Komponente	Verhalten
4	DHT11-Datensignal	Temperatur und Feuchte lesen
23	Relais IN2 für den Lüfter	LOW = EIN, HIGH = AUS
26	LED mit Vorwiderstand	HIGH = Ventilbefehl EIN, LOW = AUS


Beim Programmstart wird das Lüfterrelais auf HIGH und die Ventil-LED auf LOW gesetzt.
MQTT-Kommunikation
Topic	Richtung	Payload
bms/room1/temperature	ESP32 → Node-RED	Temperatur in °C als numerischer Text
bms/room1/humidity	ESP32 → Node-RED	Relative Luftfeuchtigkeit in % als numerischer Text
bms/room1/fan/command	Node-RED → ESP32	ON oder OFF
bms/room1/valve/command	Node-RED → ESP32	ON oder OFF


Der ESP32 verwendet die LAN-Adresse des Raspberry Pi als Brokeradresse. Node-RED verwendet im Export 127.0.0.1:1883. Die Brokeradresse muss an das eigene Netzwerk angepasst werden.
Die Sensor-Publikationen im ESP32-Code sind nicht retained. Die Ausgangsbefehle werden im Flow mit QoS 0 gesendet; es ist kein retained Ausgangsbefehl eingestellt. Der Aufbau verwendet MQTT auf Port 1883 ohne TLS. Zugangsdaten gehören in die lokale Konfiguration und nicht in das öffentliche Repository.
Modbus Mapping
Signal	Modbus-Typ	Function Code	Adresse	Bedeutung im aktuellen Aufbau
Simulierte Temperatur	Input Register	FC4	0	Verbleibender Simulations-/Debugpfad
Temperatur-Sollwert	Holding Register	FC3 / FC6	0	Sollwert lesen und schreiben
Lüfterbefehl	Coil	FC1 / FC5	0	Befehl im Modbus-Modell abbilden
Lüfterrückmeldung	Discrete Input	FC2	0	Simulierte Rückmeldung


Client-Konfiguration: Host 127.0.0.1, Port 10502, Unit ID 1. Der Simulationsserver ist im Export an 0.0.0.0 gebunden. Die Modbus-Lesezyklen sind auf eine Sekunde eingestellt.
Temperatur und Skalierung
Die reale MQTT-Temperatur wird bereits in °C übertragen und benötigt keine Division durch zehn. Die MQTT-Temperaturprüfung erwartet einen endlichen numerischen Payload; der MQTT-Eingang verwendet Auto-Detect.
Modbus-Werte werden dagegen mit dem Faktor zehn gespeichert:
Physikalischer Wert	Modbus-Rohwert
23.0 °C	230
24.6 °C	246


Der Sollwert wird vor dem Schreiben mit zehn multipliziert und nach dem Lesen mit 0,1 skaliert. Leere, nicht endliche und nullwertige Registerdaten werden beim Sollwertlesen verworfen. Ein Start-Inject schreibt nach fünf Sekunden den Sollwert 23 °C; ein späteres Deploy kann diesen erneut auslösen.
Die Feuchteprüfung wandelt den Payload in eine Zahl um und verwirft nicht endliche Werte sowie Werte außerhalb 0–100 %. Sie ersetzt keine vollständige Sensorplausibilitätsprüfung.
Hysterese-Regelung
Bei einem Sollwert von 23 °C gelten:
Temperatur	Kühlbedarf
≥ 24 °C	EIN
≤ 22 °C	AUS
Zwischen 22 und 24 °C	Vorherigen Zustand beibehalten


Der Flow speichert den Kühlzustand im Flow Context. Die Hysterese verhindert häufiges Umschalten nahe am Sollwert. Der DHT11 liefert nur grobe Messwerte; der Aufbau ist keine präzise Raumklimaregelung.
AUTO / MANUAL
AUTO
Der Lüfterbefehl folgt dem berechneten Kühlbedarf. Bei einem Temperaturdaten-Timeout setzt die Logik den Lüfterbefehl im AUTO-Modus auf AUS.
MANUAL
Die Inject-Nodes MANUAL Mode, Manual Fan ON und Manual Fan OFF ermöglichen manuelle Testbefehle im Node-RED-Editor. Der exportierte Flow enthält dafür keine Dashboard-Schalter.
Die Inject-Nodes ändern den Flow Context. Die Auswertung erfolgt bei der nächsten Nachricht durch die Regelungs-/Alarmlogik, normalerweise beim nächsten Temperaturwert. Im MANUAL-Modus bleibt der manuelle Lüfterbefehl auch bei einem Temperaturdaten-Timeout maßgeblich. Das virtuelle Ventil wird bei einem solchen Timeout geschlossen.
Die Startwerte der Logik sind AUTO und manueller Lüfterbefehl AUS, falls keine Context-Werte vorhanden sind.
Command und Feedback
Command beschreibt den gewünschten Zustand; Feedback soll eine Rückmeldung über den Gerätezustand darstellen.
Fan Command	Fan Feedback	Interpretation
ON	ON	Befehl und simulierte Rückmeldung stimmen überein
ON	OFF	Anlaufüberwachung, anschließend möglicher Lüfteralarm
OFF	OFF	Kein Einschaltbefehl
OFF	ON	Im aktuellen Flow kein eigener Alarm für diese Abweichung


Die Rückmeldung stammt hier aus der Modbus-Simulation. Es gibt keinen angeschlossenen Drehzahlsensor und keine physische Rückmeldeleitung vom Lüfter. Die Anzeige beweist deshalb nicht, dass der reale Lüfter tatsächlich läuft.
Für die Tests werden Fan Feedback ON und Fan Feedback OFF verwendet. Die ebenfalls vorhandenen Fan Healthy-/Fan Fault-Nodes setzen eine separate Variable, die die aktuelle Alarmlogik nicht auswertet.
Alarmüberwachung und Alarmhistorie
Wenn der Lüfterbefehl EIN ist und die simulierte Rückmeldung AUS bleibt, startet eine Überwachungszeit von fünf Sekunden. Bei weiteren Auswertungen nach Ablauf dieser Zeit wird der Lüfteralarm aktiv. Während der Wartezeit ist fanStartPending gesetzt.
Wird die Rückmeldung EIN oder der Lüfterbefehl AUS, endet die Alarmbedingung und die Zeitüberwachung wird zurückgesetzt. Der Alarm schaltet den Lüfterbefehl im aktuellen Flow nicht automatisch ab.
Die Historie enthält höchstens drei Alarmdatensätze:
Feld	Inhalt
raisedAt	Zeitpunkt des Alarmbeginns
clearedAt	Zeitpunkt des Alarmendes
status	AKTIV oder GEGANGEN
text	Beschreibung des fehlenden Lüfterfeedbacks


Zeitstempel verwenden Europe/Berlin und deutsches Datumsformat. Ein anhaltender Alarm erzeugt keine wiederholten neuen Einträge. Beim Ende wird der vorhandene aktive Eintrag aktualisiert. Es gibt keine separate Bedienerquittierung.
Temperaturdaten-Watchdog und ESP32-Verhalten
Node-RED erwartet regelmäßig gültige Temperaturdaten. Nach fünf Sekunden ohne Nachricht im Watchdog-Pfad erscheint eine Warnung; zusätzlich wird die Regelungslogik mit dataTimeout = true aufgerufen.
Der ESP32-Code enthält:
- Sensorabfrage alle 2.000 ms.
- WiFi-Verbindungsversuch mit 20 Sekunden Timeout.
- Wiederholungsversuche mit etwa fünf Sekunden Pause.
- MQTT-Abonnements für Lüfter und Ventil.
- Abschalten beider Ausgänge beim Schließen der MQTT-Verbindung.
- Abschalten des jeweiligen Ausgangs bei ungültigem Befehl.
- Separate Befehls-Timeouts von 10.000 ms für Lüfter und Ventil.
- Abschalten und Verbindungsabschluss bei manuellem Programmstopp.
Die Befehls-Timeouts werden in der Hauptschleife geprüft. Blockierende Netzwerkaufrufe können die Reaktion verzögern; dies ist kein unabhängiger Hardware-Watchdog und keine garantierte Abschaltzeit.
Bei einem DHT11-Lesefehler werden keine neuen Messwerte publiziert; der Code versucht einen MQTT-Ping. Der Node-RED-Temperaturwatchdog kann dadurch fehlende Temperaturdaten erkennen. Für Feuchtedaten existiert kein eigener Timeout-Watchdog.
Kühlventil
Das virtuelle Kühlventil wird nur freigegeben, wenn gleichzeitig:
- kein Temperaturdaten-Timeout vorliegt,
- Kühlbedarf besteht,
- der Lüfterbefehl EIN ist,
- die simulierte Lüfterrückmeldung EIN ist.
Node-RED sendet den daraus abgeleiteten Befehl per MQTT an GPIO26. Die LED zeigt den Ventilbefehl; es gibt weder ein reales Ventil noch eine Ventilpositionsrückmeldung.
Befehlsdauer, Persistenz und Energieabschätzung
Fan Command Runtime
Der Zähler akkumuliert Zeit, während der vorherige Lüfterbefehl EIN war. Zeitabstände von mehr als fünf Sekunden werden nicht angerechnet, damit lange Kommunikations- oder Neustartlücken nicht einfach als Laufzeit gezählt werden.
Der Gesamtwert wird über context.get/set(..., "file") gespeichert. Zeitmarke und vorheriger Befehl bleiben im Standard-Context. Dies ist Befehlsdauer, keine gemessene mechanische Lüfterlaufzeit.
Dateibasierter Context Store
Der Flow-Export enthält nicht die Node-RED-settings.js. Für Alarmhistorie und Gesamtzeit muss ein Store namens file konfiguriert sein. Beispiel innerhalb der vorhandenen Settings-Konfiguration:
contextStorage: {
    default: "memoryOnly",
    memoryOnly: { module: "memory" },
    file: { module: "localfilesystem" }
},
Danach Node-RED neu starten. Die vorhandene Settings-Datei wird dabei ergänzt, nicht vollständig ersetzt. Schreibvorgänge können gepuffert sein; ein unerwarteter Stromausfall kann zuletzt noch nicht geschriebene Werte verlieren.
Energieabschätzung
Geschätzte Energie (Wh) = Lüfterbefehlsdauer (h) × 2 W
Eine Stunde Befehlsdauer ergibt rechnerisch 2 Wh. Die Leistung von 2 W ist eine Lernannahme. Es gibt keinen Strom-, Spannungs- oder Leistungssensor; die Anzeige ist kein gemessener Verbrauch. Eine fehlerhafte oder simulierte Rückmeldung verändert diese Berechnungsgrundlage nicht.
Dashboard
Das Dashboard verwendet die Gruppe Raumüberwachung und zeigt:
- Temperatur und Sollwert in einem gemeinsamen Trend.
- Relative Luftfeuchtigkeit als Wert und als separaten Trend.
- Temperaturdaten-Status.
- Fan Command und simuliertes Fan Feedback.
- Alarm Status.
- Kühlventil Status.
- Fan Command Runtime.
- Energieabschätzung mit ausdrücklicher 2-W-Annahme.
- Die letzten drei Lüfteralarme.
Im Export sind genau zwei Chart-Nodes enthalten. Der Temperaturchart hält zehn Minuten, der Feuchtechart eine Stunde Historie im konfigurierten Zeitfenster. Daraus folgt keine dauerhafte Trendarchivierung.
Standardpfad des Exports: /dashboard/page1, beispielsweise http://<RASPBERRY_PI_IP>:1880/dashboard/page1, sofern Node-RED auf Port 1880 und ohne zusätzlichen Pfadpräfix läuft.
Inbetriebnahme
1. MicroPython auf dem ESP32 sowie DHT11- und umqtt.simple-Unterstützung bereitstellen.
2. Sensor, Relais und LED entsprechend der GPIO-Tabelle anschließen.
3. Auf dem Raspberry Pi Node-RED und einen MQTT-Broker bereitstellen.
4. Modbus- und FlowFuse-Dashboard-Pakete installieren.
5. Den Store file in Node-RED konfigurieren und Node-RED neu starten.
6. bms-step2-flow.json importieren. Beim Import zusätzliche vorhandene Flows auf doppelte MQTT-Befehle, Ports und Dashboard-Pfade prüfen.
7. In Node-RED die MQTT-Anmeldedaten und bei Bedarf Host-/Port-Einstellungen lokal eintragen.
8. Im ESP32-Code WiFi-SSID, WiFi-Passwort, MQTT-Brokeradresse, Benutzer und Passwort lokal ergänzen. Die veröffentlichte Vorlage enthält keine Passwörter und startet mit leeren Pflichtfeldern nicht.
9. Die konfigurierte ESP32-Datei als main.py auf das Gerät übertragen.
10. Flow deployen, Messwerte und MQTT-Verbindung prüfen, danach Dashboard öffnen.
11. AUTO/MANUAL, Rückmeldung und Alarmverhalten anhand des Testplans kontrollieren.
Die Bezeichnungen bms-step2-flow.json und esp32_bms_step2.py sind die vorgesehenen Upload-Namen für die bereits vorbereiteten Projektdateien.
Testplan und Nachweise
Die folgende Tabelle beschreibt reproduzierbare Prüfschritte und erwartetes Verhalten. Sie ist kein vollständig ausgefülltes Abnahmeprotokoll. Gemessene Ergebnisse, Zeitpunkte, Screenshots und Videos müssen bei der Durchführung ergänzt werden.
Test	Durchführung	Erwartetes Verhalten
Messwerte	ESP32 verbinden und DHT11-Werte beobachten	Temperatur und Feuchte etwa alle zwei Sekunden
Hysterese	Bei 23 °C Sollwert obere/untere Grenze erreichen	EIN ab 24 °C, AUS bis 22 °C; Zustand dazwischen halten
MANUAL	MANUAL wählen, Manual Fan ON/OFF auslösen	Befehl und Relais folgen bei nächster Auswertung
Feedbackalarm	Lüfterbefehl EIN, Fan Feedback OFF	Alarm nach fünf Sekunden plus Auswertungsintervall
Alarmende	Fan Feedback ON auslösen	Alarm endet; bestehender Historieneintrag wird aktualisiert
Datenverlust	Temperaturpublikation unterbrechen	Warnung; AUTO-Lüfter AUS, Ventil geschlossen
ESP32-Timeout	Weitere Ausgangsbefehle unterbrechen	Ausgang wird nach Timeout-Prüfung ausgeschaltet
Ventil	Kühlbedarf, Befehl und Feedback kombinieren	LED nur bei vollständiger Freigabe EIN
Persistenz	Historie und Zeit erfassen, geordnet neu starten	Gespeicherte Gesamtwerte bei neuen Auswertungen verfügbar
Energie	Befehlsdauer mit 2-W-Annahme vergleichen	Wh-Wert entspricht Befehlsstunden × 2


Bisherige Rückmeldungen aus der Entwicklungsarbeit bestätigen, dass die Dashboard-Charts nach Layoutkorrektur wieder sichtbar waren. Darüber hinaus ersetzt diese Dokumentation keinen neuen Hardwaretest.
Troubleshooting
Problem	Prüfung / Vorgehen
Keine MQTT-Daten	WiFi, Brokeradresse, Zugangsdaten und identische Topics prüfen
ESP32 startet nicht	Leere SSID-/Passwortfelder lokal ergänzen
Lüfter bleibt AUS	Active-LOW-Verdrahtung, Modus, Kühlbedarf und Befehls-Timeout prüfen
Alarm trotz laufendem Lüfter	Simuliertes Feedback separat setzen; es wird nicht vom realen Lüfter erfasst
Ventil-LED bleibt AUS	Kühlbedarf, Fan Command, Fan Feedback und Timeout prüfen
Context-Fehler für Store file	contextStorage ergänzen und Node-RED neu starten
Sollwert wird nach Deploy 23 °C	Start-Inject Setpoint 23°C prüfen
Chart fehlt oder ist zu klein	Widgethöhe, Breite, Gruppenbreite und Layout kontrollieren; die Temperaturhöhe 6×1 war zu klein
Zusätzliche Temperaturquelle	MQTT als primären Regelungspfad beibehalten; Simulationspfad bewusst getrennt lassen


Aus dem Vorgänger wurde die Trennung von Steuerungs- und Visualisierungsdaten übernommen. Vor dem Temperaturchart gibt der Flow nur die benötigten Felder weiter:
return { payload: msg.payload, topic: msg.topic };
Damit werden Modbus-Puffer und Transportmetadaten nicht in die Charthistorie übernommen. Steuerungszweige behalten die vollständigen Nachrichten.
Projektstatus und Grenzen
Im bereitgestellten Flow und ESP32-Code sind Sensorübertragung, Regelung, Befehlsausgänge, Modbus-Modell, Watchdog, Alarmhistorie, Befehlsdauer und Energieabschätzung implementiert. Die Funktionsbeschreibung wurde mit dem Export und dem bereitgestellten Code abgeglichen; eine neue vollständige Hardwareprüfung ist damit nicht verbunden.
Bestandteil	Status / Grenze
Temperatur / Feuchte	Reale DHT11-Messung
Lüfter	Reale Relaisansteuerung
Fan Feedback	Simuliert
Kühlventil	LED-Darstellung
Energie	Berechnete Abschätzung
Alarmhistorie / Zeit	Persistenz benötigt externen Store file
Alarmfarben	Zusätzliche Farblogik noch offen
Trends	Keine Datenbankarchivierung
Sicherheitsfunktion	Keine zertifizierte oder unabhängig garantierte Abschaltung


Mögliche Erweiterungen
- Reale Lüfterrückmeldung oder Drehzahlmessung.
- Reales Ventil mit Positionsrückmeldung.
- Gemessene Leistung und Energie.
- Alarmfarben, Quittierung und zusätzliche Alarmtypen.
- Eigener Feuchte-Watchdog und erweiterte Plausibilitätsprüfung.
- Datenbank für langfristige Trends und Ereignisse.
- BACnet/IP oder Modbus RTU/RS485.
- Mehrere Räume und Zonen.
- MQTT mit TLS und differenzierten Topic-Berechtigungen.
Ziel des Projekts
Der Aufbau vermittelt praktische Erfahrung in Sensorintegration, MQTT und Modbus, Regelungslogik, Zustandsverwaltung, Command/Feedback-Trennung, Alarmmanagement, persistenter Speicherung und Visualisierung. Für die Präsentation des Projekts werden reale Funktionen, Simulationen und rechnerische Annahmen ausdrücklich getrennt beschrieben.
🇬🇧 English
Overview
This practical building automation project combines real temperature and humidity sensing with BMS/HVAC control in Node-RED. An ESP32 reads a DHT11 and publishes measurements through MQTT to a Raspberry Pi. Node-RED processes the data, calculates cooling demand and sends commands for a real relay-controlled fan and an LED representing a cooling valve.
The project builds on Mini-BMS-HVAC-Automation. It is documented as a separate practical project because it extends the earlier Modbus simulation with real sensing, MQTT communication, ESP32 outputs, humidity visualization, alarm history and an energy estimate.
This is a learning and demonstration setup, not an approved controller for a production HVAC installation.
Main Features
- Real temperature and humidity measurement with DHT11 and ESP32.
- MQTT measurements approximately every two seconds.
- Temperature setpoint through a simulated Modbus Holding Register.
- Cooling control with ±1 °C hysteresis.
- AUTO and MANUAL operation.
- MQTT fan commands and ESP32 relay output.
- Simulated fan feedback through a Modbus Discrete Input.
- Missing-feedback fan alarm after five seconds.
- Temperature-data watchdog with a five-second timeout.
- Virtual cooling valve logic with an ESP32 LED.
- Last three fan alarms, including raised and cleared timestamps.
- Accumulated fan command duration using a file-based context store.
- Energy estimate based on an assumed power of 2 W.
- Two live charts: temperature/setpoint and relative humidity.
- WiFi/MQTT reconnection and ESP32 output shutdown logic.
System Architecture
Area	Data path	Purpose
Measurement	DHT11 → ESP32 → MQTT → Node-RED	Real temperature and relative humidity
Control	Temperature + setpoint → hysteresis → AUTO/MANUAL	Calculate fan command
Fan	Node-RED → MQTT → ESP32 GPIO23 → relay → fan	Real output actuation
Feedback	Modbus simulation → Node-RED	Simulated fan feedback for monitoring and tests
Cooling valve	Cooling demand + fan command + feedback → MQTT → GPIO26	LED represents valve command
Monitoring	States → alarm, history, command duration, energy estimate	Diagnostics and visualization
Operation	Node-RED Inject nodes + FlowFuse Dashboard	Test commands in editor; dashboard displays


MQTT is the primary temperature source. The exported Modbus temperature simulation remains available but is not connected as a second control source. Modbus is still used for the setpoint, fan command and simulated feedback.
Technologies and Hardware
Component	Use
ESP32 with MicroPython	Sensor reading, MQTT and output control
DHT11	Temperature and relative humidity
Active-LOW relay	Fan switching
Fan	Real actuator in the demonstration setup
LED with series resistor	Virtual cooling valve indication
Raspberry Pi	Node-RED, MQTT broker and Modbus simulation
Node-RED / JavaScript	Validation, control, states and monitoring
MQTT / umqtt.simple	Measurements and output commands
node-red-contrib-modbus	Modbus TCP client and simulation server
FlowFuse Dashboard	Trends, status displays and alarm table
Thonny	Editing MicroPython files on the ESP32
GitHub	Source code and documentation


Versions recorded in the flow export:
- node-red-contrib-modbus: 5.60.2
- @flowfuse/node-red-dashboard: 1.32.0
These are export versions, not a statement about the latest available releases.
GPIO Mapping
GPIO	Component	Behavior
4	DHT11 data	Read temperature and humidity
23	Fan relay IN2	LOW = ON, HIGH = OFF
26	LED with series resistor	HIGH = valve command ON, LOW = OFF


The program initializes the fan relay HIGH and the valve LED LOW.
MQTT Communication
Topic	Direction	Payload
bms/room1/temperature	ESP32 → Node-RED	Temperature in °C as numeric text
bms/room1/humidity	ESP32 → Node-RED	Relative humidity in % as numeric text
bms/room1/fan/command	Node-RED → ESP32	ON or OFF
bms/room1/valve/command	Node-RED → ESP32	ON or OFF


The ESP32 uses the Raspberry Pi LAN address for the broker. Node-RED uses 127.0.0.1:1883 in the export. Adapt the broker address to the local network.
ESP32 sensor publications are not retained. The flow sends output commands at QoS 0, with no retained output command configured. MQTT uses port 1883 without TLS. Credentials belong in local configuration, not in the public repository.
Modbus Mapping
Signal	Modbus type	Function code	Address	Current role
Simulated temperature	Input Register	FC4	0	Remaining simulation/debug path
Temperature setpoint	Holding Register	FC3 / FC6	0	Read/write setpoint
Fan command	Coil	FC1 / FC5	0	Mirror command in Modbus model
Fan feedback	Discrete Input	FC2	0	Simulated feedback


Client settings: host 127.0.0.1, port 10502, Unit ID 1. The simulation server binds to 0.0.0.0 in the export. Modbus reads run every second.
Temperature and Scaling
Real MQTT temperature arrives in °C and does not require division by ten. The temperature validation function expects a finite numeric payload; the MQTT input uses auto-detection.
Modbus values use a factor of ten:
Engineering value	Raw Modbus value
23.0 °C	230
24.6 °C	246


The setpoint is multiplied by ten before writing and by 0.1 after reading. Empty, non-finite and zero register values are rejected by the setpoint reader. A startup Inject writes 23 °C after five seconds; a later deploy can trigger it again.
Humidity validation converts the payload to a number and rejects non-finite values and values outside 0–100 %. This is not comprehensive sensor plausibility validation.
Hysteresis Control
For a 23 °C setpoint:
Temperature	Cooling demand
≥ 24 °C	ON
≤ 22 °C	OFF
Between 22 and 24 °C	Keep previous state


The flow stores the cooling state in flow context. Hysteresis prevents rapid switching close to the setpoint. The DHT11 provides coarse measurements; this setup is not precision room-climate control.
AUTO / MANUAL
AUTO
The fan command follows cooling demand. A temperature-data timeout makes the AUTO fan command OFF.
MANUAL
The MANUAL Mode, Manual Fan ON and Manual Fan OFF Inject nodes provide manual test commands in the Node-RED editor. The exported flow does not include dashboard switches for these operations.
Inject nodes change flow context. The control/alarm logic evaluates the change on its next message, normally the next temperature sample. In MANUAL mode the manual fan command remains authoritative during a temperature-data timeout. The virtual valve closes on that timeout.
Default logic states are AUTO and manual fan command OFF when no context values exist.
Command and Feedback
Command describes the requested state; feedback is intended to represent equipment response.
Fan Command	Fan Feedback	Interpretation
ON	ON	Command matches simulated feedback
ON	OFF	Startup monitoring, then possible fan alarm
OFF	OFF	No ON command
OFF	ON	No separate mismatch alarm in the current flow


Feedback comes from the Modbus simulation. No speed sensor or physical fan feedback wire is connected. The indication therefore does not prove that the real fan is running.
Use Fan Feedback ON and Fan Feedback OFF for tests. The remaining Fan Healthy/Fan Fault nodes set a separate variable that the current alarm logic does not evaluate.
Alarm Monitoring and History
When the fan command is ON and simulated feedback is OFF, a five-second monitoring period starts. Further evaluations after this period activate the fan alarm. During the waiting period, fanStartPending is set.
Feedback ON or command OFF clears the alarm condition and resets monitoring. The current flow does not automatically disable the fan command because of this alarm.
History contains at most three records:
Field	Content
raisedAt	Alarm start timestamp
clearedAt	Alarm end timestamp
status	AKTIV (active) or GEGANGEN (cleared)
text	Missing fan feedback description


Timestamps use the Europe/Berlin timezone and German formatting. A continuous alarm does not create duplicate records. Clearing updates the existing active record. No separate operator acknowledgement is implemented.
Temperature Watchdog and ESP32 Behavior
Node-RED expects regular valid temperature data. Five seconds without a message in the watchdog path triggers a warning and evaluates the control logic with dataTimeout = true.
The ESP32 code includes:
- Sensor reads every 2,000 ms.
- WiFi connection attempt with a 20-second timeout.
- Retry pauses of approximately five seconds.
- MQTT subscriptions for fan and valve.
- Both outputs switched OFF when closing the MQTT connection.
- The affected output switched OFF on an invalid command.
- Separate 10,000 ms command timeouts for fan and valve.
- Output shutdown and connection cleanup on manual program stop.
Command timeouts are checked in the main loop. Blocking network operations may delay the response. This is not an independent hardware watchdog or a guaranteed shutdown time.
On a DHT11 read error, no new sensor values are published and the code attempts an MQTT ping. Node-RED can detect missing temperature data through its watchdog. There is no separate humidity timeout watchdog.
Cooling Valve
The virtual valve is enabled only when all conditions hold:
- No temperature-data timeout.
- Cooling demand is active.
- Fan command is ON.
- Simulated fan feedback is ON.
Node-RED sends the resulting MQTT command to GPIO26. The LED represents the command. There is no physical valve or valve-position feedback.
Command Duration, Persistence and Energy Estimate
Fan Command Runtime
The counter accumulates elapsed time while the previous fan command was ON. Intervals longer than five seconds are excluded so that long communication or restart gaps are not simply counted as runtime.
The total is stored using context.get/set(..., "file"). Timing markers and previous command remain in the default context. This is command duration, not measured mechanical fan runtime.
File-Based Context Store
A flow export does not contain Node-RED settings.js. History and total duration require a context store named file. Add the following configuration to the existing settings:
contextStorage: {
    default: "memoryOnly",
    memoryOnly: { module: "memory" },
    file: { module: "localfilesystem" }
},
Restart Node-RED afterward. Extend the existing settings file rather than replacing it completely. Writes may be buffered; sudden power loss may lose recently updated values that have not yet been written.
Energy Estimate
Estimated energy (Wh) = fan command duration (h) × 2 W
One hour of command duration gives a calculated 2 Wh. The 2 W value is a learning assumption. No current, voltage or power sensor is installed, so the value is not measured consumption. Faulty or simulated feedback does not change this calculation basis.
Dashboard
The Raumüberwachung group displays:
- Temperature and setpoint in one trend.
- Relative humidity value and separate trend.
- Temperature-data status.
- Fan Command and simulated Fan Feedback.
- Alarm Status.
- Cooling valve status.
- Fan Command Runtime.
- Energy estimate with explicit 2 W assumption.
- Last three fan alarms.
The export contains exactly two chart nodes. The temperature chart retains a ten-minute window and the humidity chart a one-hour window. This does not provide persistent trend archiving.
Export path: /dashboard/page1, for example http://<RASPBERRY_PI_IP>:1880/dashboard/page1 when Node-RED uses port 1880 without an additional path prefix.
Setup
1. Prepare MicroPython and DHT11/umqtt.simple support on the ESP32.
2. Connect the sensor, relay and LED according to the GPIO table.
3. Prepare Node-RED and an MQTT broker on the Raspberry Pi.
4. Install the Modbus and FlowFuse Dashboard packages.
5. Configure the file context store and restart Node-RED.
6. Import bms-step2-flow.json. Check other installed flows for duplicate MQTT commands, ports and dashboard paths.
7. Enter MQTT credentials and any required host/port settings locally in Node-RED.
8. Fill in WiFi SSID/password and MQTT broker/user/password locally in the ESP32 code. The public template contains no passwords and does not run with empty required fields.
9. Transfer the configured ESP32 script to the device as main.py.
10. Deploy, verify measurements and MQTT connection, then open the dashboard.
11. Check AUTO/MANUAL, feedback and alarm behavior using the test plan.
bms-step2-flow.json and esp32_bms_step2.py are the intended upload names for the project files already prepared.
Test Plan and Evidence
This table specifies reproducible checks and expected behavior. It is not a completed acceptance report. Record measured results, dates, screenshots and videos when running the tests.
Test	Procedure	Expected behavior
Measurements	Connect ESP32 and observe DHT11 values	Temperature/humidity about every two seconds
Hysteresis	Reach upper/lower thresholds with 23 °C setpoint	ON at 24 °C, OFF at 22 °C; hold state between
MANUAL	Select MANUAL and trigger Manual Fan ON/OFF	Command/relay follow on next evaluation
Feedback alarm	Fan command ON; Fan Feedback OFF	Alarm after five seconds plus evaluation interval
Alarm clear	Trigger Fan Feedback ON	Alarm clears; existing history record updated
Data loss	Interrupt temperature publications	Warning; AUTO fan OFF and valve closed
ESP32 timeout	Stop further output commands	Output shuts down when timeout is checked
Valve	Combine cooling demand, command and feedback	LED ON only with full enable conditions
Persistence	Record history/duration; perform orderly restart	Stored totals available on new evaluations
Energy	Compare command duration with 2 W assumption	Wh equals command hours × 2


Development feedback confirms that dashboard charts became visible again after a layout correction. This documentation does not replace a new hardware test.
Troubleshooting
Problem	Check / action
No MQTT data	Check WiFi, broker address, credentials and matching topics
ESP32 will not start	Fill empty SSID/password fields locally
Fan stays OFF	Check active-LOW wiring, mode, cooling demand and command timeout
Alarm despite real fan running	Set simulated feedback separately; it is not measured from the fan
Valve LED stays OFF	Check cooling demand, Fan Command, Fan Feedback and timeout
Context error for file store	Add contextStorage and restart Node-RED
Setpoint returns to 23 °C after deploy	Check the Setpoint 23°C startup Inject
Missing/tiny chart	Check widget dimensions, group width and layout; temperature size 6×1 was too small
Additional temperature source	Keep MQTT as primary control source and simulation deliberately separate


The project retains the predecessor's separation of control and visualization data. Before the temperature chart, only required fields are forwarded:
return { payload: msg.payload, topic: msg.topic };
Modbus buffers and transport metadata therefore do not enter chart history. Control branches keep the complete messages.
Project Status and Limitations
Sensor transmission, control, command outputs, Modbus model, watchdog, alarm history, command duration and energy estimate are implemented in the provided flow and ESP32 code. This description was checked against the export and supplied code; this does not constitute a new complete hardware validation.
Component	Status / limitation
Temperature / humidity	Real DHT11 measurement
Fan	Real relay actuation
Fan Feedback	Simulated
Cooling valve	LED representation
Energy	Calculated estimate
History / duration	Persistence requires external file store
Alarm colors	Additional color logic still pending
Trends	No database archive
Safety function	No certified or independently guaranteed shutdown


Possible Future Extensions
- Physical fan feedback or speed measurement.
- Real valve and position feedback.
- Measured power and energy.
- Alarm colors, acknowledgement and additional alarm types.
- Dedicated humidity watchdog and stronger plausibility validation.
- Database for long-term trends and events.
- BACnet/IP or Modbus RTU/RS485.
- Multiple rooms and zones.
- MQTT with TLS and differentiated topic permissions.
Project Purpose
The setup develops practical experience in sensor integration, MQTT and Modbus, control logic, state management, command/feedback separation, alarm management, persistent storage and visualization. The project presentation explicitly distinguishes real hardware functions, simulations and calculated assumptions.
