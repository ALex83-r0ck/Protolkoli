import sqlite3
from datetime import datetime
import csv
import os

DB_FILE = "database/protokoll.db"

def create_database():
    """Erstellt die Datenbank und Tabellen, falls diese noch nicht existieren."""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)  # Ordner erstellen, falls nicht vorhanden
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Tabelle 'laermdaten' erstellen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS laermdaten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datum TEXT NOT NULL,  -- Format: DD-MM-YYYY
            beginn TEXT NOT NULL, -- Format: HH:MM
            ende TEXT NOT NULL,   -- Format: HH:MM
            grund TEXT NOT NULL,
            verursacher TEXT NOT NULL,
            auswirkung TEXT NOT NULL
        );
    """)

    # Tabelle 'massnahmen' erstellen
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS massnahmen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datum TEXT NOT NULL, -- Format: DD-MM-YYYY
            massnahme TEXT NOT NULL,
            ergebnis TEXT
        );
    """)

    # Indexe erstellen
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_datum ON laermdaten (datum);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_massnahmen_datum ON massnahmen (datum);")

    conn.commit()
    conn.close()
    print("Datenbank und Tabellen erfolgreich erstellt!")

def insert_laermdaten(datum, beginn, ende, grund, verursacher, auswirkung):
    """Fügt einen neuen Eintrag in die Tabelle 'laermdaten' ein."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO laermdaten (datum, beginn, ende, grund, verursacher, auswirkung)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (datum, beginn, ende, grund, verursacher, auswirkung))
    
    conn.commit()
    conn.close()
    print("Lärmdaten erfolgreich eingefügt!")

def insert_massnahmen(datum, massnahme, ergebnis):
    """Fügt einen neuen Eintrag in die Tabelle 'massnahmen' ein."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO massnahmen (datum, massnahme, ergebnis)
        VALUES (?, ?, ?);
    """, (datum, massnahme, ergebnis))

    conn.commit()
    conn.close()
    print("Maßnahme erfolgreich eingefügt!")

def get_all_laermdaten():
    """Listet alle Lärmdaten aus der Datenbank auf."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT datum, beginn, ende, grund, verursacher, auswirkung
        FROM laermdaten
        ORDER BY date(datum) ASC, time(beginn) ASC;
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def get_all_massnahmen():
    """Listet alle Maßnahmen aus der Datenbank auf."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT datum, massnahme, ergebnis
        FROM massnahmen
        ORDER BY date(datum) ASC;
    """)
    data = cursor.fetchall()
    conn.close()
    return data

def delete_all_laermdaten():
    """Löscht alle Einträge aus der Tabelle 'laermdaten'."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM laermdaten;")
    conn.commit()
    conn.close()
    print("Alle Lärmdaten erfolgreich gelöscht!")

def delete_all_massnahmen():
    """Löscht alle Einträge aus der Tabelle 'massnahmen'."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM massnahmen;")
    conn.commit()
    conn.close()
    print("Alle Maßnahmen erfolgreich gelöscht!")

def import_laermdaten_from_csv(csv_file):
    """Importiert Lärmdaten aus einer CSV-Datei in die Datenbank."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Konvertiere Datum ins Format DD-MM-YYYY
            datum = datetime.strptime(row['datum'], "%Y-%m-%d").strftime("%d-%m-%Y") 
            cursor.execute("""
                INSERT INTO laermdaten (datum, beginn, ende, grund, verursacher, auswirkung)
                VALUES (?, ?, ?, ?, ?, ?);
            """, (datum, row['beginn'], row['ende'], row['grund'], row['verursacher'], row['auswirkung']))
    conn.commit()
    conn.close()
    print("Lärmdaten erfolgreich aus CSV importiert!")

def import_massnahmen_from_csv(csv_file):
    """Importiert Maßnahmen aus einer CSV-Datei in die Datenbank."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Konvertiere Datum ins Format DD-MM-YYYY
            datum = datetime.strptime(row['datum'], "%Y-%m-%d").strftime("%d-%m-%Y") 
            cursor.execute("""
                INSERT INTO massnahmen (datum, massnahme, ergebnis)
                VALUES (?, ?, ?);
            """, (datum, row['massnahme'], row['ergebnis']))
    conn.commit()
    conn.close()
    print("Maßnahmen erfolgreich aus CSV importiert!")
