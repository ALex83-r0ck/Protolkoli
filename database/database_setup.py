import sqlite3

def create_database():
    conn = sqlite3.connect('database/protokoll.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS laermdaten (
                   id INTEGER PRIMARY KEY,
                   datum TEXT,
                   beginn TEXT,
                   ende TEXT,
                   dauer TEXT,
                   grund TEXT,
                   verursacher TEXT,
                   auswirkung INTEGER CHECK(auswirkung BETWEEN 1 AND 5),
                   UNIQUE(datum, beginn, verursacher))''')  # Verhindert doppelte Einträge
    conn.commit()
    conn.close()

def insert_data(datum, beginn, ende, dauer, grund, verursacher, auswirkung):
    try:
        conn = sqlite3.connect('database/protokoll.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO laermdaten (datum, beginn, ende, dauer, grund, verursacher, auswirkung) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (datum, beginn, ende, dauer, grund, verursacher, auswirkung))
        conn.commit()
        print("Daten erfolgreich hinzugefügt.")
    except sqlite3.IntegrityError:
        print("Ein Eintrag mit dem gleichen Datum und der gleichen Zeit existiert bereits.")
    finally:
        conn.close()

def get_all_data():
    with sqlite3.connect('database/protokoll.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM laermdaten")
        data = cursor.fetchall()
    return data


def update_data(entry_id, datum, beginn, ende, dauer, grund, verursacher, auswirkung):
    conn = sqlite3.connect('database/protokoll.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE laermdaten 
                      SET datum = ?, beginn = ?, ende = ?, dauer = ?, grund = ?, verursacher = ?, auswirkung = ?
                      WHERE id = ?''', (datum, beginn, ende, dauer, grund, verursacher, auswirkung, entry_id))
    conn.commit()
    conn.close()
    print(f"Eintrag {entry_id} erfolgreich aktualisiert.")

def delete_data(entry_id):
    conn = sqlite3.connect('database/protokoll.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM laermdaten WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    print(f"Eintrag {entry_id} erfolgreich gelöscht.")

# Erstellung der db
create_database()
