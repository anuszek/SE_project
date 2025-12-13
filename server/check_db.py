import sqlite3
import os

# Ścieżka do bazy (zakładając, że uruchamiasz z folderu server)
db_path = os.path.join("instance", "access_system.db")

if not os.path.exists(db_path):
    print("Błąd: Nie znaleziono pliku bazy!")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # PRAGMA table_info zwraca informacje o kolumnach
        columns = cursor.execute("PRAGMA table_info(employee);").fetchall()
        
        print(f"{'ID':<5} {'NAZWA KOLUMNY':<20} {'TYP':<10} {'NOT NULL?'}")
        print("-" * 50)
        
        for col in columns:
            # col to krotka: (cid, name, type, notnull, dflt_value, pk)
            cid, name, dtype, notnull, dflt, pk = col
            print(f"{cid:<5} {name:<20} {dtype:<10} {bool(notnull)}")
            
    except Exception as e:
        print("Błąd odczytu tabeli:", e)
    finally:
        conn.close()