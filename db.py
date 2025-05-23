import sqlite3
import bcrypt

def get_db():
    conn = sqlite3.connect("diabetes.db")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            data TEXT,
            prediction INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def create_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True, "Utilisateur créé avec succès"
    except sqlite3.IntegrityError:
        return False, "Nom d'utilisateur déjà pris"
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.checkpw(password.encode(), user[1]):
        return user[0]
    return None

def save_prediction(user_id, data, prediction):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO predictions (user_id, data, prediction) VALUES (?, ?, ?)",
                   (user_id, str(data), prediction))
    conn.commit()
    conn.close()

def get_predictions(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT data, prediction FROM predictions WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    # Convertir les prédictions bytes en int
    return [(data, int.from_bytes(pred, byteorder='little') if isinstance(pred, bytes) else int(pred)) 
            for data, pred in rows]

def get_predictions_with_dates(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT data, prediction, created_at 
        FROM predictions 
        WHERE user_id = ? 
        ORDER BY created_at DESC
    """, (user_id,))
    preds = cursor.fetchall()
    conn.close()
    return preds

def fix_existing_predictions():
    conn = get_db()
    cursor = conn.cursor()
    
    # Récupérer toutes les prédictions
    cursor.execute("SELECT rowid, prediction FROM predictions")
    rows = cursor.fetchall()
    
    for row in rows:
        rowid, pred = row
        if isinstance(pred, bytes):
            # Convertir bytes en int
            new_pred = int.from_bytes(pred, byteorder='little')
            cursor.execute("UPDATE predictions SET prediction = ? WHERE rowid = ?", (new_pred, rowid))
    
    conn.commit()
    conn.close()

# Exécuter une seule fois
fix_existing_predictions()