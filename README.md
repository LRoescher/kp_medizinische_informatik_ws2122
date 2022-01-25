# Entscheidungsunterstützungssystem Kawasaki-Syndrom und PIMS

Dieses Projekt umfasst eine Python-Anwendung, die medizinisches Personal bei der Diagnosestellung für die seltenen Erkrankungen Kawasaki-Syndrom und Pediatric Inflammatory Multisystem Syndrome (PIMS) unterstützen soll. 

Genauere Informationen können im docs-Verzeichnis eingesehen werden

## Aufbau

Das Projekt ist in verschiedene Verzeichnisse unterteilt:

- data: Enthält alle zur Verfügung gestelltenen Datensätze
- docs: Enthält die Dokumentation des Projekts
- config: Enthält Konfigurationsdateien, die automatisch eingelesen werden
- upload: Ordner zum Speichern von über die Anwendung hochgeladenen CSV-Dateien
- Backend: Backend der Anwendung enthält einen ETL-Job, Datenbank-Connector und Analyse-Software
- Frontend: Enthält den Flask-Server und Frontend-Dateien (HTML, CSS, Javascript)
- Mock-Up: Enthält ein während der Entwicklung erstelltes interaktives Mock-Up für das Frontend
- ETLProcess: Enthält eine Standalone-Version des ETL-Jobs (Ggf. nicht auf dem selben Stand wie im Backend)

## Installation/ Verwendung

Die Anwendung ist in Kombination mit einer laufenden OMOP-Datenbank zu verwenden. Über die Konfigurationsdatei im *config*-Verzeichnis kann die entsprechende Verbindung eingestellt werden. Dies ist auch noch über die Web-Oberfläche nach Start der Anwendung möglich.

#### Lokale Ausführung

Die Anwendung kann lokal gestartet werden, indem die Datei *flask_app.py* im *Frontend*-Verzeichnis ausgeführt wird. Alternativ kann auch das Shell-Script *start_app.sh* aus dem Hauptverzeichnis gestartet werden.

Ggf. sind zunächst die im *requirements.txt* aufgeführten Abhängigkeiten zu installieren.

Die Anwendung ist anschließend unter http://192.168.2.132:8080/ über einen Browser erreichbar.

#### Ausführung als Docker-Container

Alternativ kann die Anwendung auch als Docker-Container betrieben werden. Im Hauptverzeichnis ist dafür ein Dockerfile hinterlegt.
Dieses Dockerfile kann mit dem Kommandozeilenbefehl *docker build -f ./dockerfile -t decision_system:v1 .* ausgeführt werden. Die benötigten Abhängigkeiten werden während des Builds automatisch heruntergeladen.

Der Docker-Container kann dann beispielsweise mit dem Befehl *docker run -d -p 80:8080 decision_system:v1* gestartet werden.

Die Anwendung ist anschließend unter *localhost* auf dem angegebenen Port über einen Browser erreichbar. Beachten Sie dabei, dass die Konfigurationsdatei die richtige Einstellung zur Datenbank enthält und passen Sie diese ggf. über das Frontend an. Docker-Container benötigen in der Regel als Hostname der Datenbank die IP-Adresse des entsprechenden Systems (Die Angabe von 'localhost' würde daher nicht funktionieren).
