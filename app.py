from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Zum Verwalten von Flash-Nachrichten
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['DATA_BASE']='lager.db'

# Sicherstellen, dass der Upload-Ordner existiert
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Standard-Datenbankverbindung
def get_db_connection():
    conn = sqlite3.connect(app.config['DATA_BASE'])
    conn.row_factory = sqlite3.Row  
    return conn

# Route für die Startseite und Anzeige der Artikel
@app.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM lager').fetchall()
    conn.close()
    return render_template('index.html', items=items)

# Route für das Hinzufügen eines neuen Artikels
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method != 'POST':
        return render_template('add_item.html')
    
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
        image_filename = str(uuid.uuid4().hex)+"."+image_file.filename.rsplit('.', 1)[1].lower()
        stat_sheet_filename = str(uuid.uuid4().hex)+"."+stat_sheet_file.filename.rsplit('.', 1)[1].lower()
        image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        stat_sheet_file.save(os.path.join(app.config['UPLOAD_FOLDER'], stat_sheet_filename))

        conn = get_db_connection()
        conn.execute('INSERT INTO lager (name, menge, preis, bild, beschreibung, lagerort, stat_sheet) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (name, menge, preis, image_filename, beschreibung, lagerort, stat_sheet_filename))
        conn.commit()
        conn.close()

        flash('Artikel erfolgreich hinzugefügt!')
        return redirect(url_for('index'))
    
    flash('Bitte stellen Sie sicher, dass beide Bilder im richtigen Format vorliegen!')
    return redirect(url_for('add_item'))
    

# Route für das Suchen von Artikeln nach Name
@app.route('/search', methods=['GET'])
def search_item():
    search_term = request.args.get('search_term', '')
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM lager WHERE name LIKE ?', ('%' + search_term + '%',)).fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/sort/<sort_term>', methods=['GET'])
def sort(sort_term):
    print(sort_term)
    conn = get_db_connection()
    search_str = f"SELECT * FROM lager ORDER BY {str(sort_term).lower()}"
    items = conn.execute( search_str).fetchall()
    conn.close()
    return render_template('index.html', items=items)

# Funktion zur Überprüfung der Dateiendungen
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/connect_database', methods=['GET', 'POST'])
def connect_database():
    return render_template('connect_database.html')

@app.route('/item_view/<item_id>')
def item_view(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM lager WHERE id IS ?', ( item_id ,)).fetchone()
    conn.close()
    return render_template('item_view.html', item=item)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM lager WHERE id IS ?', (id, )).fetchall()
    conn.execute('DELETE FROM lager WHERE id IS ?', ( id ,)).fetchone()
    conn.commit()
    conn.close()
    
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item[0]['bild']))
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item[0]['stat_sheet']))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
