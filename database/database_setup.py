import sqlite3
import logging


logger = logging.getLogger(__name__)

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
    logger.info("Datenbank und Tabellen erfolgreich erstellt.")

def insert_data(datum, beginn, ende, dauer, grund, verursacher, auswirkung):
    try:
        conn = sqlite3.connect('database/protokoll.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO laermdaten (datum, beginn, ende, dauer, grund, verursacher, auswirkung) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (datum, beginn, ende, dauer, grund, verursacher, auswirkung))
        conn.commit()
        logger.info("Daten erfolgreich hinzugefügt.")
    except sqlite3.IntegrityError:
        logger.warning("Ein Eintrag mit dem gleichen Datum und der gleichen Zeit existiert bereits.")
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
    logger.info(f"Eintrag {entry_id} erfolgreich aktualisiert.")

def delete_data(self, entry_id):
    conn = sqlite3.connect('database/protokoll.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM laermdaten WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    logger.warning(f"Eintrag {entry_id} erfolgreich gelöscht.")
    self.show_snackbar(f'Daten gelöscht: {entry_id}')

# Erstellung der db

create_database()

