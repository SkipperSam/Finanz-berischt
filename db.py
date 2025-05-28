import sqlite3
from pathlib import Path

DB_FILE = "finanzguru_data.db"

def get_connection():
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = get_connection()
    cur = con.cursor()
    # Konten
    cur.execute("""
    CREATE TABLE IF NOT EXISTS konten (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """)
    # Kategorien
    cur.execute("""
    CREATE TABLE IF NOT EXISTS kategorien (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)
    # Zahlungen
    cur.execute("""
    CREATE TABLE IF NOT EXISTS zahlungen (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        betrag REAL NOT NULL,
        typ TEXT NOT NULL,
        datum TEXT NOT NULL,
        kategorie_id INTEGER,
        konto_id INTEGER,
        beschreibung TEXT,
        wiederkehrend INTEGER,
        FOREIGN KEY (kategorie_id) REFERENCES kategorien(id),
        FOREIGN KEY (konto_id) REFERENCES konten(id)
    )
    """)
    con.commit()
    # Standard-Konten
    cur.execute("INSERT OR IGNORE INTO konten (name) VALUES (?)", ("Girokonto",))
    cur.execute("INSERT OR IGNORE INTO konten (name) VALUES (?)", ("Bargeld",))
    # Standard-Kategorien
    cur.execute("INSERT OR IGNORE INTO kategorien (name) VALUES (?)", ("Miete",))
    cur.execute("INSERT OR IGNORE INTO kategorien (name) VALUES (?)", ("Lebensmittel",))
    cur.execute("INSERT OR IGNORE INTO kategorien (name) VALUES (?)", ("Gehalt",))
    cur.execute("INSERT OR IGNORE INTO kategorien (name) VALUES (?)", ("Sonstiges",))
    con.commit()
    con.close()

# --- Konten ---
def add_konto(name):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO konten (name) VALUES (?)", (name,))
    con.commit()
    con.close()

def update_konto(konto_id, new_name):
    con = get_connection()
    cur = con.cursor()
    cur.execute("UPDATE konten SET name = ? WHERE id = ?", (new_name, konto_id))
    con.commit()
    con.close()

def delete_konto(konto_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("UPDATE zahlungen SET konto_id = NULL WHERE konto_id = ?", (konto_id,))
    cur.execute("DELETE FROM konten WHERE id = ?", (konto_id,))
    con.commit()
    con.close()

def get_konten():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT id, name FROM konten ORDER BY name")
    return cur.fetchall()

# --- Kategorien ---
def add_kategorie(name):
    con = get_connection()
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO kategorien (name) VALUES (?)", (name,))
    con.commit()
    con.close()

def update_kategorie(kategorie_id, new_name):
    con = get_connection()
    cur = con.cursor()
    cur.execute("UPDATE kategorien SET name = ? WHERE id = ?", (new_name, kategorie_id))
    con.commit()
    con.close()

def delete_kategorie(kategorie_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("UPDATE zahlungen SET kategorie_id = NULL WHERE kategorie_id = ?", (kategorie_id,))
    cur.execute("DELETE FROM kategorien WHERE id = ?", (kategorie_id,))
    con.commit()
    con.close()

def get_kategorien():
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT id, name FROM kategorien ORDER BY name")
    return cur.fetchall()

# --- Zahlungen ---
def add_zahlung(betrag, typ, datum, kategorie_id, konto_id, beschreibung, wiederkehrend):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO zahlungen (betrag, typ, datum, kategorie_id, konto_id, beschreibung, wiederkehrend)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (betrag, typ, datum, kategorie_id, konto_id, beschreibung, int(bool(wiederkehrend))))
    con.commit()
    con.close()

def update_zahlung(zahlung_id, betrag, typ, datum, kategorie_id, konto_id, beschreibung, wiederkehrend):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        UPDATE zahlungen
        SET betrag = ?, typ = ?, datum = ?, kategorie_id = ?, konto_id = ?, beschreibung = ?, wiederkehrend = ?
        WHERE id = ?
    """, (betrag, typ, datum, kategorie_id, konto_id, beschreibung, int(bool(wiederkehrend)), zahlung_id))
    con.commit()
    con.close()

def delete_zahlung(zahlung_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("DELETE FROM zahlungen WHERE id = ?", (zahlung_id,))
    con.commit()
    con.close()

def get_zahlungen():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT z.*, 
               k.name AS kategorie_name,
               ko.name AS konto_name
        FROM zahlungen z
        LEFT JOIN kategorien k ON z.kategorie_id = k.id
        LEFT JOIN konten ko ON z.konto_id = ko.id
        ORDER BY z.datum DESC, z.id DESC
    """)
    return cur.fetchall()

def get_gesamtvermoegen():
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT SUM(CASE WHEN typ='Einnahme' THEN betrag ELSE -betrag END) as saldo
        FROM zahlungen
    """)
    result = cur.fetchone()
    return result["saldo"] if result and result["saldo"] is not None else 0.0

def get_zahlung_by_id(zahlung_id):
    con = get_connection()
    cur = con.cursor()
    cur.execute("""
        SELECT *
        FROM zahlungen
        WHERE id = ?
    """, (zahlung_id,))
    result = cur.fetchone()
    con.close()
    return result