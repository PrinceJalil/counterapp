import sqlite3
import random
from datetime import datetime, timedelta
import os

# Sesuaikan dengan path database Anda
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "database.db")

def generate_dummy_data():
    # Pastikan folder database ada
    if not os.path.exists(os.path.dirname(DB_PATH)):
        os.makedirs(os.path.dirname(DB_PATH))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Buat tabel jika belum ada
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT (datetime('now', '+7 hours')),
            class_name TEXT,
            count_in INTEGER
        )
    ''')
    
    # Atur tanggal mulai dan akhir
    start_date = datetime(2025, 6, 20)
    end_date = datetime.now()
    
    classes = ["Apple", "Orange"]
    
    current_date = start_date
    total_inserted = 0
    
    print(f"Menambahkan data dari {start_date.strftime('%d-%m-%Y')} sampai {end_date.strftime('%d-%m-%Y')}...")
    
    # Loop untuk setiap hari di rentang waktu
    while current_date.date() <= end_date.date():
        for cls in classes:
            # Buat jumlah random untuk tiap kelas per harinya
            count = random.randint(500, 1000)
            
            # Buat timestamp dengan jam acak (antara jam 8 pagi - 6 sore) agar terlihat natural
            random_hour = random.randint(8, 18)
            random_minute = random.randint(0, 59)
            random_second = random.randint(0, 59)
            
            timestamp = current_date.replace(hour=random_hour, minute=random_minute, second=random_second)
            
            cursor.execute(
                "INSERT INTO history_logs (timestamp, class_name, count_in) VALUES (?, ?, ?)",
                (timestamp.strftime("%Y-%m-%d %H:%M:%S"), cls, count)
            )
            total_inserted += 1
            
        current_date += timedelta(days=1)
        
    conn.commit()
    conn.close()
    
    print(f"Berhasil menambahkan {total_inserted} baris data dummy ke dalam database!")

if __name__ == "__main__":
    generate_dummy_data()
