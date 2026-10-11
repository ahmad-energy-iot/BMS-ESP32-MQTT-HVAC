# Projektdokumentation: BMS mit ESP32, MQTT und Modbus TCP

## 1. Ziel des Projekts

Aufbau einer Gebäudeautomations-Demonstration für einen Raum mit realen Messwerten, Lüftersteuerung, simuliertem Kühlventil, Rückmeldungsüberwachung, Alarmhistorie und Energieabschätzung.

Dieses persönliche Lernprojekt entwickelt das vorherige Mini-BMS-Projekt weiter. Es dokumentiert eigene praktische Projekterfahrung.

## 2. Hardware und Software

| Bestandteil | Aufgabe |
|---|---|
| Raspberry Pi | Node-RED und Mosquitto |
| ESP32 mit MicroPython | Sensorabfrage und Ausgangssteuerung |
| DHT11 | Temperatur und relative Luftfeuchtigkeit |
| 5-V-Relaismodul | Schalten des Lüfters |
| 5-V-USB-Lüfter | Realer Aktor |
| LED mit Vorwiderstand | Darstellung eines Kühlventils |
| Node-RED Dashboard 2 | Visualisierung |
| Modbus-TCP-Simulator | Sollwert, Befehl und simulierte Rückmeldung |

Im getesteten Aufbau wurden folgende Versionen verwendet:

- Node-RED: 5.0.7
- `@flowfuse/node-red-dashboard`: 1.32.0
- `node-red-contrib-modbus`: 5.60.2

Die ESP32-Firmware benötigt das Modul `umqtt.simple`.

## 3. Anschlüsse

| Signal | Anschluss | Verhalten |
|---|---|---|
| DHT11-Datenleitung | GPIO4 | Sensorabfrage |
| Relais IN2 | GPIO23 | LOW = ON, HIGH = OFF |
| Ventil-LED | GPIO26 | HIGH = ON, LOW = OFF |

Die LED wird mit Vorwiderstand betrieben; ihre Kathode ist mit GND verbunden.

Der Lüfter erhält seine Versorgung aus einem separaten 5-V-USB-Netzteil. Der Relaiskontakt schaltet die Lüfterversorgung. Der Steuereingang des Relais und sein Schaltkontakt erfüllen unterschiedliche Aufgaben.

Die Relaisversorgung und die Eingangspegel müssen zum verwendeten Modul passen. Die Angaben beschreiben den getesteten Niederspannungsaufbau und sind kein universeller Verdrahtungsplan.

## 4. Netzwerk

| Verbindung | Einstellung im Versuchsaufbau |
|---|---|
| Raspberry Pi | 192.168.178.38 |
| ESP32 | 192.168.178.36 |
| Node-RED Editor | Port 1880 |
| MQTT | Port 1883 |
| Modbus TCP | Port 10502 |
| Dashboard | /dashboard/page1 |

Die IP-Adressen sind lokale Beispiele und müssen an das eigene Netzwerk angepasst werden.

Node-RED verbindet sich mit dem MQTT-Broker und dem Modbus-Simulator über `127.0.0.1`, da diese Dienste auf demselben Raspberry Pi laufen.

Der ESP32 verwendet die LAN-Adresse des Raspberry Pi als MQTT-Broker-Adresse.

## 5. MQTT-Datenpunkte

| Topic | Richtung | Payload |
|---|---|---|
| bms/room1/temperature | ESP32 → Node-RED | Temperatur als numerischer Text |
| bms/room1/humidity | ESP32 → Node-RED | Relative Luftfeuchtigkeit als numerischer Text |
| bms/room1/fan/command | Node-RED → ESP32 | ON / OFF |
| bms/room1/valve/command | Node-RED → ESP32 | ON / OFF |

Die Messwerte werden ungefähr alle zwei Sekunden mit QoS 0 und `retain=False` veröffentlicht.

Es gibt keinen MQTT-Rückkanal für die tatsächliche Drehzahl oder den mechanischen Lauf des Lüfters.

Die Lüfterrückmeldung wird separat innerhalb von Node-RED simuliert.

## 6. Modbus-Datenpunkte

Unit ID: 1. Die Adressen beginnen im Flow bei 0.

Die vier Datenbereiche besitzen getrennte Adressräume.

| Bereich | Adresse | Bedeutung |
|---|---|---|
| Input Register | 0 | Simulierte Temperatur im Lern-/Debugzweig |
| Holding Register | 0 | Temperatursollwert |
| Coil | 0 | Lüfterbefehl |
| Discrete Input | 0 | Simulierte Lüfterrückmeldung |

Temperaturwerte werden im Simulator mit Faktor 10 dargestellt:

- 230 entspricht 23 °C.
- 246 entspricht 24,6 °C.

Die reale Regeltemperatur der aktuellen Version kommt über MQTT vom DHT11. Der simulierte Temperaturwert ist im aktuellen Export nur mit einem Debugzweig verbunden.

Der Modbus-Server verwendet Port 10502. Der lokale Client verbindet sich mit `127.0.0.1:10502`.

## 7. Installation und Inbetriebnahme

### Raspberry Pi

Node-RED muss bereits installiert sein.

Mosquitto bereitstellen:

```bash
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable --now mosquitto
```

Für den ESP32 muss Mosquitto Verbindungen aus dem LAN akzeptieren. Ein Broker, der ausschließlich auf localhost lauscht, ist vom ESP32 nicht erreichbar.

Im getesteten Aufbau wurde MQTT-Authentifizierung mit dem Benutzer `bms_user` verwendet. Listener, Benutzer und Passwortdatei müssen lokal eingerichtet werden. Die individuelle Mosquitto-Konfiguration ist nicht Teil dieses Repositorys.

### Node-RED

1. Über Manage palette die Dashboard- und Modbus-Pakete installieren.
2. Den Kontextspeicher aus `config/context-storage.example.js` in der aktiven `settings.js` einrichten.
3. Eine vorhandene `contextStorage`-Eigenschaft ersetzen; keine zweite hinzufügen.
4. Den Ausschnitt innerhalb des exportierten Einstellungsobjekts und außerhalb von Kommentaren einsetzen.
5. Syntax prüfen und Node-RED neu starten.

Im ursprünglichen Pi-Aufbau:

```bash
node --check /home/ahmad/.node-red/settings.js
sudo systemctl restart nodered
```

Danach:

1. `flows/bms-step2-flow.json` importieren.
2. Im MQTT-Broker-Konfigurationsknoten Zugangsdaten lokal ergänzen.
3. Prüfen, dass Port 10502 nicht durch einen anderen Modbus-Simulator belegt ist.
4. Deploy ausführen.
5. Dashboard öffnen:

```text
http://<PI-IP>:1880/dashboard/page1
```

Der Sollwert-Inject initialisiert nach ungefähr fünf Sekunden den Sollwert 23 °C.

Automatischen Dienststart aktivieren:

```bash
sudo systemctl enable nodered.service
```

### ESP32

1. MicroPython und das Modul `umqtt.simple` bereitstellen.
2. `firmware/esp32_bms_step2.py` öffnen.
3. SSID, WiFi-Passwort, MQTT-Broker-Adresse und MQTT-Passwort lokal ergänzen.
4. Als `main.py` auf dem ESP32 speichern.
5. Shell-Ausgaben und MQTT-Eingang in Node-RED prüfen.

Die Vorlage mit leeren Zugangsdaten ist nicht direkt betriebsbereit.

## 8. Steuerungslogik

### Hysterese

Bei einem Sollwert von 23 °C:

- Ab 24 °C: Kühlbedarf ON.
- Bei höchstens 22 °C: Kühlbedarf OFF.
- Zwischen den Grenzen: bisherigen Zustand beibehalten.

### AUTO

Der Lüfterbefehl folgt dem Kühlbedarf.

Bei einer Temperaturdaten-Timeout-Nachricht wird der Lüfterbefehl ausgeschaltet.

### MANUAL

Die Bedienung erfolgt über Inject-Nodes im Node-RED-Editor:

- MANUAL Mode
- Manual Fan ON
- Manual Fan OFF

Die aktuelle Version besitzt dafür keine Dashboard-Schaltflächen.

Im MANUAL-Modus überschreibt der Temperaturdaten-Timeout den manuellen Lüfterbefehl nicht.

Änderungen werden bei der nächsten Auswertung der Steuerlogik wirksam.

### Ventil-LED

Die Ventilfreigabe benötigt gleichzeitig:

- Kühlbedarf ON.
- Lüfterbefehl ON.
- Simulierte Lüfterrückmeldung ON.
- Keine Temperaturdaten-Timeout-Nachricht.

Ein manueller Lüfterbefehl allein öffnet das simulierte Ventil nicht.

## 9. Überwachung

### Temperaturdaten

Nach fünf Sekunden ohne gültige Temperaturdaten erzeugt der Trigger eine Warnung und eine Timeout-Nachricht.

### Lüfterrückmeldung

Ein ON-Befehl ohne simulierte Rückmeldung startet die Überwachung.

Nach mindestens fünf Sekunden wird bei der nächsten eingehenden Steuerungsnachricht ein Alarm gesetzt.

Es handelt sich um eine nachrichtenabhängige Auswertung, nicht um einen unabhängig laufenden Alarmtimer.

Bei Befehl OFF oder vorhandener Rückmeldung wird die Überwachung zurückgesetzt.

Für diesen Test werden `Fan Feedback ON` und `Fan Feedback OFF` verwendet.

Die älteren Inject-Nodes `Fan Healthy` und `Fan Fault` schreiben eine andere Variable, die von der aktuellen Alarmfunktion nicht ausgewertet wird.

### ESP32-Befehlsüberwachung

Für Lüfter und Ventil werden getrennte Zeitstempel geführt.

Nach zehn Sekunden ohne erneuten gültigen Befehl wird der betreffende Ausgang bei der nächsten Schleifenauswertung ausgeschaltet.

Bei erkanntem WiFi- oder MQTT-Verlust werden beide Ausgänge ausgeschaltet und Verbindungsversuche wiederholt.

Blockierende Netzwerkoperationen können die Reaktion verzögern. Zehn Sekunden sind deshalb kein garantierter maximaler Abschaltzeitraum.

## 10. Alarmhistorie

Pro neuem Alarm wird ein Datensatz erzeugt:

| Feld | Bedeutung |
|---|---|
| raisedAt | Beginn der erkannten Alarmbedingung |
| clearedAt | Ende der erkannten Alarmbedingung |
| status | AKTIV / GEGANGEN |
| text | Alarmmeldung |

Bei Alarmende wird derselbe Datensatz aktualisiert.

Die Liste enthält höchstens drei Ereignisse, neueste zuerst.

`GEGANGEN` bedeutet, dass die Alarmbedingung nicht mehr erkannt wird. Es bedeutet keine Quittierung und keinen Nachweis einer Reparatur.

Zeitangaben verwenden `Europe/Berlin`.

Nach einer Unterbrechung entspricht eine neu eingetragene Ende-Zeit dem ersten beobachteten Normalzustand, nicht einer rekonstruierten Zeit während des Ausfalls.

## 11. Persistente Speicherung

Die Konfiguration verwendet:

- `memoryOnly` als Standardspeicher für momentane Zustände.
- `file` für die Laufzeitsumme und Alarmhistorie.

AUTO/MANUAL-Zustand und simulierte Rückmeldung werden nicht dauerhaft gespeichert. Nach Neustart gelten die Initialwerte.

Der Dateispeicher schreibt mit der verwendeten Standardkonfiguration ungefähr alle 30 Sekunden.

Für einen Persistenztest:

1. Lüfter auf MANUAL OFF setzen.
2. Mindestens 35 Sekunden nach der letzten Änderung warten.
3. Node-RED geordnet neu starten.
4. Laufzeit und Alarmhistorie vergleichen.

Ein abruptes Abschalten kann zuletzt noch nicht geschriebene Werte verlieren.

Gespeicherte Kontextwerte sind nicht Teil des JSON-Exports. Ein neuer Aufbau beginnt ohne die historischen Werte des ursprünglichen Raspberry Pi.

## 12. Befehlsdauer und Energie

Der Zähler addiert das vorangegangene Zeitintervall, wenn der vorherige Lüfterbefehl ON war.

Intervalle über fünf Sekunden werden übersprungen, um unbeobachtete Unterbrechungen nicht mitzuzählen.

Die Zeitmessung ist eine Näherung der Befehlsdauer und keine bestätigte mechanische Laufzeit.

```text
Geschätzte Energie [Wh] = Befehlsdauer [h] × 2 W
```

Die Leistung von 2 W ist eine ausdrücklich gewählte Lernannahme. Sie wurde nicht elektrisch gemessen und nicht aus einem Datenblatt übernommen.

Beispiel mit ganzen Sekunden:

```text
2990 ÷ 3600 × 2 ≈ 1,661 Wh
```

Die Anzeige kann 1,662 Wh zeigen, weil die Berechnung die vollständige Zeit in Millisekunden verwendet, während der Sekundenzähler abgerundet wird.

Die Energie wird aus der gespeicherten Laufzeit neu berechnet und benötigt keinen zusätzlichen persistenten Zähler.

## 13. Praktisch geprüfte Szenarien

| Test | Beobachtung |
|---|---|
| AUTO-Hysterese | ON bei 24 °C, OFF bei 22 °C |
| Relais und Lüfter | Reales Schalten und Lüfterlauf |
| Fehlende simulierte Rückmeldung | Verzögerter Lüfteralarm |
| Rückmeldung ON oder Befehl OFF | Alarmbedingung endet |
| Ventilfreigabe | LED abhängig von Bedarf, Befehl und Rückmeldung |
| MQTT-Unterbrechung | Verbindungsversuche und erneute Datenübertragung |
| WiFi-Unterbrechung | Erneute WiFi- und MQTT-Verbindung |
| Fehlende Temperaturdaten | Datenwarnung und AUTO-Befehl OFF |
| Alarmhistorie | Höchstens drei Ereignisse; Beginn und Ende |
| Node-RED-Neustart | Laufzeit und Alarmhistorie bleiben erhalten |
| Energieabschätzung | Rechnerisch geprüft; nach OFF konstant |

Diese Prüfungen wurden am persönlichen Laboraufbau durchgeführt. Sie sind keine automatisierten Tests auf beliebiger Hardware.

## 14. Troubleshooting

### MQTT-Verbindung funktioniert nicht

Brokerdienst und Listener prüfen:

```bash
systemctl status mosquitto --no-pager
sudo ss -ltnp 'sport = :1883'
```

Zusätzlich IP-Adresse, Benutzer und Passwort prüfen.

### Node-RED öffnet nicht

```bash
systemctl status nodered --no-pager
sudo systemctl start nodered
```

### DHT11 meldet ETIMEDOUT

Datenpin GPIO4, Versorgung und Steckverbindungen prüfen.

Eine erfolgreiche MQTT-Verbindung bestätigt nicht, dass der Sensor korrekt angeschlossen ist.

### Zähler wird nach Neustart null

Aktive `settings.js` und Kontextspeicher prüfen.

Eine Syntaxprüfung allein erkennt nicht, dass die Konfiguration versehentlich innerhalb eines Kommentars steht.

### Doppelte Dashboard-Elemente

Andere Flow-Tabs können dieselbe Dashboard-Gruppe verwenden.

Vor dem Entfernen eines Elements dessen Herkunft prüfen. Der veröffentlichte Export enthält nur BMS Step2.

## 15. Grenzen

- Ein Raum, keine Multi-Zone-Anlage.
- Simulierte Lüfterrückmeldung.
- LED statt physischem Kühlventil.
- Angenommene Leistung statt elektrischer Energiemessung.
- Keine BACnet/IP-Implementierung.
- Keine produktive Gebäudeanlage.
- Keine zertifizierte Sicherheitssteuerung.

Die nächsten Lernprojekte können Multi-Zone-Regelung, BACnet/IP und weitere Systemintegration ergänzen.
