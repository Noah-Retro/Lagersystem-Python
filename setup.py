import sqlite3

# Verbindung zur Datenbank (die Datei wird erstellt, wenn sie noch nicht existiert)
conn = sqlite3.connect('lager.db')

# Erstelle einen Cursor zum Ausführen von SQL-Befehlen
cursor = conn.cursor()

# Erstelle die Tabelle 'lager', falls sie noch nicht existiert
cursor.execute('''
CREATE TABLE IF NOT EXISTS lager (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    menge INTEGER NOT NULL,
    preis REAL NOT NULL,
    bild TEXT NOT NULL,
    beschreibung TEXT NOT NULL,
    lagerort TEXT NOT NULL,
    stat_sheet TEXT NOT NULL
)
''')

# Schließe die Verbindung zur Datenbank
conn.commit()
conn.close()

print("Datenbank und Tabelle wurden erfolgreich erstellt!")
