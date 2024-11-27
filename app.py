from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Zum Verwalten von Flash-Nachrichten
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Sicherstellen, dass der Upload-Ordner existiert
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Standard-Datenbankverbindung
def get_db_connection():
    conn = sqlite3.connect('lager.db')
    conn.row_factory = sqlite3.Row  # Um auf die Spalten wie Dictionary zuzugreifen
    return conn

# Route für die Startseite und Anzeige der Artikel
@app.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM lager').fetchall()
    conn.close()
    return render_template('index.html', items=items)

# Route für das Hinzufügen eines neuen Artikels
@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        menge = request.form['menge']
        preis = request.form['preis']
        beschreibung = request.form['beschreibung']
        lagerort = request.form['lagerort']
        
        image_file = request.files['bild']
        stat_sheet_file = request.files['stat_sheet']
        
        if not name or not menge or not preis or not beschreibung or not lagerort:
            flash('Alle Felder müssen ausgefüllt sein!')
            return redirect(url_for('add_item'))

        if image_file and allowed_file(image_file.filename) and stat_sheet_file and allowed_file(stat_sheet_file.filename):
            image_filename = str(uuid.uuid4().hex)
            stat_sheet_filename = str(uuid.uuid4().hex)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            stat_sheet_file.save(os.path.join(app.config['UPLOAD_FOLDER'], stat_sheet_filename))

            conn = get_db_connection()
            conn.execute('INSERT INTO lager (name, menge, preis, bild, beschreibung, lagerort, stat_sheet) VALUES (?, ?, ?, ?, ?, ?, ?)',
                         (name, menge, preis, image_filename, beschreibung, lagerort, stat_sheet_filename))
            conn.commit()
            conn.close()

            flash('Artikel erfolgreich hinzugefügt!')
            return redirect(url_for('index'))
        else:
            flash('Bitte stellen Sie sicher, dass beide Bilder im richtigen Format vorliegen!')
            return redirect(url_for('add'))

    return render_template('add_item.html')

# Route für das Suchen von Artikeln nach Name
@app.route('/search', methods=['GET'])
def search_item():
    search_term = request.args.get('search_term', '')
    conn = get_db_connection()
    print("!!!!!"+search_term+"!!!!!")
    items = conn.execute('SELECT * FROM lager WHERE name LIKE ?', ('%' + search_term + '%',)).fetchall()
    conn.close()
    return render_template('index.html', items=items)

# Funktion zur Überprüfung der Dateiendungen
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/connect_database')
def connect_database():
    return "Datenbank verbinden"


@app.route('/admin_page')
def admin_page():
    # Logik für die Admin-Seite
    return render_template('admin_page.html')

if __name__ == '__main__':
    app.run(debug=True)
