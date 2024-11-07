from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from datetime import datetime
from database.database_setup import create_database, insert_data, get_all_data, update_data, delete_data
from utils.pdf_generation import generiere_protokoll as pg_generiere_protokoll
from utils.data_processing import analyse_dauer as dp_analyse_dauer 
from utils.data_processing import analyse_auswirkungen as dp_analyse_auswirkung
from utils.data_processing import analyse_haeufigkeit as dp_analyse_haeufigkeit
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.textfield import MDTextField
import pandas as pd


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

class ProtokollApp(MDApp):
    def __init__(self, **kwargs):
        super(ProtokollApp, self).__init__(**kwargs)
        current_date, current_time = self.default_values()
        
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
        

    def erfasse_daten(self, datum, beginn, ende, dauer, grund, verursacher, auswirkung):
        """Daten erfassen und in die Datenbank einfügen"""
        start_datetime = datetime.strptime(f"{datum} {beginn}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{datum} {ende}", "%Y-%m-%d %H:%M")
        dauer = (end_datetime - start_datetime).total_seconds() / 60
        insert_data(datum, beginn, ende, dauer, grund, verursacher, auswirkung)
        print(f'Daten erfasst: {datum}, {beginn}, {ende}, Dauer: {dauer}, Grund: {grund}, Nachbar: {verursacher}, Auswirkungen: {auswirkung}')

    def aktualisiere_daten(self, entty_id, datum, beginn, ende, dauer, grund, verursacher, auswirkung):
        """Daten aktualisieren"""
        update_data(entty_id, datum, beginn, ende, dauer, grund, verursacher, auswirkung)
        print(f'Daten aktualisiert: {entty_id}, {datum}, {beginn}, {ende}, Dauer: {dauer}, Grund: {grund}, Nachbar: {verursacher}, Auswirkungen: {auswirkung}')

    def loesche_daten(self, entry_id):
        """Daten löschen"""
        delete_data(entry_id)
        print(f'Daten gelöscht: {entry_id}')

    def analyse_dauer(self):
        """Durchschnittliche Dauer analysieren"""
        avg_dauer = dp_analyse_dauer()
        self.root.avg_dauer_label = f'{avg_dauer:.2f} Minuten'
        #print(f'Durchschnittliche Dauer: {avg_dauer:.2f} Minuten')

    def analyse_auswirkung(self):
        """Durchschnittliche Auswirkungen analysieren"""
        avg_auswirkung = dp_analyse_auswirkung()
        self.root.ids.avg_auswirkung_label = f'{avg_auswirkung:.2f}'
        #print(f'Durchschnittliche Auswirkung: {avg_auswirkung:.2f}')

    def analyse_haeufigkeit(self):
        """Häufigster Verursacher analysieren"""
        verursacher, freq = dp_analyse_haeufigkeit()
        self.root.ids.haeufigster_verursacher_label = f"{verursacher} mit {freq} Vorkommen"
        #print(f'Häufigster Verursacher: {verursacher} mit {freq} Vorkommen')

    def generiere_protokoll(self):
        """Protokoll generieren"""
        data = get_all_data()
        df = pd.DataFrame(data)
        print(df.columns)
        pg_generiere_protokoll(df.to_dict(orient='records'))


if __name__ == '__main__':
    ProtokollApp().run()