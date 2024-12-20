from cProfile import label
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
import numpy as np
from datetime import datetime
from database.database_setup import get_all_laermdaten, get_all_massnahmen
import os

_cached_data = None

def get_all_data():
    """
    Loads all data from the SQLite database and returns it as a Pandas DataFrame.

    If the data is empty, the function returns an empty DataFrame.
    """
    try:
        conn = sqlite3.connect('database/protokoll.db')
        query = "SELECT * FROM laermdaten"
        df = pd.read_sql_query(query, conn)
    except sqlite3.Error as e:
        print(f"Error reading data from the database: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

    if df.empty:
        print("Warning: No data found in the table.")
        return pd.DataFrame()

    required_columns = {'datum', 'beginn', 'ende'}
    if not required_columns.issubset(df.columns):
        missing_columns = required_columns - set(df.columns)
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    try:
        # Convert columns to datetime
        df['datum'] = pd.to_datetime(df['datum'], format='%d-%m-%Y', dayfirst=True)
        df['beginn'] = pd.to_datetime(df['datum'].astype(str) + ' ' + df['beginn'])
        df['ende'] = pd.to_datetime(df['datum'].astype(str) + ' ' + df['ende'])
    except ValueError as e:
        raise ValueError(f"Error converting columns to datetime: {e}")

    # Calculate duration in minutes
    df['dauer'] = (df['ende'] - df['beginn']).dt.total_seconds() / 60
    return df

def get_cached_data(force_reload=False):
    global _cached_data
    if _cached_data is None or force_reload:
        _cached_data = get_all_data()
    return _cached_data

def filter_zeiten(df):
    """
    Filtert nur die relevanten Spalten 'beginn' und 'ende' aus dem DataFrame.
    """
    if not {'beginn', 'ende'}.issubset(df.columns):
        raise ValueError("Die Spalten 'beginn' und 'ende' fehlen im DataFrame.")
    return df[['beginn', 'ende']]

def analyse_dauer(data):
    # Falls data eine Liste ist, in einen DataFrame umwandeln
    if isinstance(data, list):
        data = pd.DataFrame(data)

    print(data.columns)  # Zeigt die tatsächlichen Spaltennamen an

    # Überprüfe, ob die Spalten 'beginn' und 'ende' vorhanden sind
    if 'beginn' not in data.columns or 'ende' not in data.columns:
        raise ValueError("Die Spalten 'beginn' und 'ende' sind nicht im DataFrame vorhanden.")
    
    # Berechne die Dauer, falls noch nicht vorhanden
    if 'dauer' not in data.columns:
        data['dauer'] = (data['ende'] - data['beginn']).dt.total_seconds() / 60
    
    # Berechne den Durchschnitt
    durchschnitt = data['dauer'].mean()
    return durchschnitt if not np.isnan(durchschnitt) else 0

def analyse_auswirkungen(data):
    """
    Calculates the average impact of the disturbances (1 to 5).
    """
    if 'auswirkung' not in data.columns:
        print("Warning: 'auswirkung' column is missing in the data.")
        return 0

    return data['auswirkung'].astype(float).mean()

def analyse_haeufigkeit(data):
    """
    Finds the most frequent cause and its frequency.
    """
    if 'verursacher' not in data.columns:
        print("Warning: 'verursacher' column is missing in the data.")
        return None, 0

    verursacher_counts = data['verursacher'].value_counts()
    most_frequent_verursacher = verursacher_counts.idxmax()
    frequency = verursacher_counts.max()
    return most_frequent_verursacher, frequency

def analyse_daten(df):
    """
    Führt verschiedene Analysen auf dem DataFrame aus.
    """
    required_columns = {'verursacher', 'stoerung', 'dauer', 'datum'}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"Fehlende Spalten: {required_columns - set(df.columns)}")

    result = {
        "haeufigster_verursacher": df['verursacher'].mode().iloc[0] if not df['verursacher'].empty else None,
        "haeufigste_stoerung": df['stoerung'].mode().iloc[0] if not df['stoerung'].empty else None,
        "laengste_stoerung": df.loc[df['dauer'].idxmax()] if not df['dauer'].empty else None,
        "wochenauswertung": df.groupby(df['datum'].dt.isocalendar().week)['dauer'].sum().to_dict()
    }
    return result

def forecast_dauer(df, days=7):
    """
    Prognostiziert die durchschnittliche Dauer für die nächsten `days` Tage.
    """
    if 'datum' not in df.columns or 'dauer' not in df.columns:
        raise ValueError("Die Spalten 'datum' und 'dauer' fehlen im DataFrame.")

    df = df.dropna(subset=['datum', 'dauer'])
    df['ordinal_date'] = df['datum'].map(pd.Timestamp.toordinal)

    X = df[['ordinal_date']]
    y = df['dauer']

    model = LinearRegression()
    model.fit(X, y)

    future_days = np.array([df['ordinal_date'].max() + i for i in range(1, days + 1)]).reshape(-1, 1)
    predictions = model.predict(future_days)

    future_dates = [pd.Timestamp.fromordinal(int(d)) for d in future_days.flatten()]
    return pd.DataFrame({'datum': future_dates, 'dauer_prognose': predictions})

def plot_dauer_trend(df):
    """Plottet den Trend der Störungsdauer über die Zeit."""
    if 'datum' not in df.columns or 'dauer' not in df.columns:
        raise ValueError("Die Spalten 'datum' und 'dauer' fehlen im DataFrame.")

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='datum', y='dauer', markers='o', label='Dauer (Minuten)')
    plt.title("Trend der Störungsdauer über die Zeit der Erfassung.")
    plt.xlabel("Datum")
    plt.ylabel("Dauer (Minuten)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    os.makedirs('plots', exist_ok=True)
    plt.savefig("plots/plot_dauer_trend.png", dpi=100, bbox_inches="tight")

def plot_wochenauswertung(df):
    """
    Plottet die wöchentliche Summe der Störungsdauern.
    """
    if 'datum' not in df.columns or 'dauer' not in df.columns:
        raise ValueError("Die Spalten 'datum' und 'dauer' fehlen im DataFrame.")
    
    df['woche'] = df['datum'].dt.isocalendar().week
    wochen_daten = df.groupby('woche')['dauer'].sum().reset_index()
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=wochen_daten, x='woche', y='dauer', palette='viridis')
    plt.title("Wöchentliche Auswertung der Störungsdauer")
    plt.xlabel("Kalenderwoche")
    plt.ylabel("Gesamtdauer (Minuten)")
    plt.grid(axis='y')
    plt.tight_layout()
    os.makedirs('plots', exist_ok=True)
    plt.savefig("plots/plot_wochenauswertung.png", dpi=100, bbox_inches="tight")

def plot_dauer_histogram(df):
    """
    Erstellt ein Histogramm der Störungsdauern.
    """
    if 'dauer' not in df.columns:
        raise ValueError("Die Spalte 'dauer' fehlt im DataFrame.")
    
    plt.figure(figsize=(8, 6))
    sns.histplot(df['dauer'], bins=20, kde=True, color='blue')
    plt.title("Verteilung der Störungsdauern")
    plt.xlabel("Dauer (Minuten)")
    plt.ylabel("Häufigkeit")
    plt.grid(True)
    plt.tight_layout()
    os.makedirs('plots', exist_ok=True)
    plt.savefig("plots/plot_dauer_histogram.png", dpi=100, bbox_inches="tight")

def plot_auswirkung(df):
    """
    Plottet die durchschnittlichen Auswirkungen (1 bis 5).
    """
    if 'auswirkung' not in df.columns:
        raise ValueError("Die Spalte 'auswirkung' fehlt im DataFrame.")
    
    plt.figure(figsize=(6, 6))
    auswirkung_counts = df['auswirkung'].value_counts().sort_index()
    sns.barplot(x=auswirkung_counts.index, y=auswirkung_counts.values, palette='coolwarm')
    plt.title("Verteilung der Auswirkungen")
    plt.xlabel("Auswirkungslevel (1-5)")
    plt.ylabel("Häufigkeit")
    plt.grid(axis='y')
    plt.tight_layout()
    os.makedirs('plots', exist_ok=True)
    plt.savefig("plots/plot_auswirkung.png", dpi=100, bbox_inches="tight")

def plot_forecast(forecast_df):
    """
    Plottet die Prognose der Störungsdauern.
    """
    if 'datum' not in forecast_df.columns or 'dauer_prognose' not in forecast_df.columns:
        raise ValueError("Die Spalten 'datum' und 'dauer_prognose' fehlen im Prognosedatenframe.")
    
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=forecast_df, x='datum', y='dauer_prognose', marker='o', label='Prognose')
    plt.title("Prognose der Störungsdauern")
    plt.xlabel("Datum")
    plt.ylabel("Dauer (Minuten)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()
    plt.tight_layout()
    os.makedirs('plots', exist_ok=True)
    plt.savefig("plots/plot_forecast.png", dpi=100, bbox_inches="tight")

def plot_hauptzeiten(df):
    """
    Plottet die Häufigkeit der Ereignisse pro Stunde.
    """
    if 'beginn' not in df.columns:
        raise ValueError("Die Spalte 'beginn' fehlt im DataFrame.")

    df['stunde'] = df['beginn'].dt.hour
    hauptzeiten = df.groupby('stunde').size()

    plt.figure(figsize=(10, 6))
    plt.bar(hauptzeiten.index, hauptzeiten.values, color='skyblue', edgecolor='black')
    plt.title("Häufigkeit der Ereignisse pro Stunde")
    plt.xlabel("Stunde")
    plt.ylabel("Anzahl der Ereignisse")
    plt.grid(axis='y')
    plt.tight_layout()
    os.makedirs('plots', exist_ok=True)
    plt.savefig("plots/plot_hauptzeiten.png", dpi=100, bbox_inches="tight")

def plot_hauptzeiten_nach_20(df):
    """
    Plottet die Häufigkeit der Ereignisse nach 20 Uhr.
    """
    if 'beginn' not in df.columns:
        raise ValueError("Die Spalte 'beginn' fehlt im DataFrame.")

    df['stunde'] = df['beginn'].dt.hour
    nach_20 = df[df['stunde'] >= 20].groupby('stunde').size()

    plt.figure(figsize=(10, 6))
    plt.bar(nach_20.index, nach_20.values, color='orange', edgecolor='black')
    plt.title("Häufigkeit der Ereignisse nach 20 Uhr")
    plt.xlabel("Stunde")
    plt.ylabel("Anzahl der Ereignisse")
    plt.grid(axis='y')
    plt.tight_layout()
    os.makedirs('plots', exist_ok=True)
    plt.savefig("plots/plot_hauptzeiten_nach_20.png", dpi=100, bbox_inches="tight")

def plot_zeit_und_tag_heatmap(df):
    """
    Erstellt eine Heatmap der Ereignisse basierend auf Stunde und Tag.
    """
    if 'beginn' not in df.columns:
        raise ValueError("Die Spalte 'beginn' fehlt im DataFrame.")

    df['stunde'] = df['beginn'].dt.hour
    df['tag'] = df['beginn'].dt.day_name()
    heatmap_data = df.pivot_table(index='tag', columns='stunde', values='dauer', aggfunc='size', fill_value=0)

    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap='coolwarm', annot=True, fmt='d', linewidths=0.5)
    plt.title("Ereignisverteilung nach Stunde und Tag")
    plt.xlabel("Stunde")
    plt.ylabel("Tag")
    plt.tight_layout()
    os.makedirs('plots', exist_ok=True)
    plt.savefig("plots/plot_heatmap_zeit_tag.png", dpi=100, bbox_inches="tight")

def update_plot(self, width, height):
        figsize = (width / 100, height / 100)  # Passe Größe an Layout an
        plt.figure(figsize=figsize, dpi=100)
        # Erstelle oder lade den Plot hier
        plt.tight_layout()
        plt.savefig("dynamic_plot.png", dpi=100, bbox_inches="tight")
        plt.close()

# Daten laden und vorbereiten
df = get_cached_data()

# Trend der Störungsdauer
plot_dauer_trend(df)

# Wöchentliche Auswertung
plot_wochenauswertung(df)

# Histogramm der Störungsdauern
plot_dauer_histogram(df)

# Auswirkungen analysieren und plotten
plot_auswirkung(df)

# Prognose berechnen und plotten
forecast_df = forecast_dauer(df, days=14)
plot_forecast(forecast_df)

# Hauptzeiten analysieren
plot_hauptzeiten(df)

# Zeiten nach 20 Uhr analysieren
plot_hauptzeiten_nach_20(df)

# Heatmap der Stunden und Tage
plot_zeit_und_tag_heatmap(df)