📝 Protokoll-App
Die Protokoll-App ermöglicht es, Lärmdaten zu erfassen und zu verwalten. Sie bietet eine einfache Benutzeroberfläche zur Eingabe und Anzeige von Störungen und speichert alle Daten in einer SQLite-Datenbank.

(Beispiel eines App-Screenshots)

🚀 Features
📅 Erfassung von Lärmdaten (Datum, Beginn, Ende, Dauer)
📊 Berechnung der Störungsdauer zwischen Start- und Endzeit
💾 Speicherung der Daten in einer SQLite-Datenbank
🔄 Automatische Berechnung der Dauer
⚙️ Einfache Benutzeroberfläche mit Kivy
🛠️ Möglichkeit, die Datenbank zu durchsuchen und anzuzeigen
📋 Installation
1. Repository klonen
bash
Code kopieren
git clone git@github.com:ALex83-r0ck/Protolkoli.git
2. Virtuelle Umgebung einrichten
Erstelle und aktiviere eine virtuelle Umgebung:

bash
Code kopieren
python -m venv .venv
Für Windows:

bash
Code kopieren
.venv\Scripts\activate
Für macOS/Linux:

bash
Code kopieren
source .venv/bin/activate
3. Abhängigkeiten installieren
Installiere alle notwendigen Pakete:

bash
Code kopieren
pip install -r requirements.txt
4. Datenbank einrichten
Erstelle die Datenbank mit der create_database() Funktion:

bash
Code kopieren
python database_setup.py
5. App starten
Führe das Programm aus:

bash
Code kopieren
python protokoll.py
👨‍💻 Nutzung
Nach dem Start der App kannst du:

Lärmdaten mit den folgenden Informationen erfassen:

Datum der Störung
Beginn und Ende der Störung
Störungsgrund
Verursacher (z.B. Nachbar)
Auswirkungen der Störung (Bewertung von 1 bis 5)
Die Daten werden in einer SQLite-Datenbank gespeichert und sind leicht abrufbar.

🛠️ Technologien
Kivy: Für die Erstellung der grafischen Benutzeroberfläche
SQLite: Datenbank zur Speicherung der Störungen
Python: Hauptsprache des Projekts
🤝 Beitrag
Beiträge sind willkommen! Wenn du neue Features oder Verbesserungen hast, fork das Repository und schick einen Pull-Request. Achte darauf, die bestehenden Code-Konventionen zu befolgen und Tests für neue Features zu schreiben.

Schritte zum Beitrag:
Forke das Repository
Erstelle einen Branch (git checkout -b feature-xyz)
Implementiere die Änderungen
Teste deine Änderungen
Schicke einen Pull-Request an den main-Branch
📄 Lizenz
Dieses Projekt ist unter der MIT-Lizenz lizenziert. Weitere Details findest du in der LICENSE-Datei.

🖼️ Screenshots
Hier ist ein Beispiel, wie die Benutzeroberfläche aussieht: