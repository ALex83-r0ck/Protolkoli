import sqlite3
import pandas as pd 

def get_all_data():
    conn = sqlite3.connect('database/protokoll.db')
    df = pd.read_sql_query("SELECT * FROM laermdaten", conn)
    conn.close()
    return df

def analyse_dauer():
    df = get_all_data()

    df['beginn'] = pd.to_datetime(df['datum'] + ' ' + df['beginn'])
    df['ende'] = pd.to_datetime(df['datum'] + ' ' + df['ende'])
    df['dauer'] = (df['ende'] - df['beginn']).dt.total_seconds() / 60
    avg_dauer = df['dauer'].mean()
    print(f'Durchschnittliche Dauer: {avg_dauer:.2f} Minuten')
    return avg_dauer

def analyse_auswirkungen():
    df = get_all_data()
    # Auswirkung von 1 (leicht störend) - 5 (sehr störend)
    avg_auswirkung = df['auswirkung'].astype(float).mean()
    print(f'Durchschnittliche Auswirkungen: {avg_auswirkung:.2f}')
    return avg_auswirkung

def analyse_haeufigkeit():
    df = get_all_data()
    verursacher_haeufigkeit = df['verursacher'].value_counts()
    most_frequent_verursacher = verursacher_haeufigkeit.idxmax()
    freq = verursacher_haeufigkeit.max()
    print(f'Häufigster Verursacher: {most_frequent_verursacher} mit {freq} Vorkommen')
    return most_frequent_verursacher, freq