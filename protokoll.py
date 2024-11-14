from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar
from kivy.graphics import Rotate 
from datetime import datetime
from database.database_setup import create_database, insert_data, get_all_data, update_data, delete_data
from utils.pdf_generation import generiere_protokoll as pg_generiere_protokoll
from utils.data_processing import analyse_dauer as dp_analyse_dauer 
from utils.data_processing import analyse_auswirkungen as dp_analyse_auswirkung
from utils.data_processing import analyse_haeufigkeit as dp_analyse_haeufigkeit
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField
import pandas as pd
import os

import logging
log_directory = 'data/logs'
log_file_path = os.path.join(log_directory, 'app.log')
os.makedirs(log_directory, exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ],
    filename=log_file_path
)
logger = logging.getLogger(__name__)

class RootWidget(BoxLayout):
    datum = ObjectProperty()
    beginn = ObjectProperty()
    ende = ObjectProperty()
    avg_dauer = ObjectProperty()
    avg_auswirkung = ObjectProperty()
    haeufigster_verursacher = ObjectProperty()
    dauer = ObjectProperty() 
    grund = ObjectProperty()
    verursacher = ObjectProperty()
    auswirkung = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_kv_post(self, base_widget):
        app = MDApp.get_running_app()
        Clock.schedule_once(lambda dt: app.set_default_values(), 0)


class VerticalLabel(MDLabel):
    def __init__(self, **kwargs):
        super(VerticalLabel, self).__init__(**kwargs)
        self.bind(size=self._update_rotation, pos=self._update_rotation)
        with self.canvas.before:
            self.rot = Rotate(angel=270, origin=self.center)

    def _update_rotation(self, *args):
        self.rot.origin = self.center

    def create_label(self, message):
        label = VerticalLabel()
        label.text = (message)
        label.font_size = '18sp'
        label.size_hint = (1, None)
        label.texture_update()
        label.size = label.texture_size
        label.halign = "center"  # Horizontale Ausrichtung
        label.valign = "middle"  # Vertikale Ausrichtung
        return label

    # Funktion zum Anzeigen der Snackbar
    def show_snackbar(self, message):
        snackbar = MDSnackbar()

        # Erstelle das Label mit der Funktion
        label = self.create_label(message)

        # Setze das Label als Inhalt der Snackbar

        snackbar.content = label
        snackbar.add_widget(snackbar.content)
    
        # Weitere Einstellungen für die Snackbar
        snackbar.duration = 3
        snackbar.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        snackbar.size_hint = (0.15, 0.1)
        snackbar.md_bg_color = self.theme_cls.primary_color  # Hintergrundfarbe der Snackbar
        snackbar.text_color = [1, 0, 0, 1]  # Textfarbe der Snackbar (rot)
    
        # Öffne die Snackbar
        snackbar.open()


class ProtokollApp(MDApp):
    def __init__(self, **kwargs):
        super(ProtokollApp, self).__init__(**kwargs)
        current_date, current_time = self.default_values()
        self.label = VerticalLabel()
        
    def build(self):
        create_database()
        return RootWidget() # Diese RootWidget-Instanz wird durch die .kv-Datei definiert

    def on_start(self):
        Clock.schedule_once(self.set_default_values)  # Warten, bis das Layout vollständig geladen ist
        
    def default_values(self):
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        return current_date, current_time

    def set_default_values(self, *args):
        """Stellt sicher, dass die TextInputs gesetzt werden, nachdem das Layout geladen ist"""
        current_date, current_time = self.default_values()
        self.root.datum.text = current_date
        self.root.beginn.text = current_time
        self.root.ende.text = current_time
        

    def erfasse_daten(self, datum, beginn, ende, grund, verursacher, auswirkung):
        """Daten erfassen und in die Datenbank einfügen"""
        start_datetime = datetime.strptime(f"{datum} {beginn}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{datum} {ende}", "%Y-%m-%d %H:%M")
        dauer = (end_datetime - start_datetime).total_seconds() / 60
        insert_data(datum, beginn, ende, dauer, grund, verursacher, auswirkung)
        self.label.show_snackbar(f'Daten erfasst: {datum}, {beginn}, {ende}, Art der Störung: {grund}, Nachbar: {verursacher}, Auswirkung: {auswirkung}')

    def aktualisiere_daten(self, entty_id, datum, beginn, ende, dauer, grund, verursacher, auswirkung):
        """Daten aktualisieren"""
        try:
            update_data(entty_id, datum, beginn, ende, dauer, grund, verursacher, auswirkung)
            self.label.show_snackbar(f'Daten aktualisiert: {entty_id}, {datum}, {beginn}, {ende}, Dauer: {dauer}, Art der Störung: {grund}, Nachbar: {verursacher}, Auswirkung: {auswirkung}')
        except Exception as e:
            self.label.show_snackbar(f'Fehler beim Aktualisieren der Daten: {e}')

    def loesche_daten(self, entry_id):
        """Daten löschen"""
        try:
            delete_data(entry_id)
            self.label.show_snackbar(f'Daten gelöscht: {entry_id}')
        except Exception as e:
            self.label.show_snackbar(f'Fehler beim Löschen der Daten: {e}')

    def analyse_dauer(self):
        """Durchschnittliche Dauer analysieren"""
        avg_dauer = dp_analyse_dauer(self)
        self.root.avg_dauer_label = f'{avg_dauer:.2f} Minuten'
        self.label.show_snackbar(f'  Durchschnittliche Dauer: {avg_dauer:.2f} Minuten')

    def analyse_auswirkung(self):
        """Durchschnittliche Auswirkungen analysieren"""
        avg_auswirkung = dp_analyse_auswirkung(self)
        self.root.ids.avg_auswirkung_label = f'{avg_auswirkung:.2f}'
        self.label.show_snackbar(f' Durchschnittliche Auswirkung: {avg_auswirkung:.2f}')

    def analyse_haeufigkeit(self):
        """Häufigster Verursacher analysieren"""
        verursacher, freq = dp_analyse_haeufigkeit(self)
        self.root.ids.haeufigster_verursacher_label = f"{verursacher} mit {freq} Vorkommen"
        self.label.show_snackbar(f'  Häufigster Verursacher:  {verursacher} = {freq}')

    def generiere_protokoll(self):
        """Protokoll generieren"""
        data = get_all_data()
        df = pd.DataFrame(data)
        print(df.columns)
        pg_generiere_protokoll(df.to_dict(orient='records'))

    
    
if __name__ == '__main__':
    ProtokollApp().run()