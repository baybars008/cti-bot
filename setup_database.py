#!/usr/bin/env python3
"""
CTI-BOT: Advanced Cyber Threat Intelligence Platform
===================================================

Created by: Alihan Şahin | Baybars
Threat & Security Researcher

Website: https://alihansahin.com
GitHub: https://github.com/baybars008

Database Setup Script
====================
Creates necessary database tables and initializes the system.
"""

import sqlite3
import os
from datetime import datetime

def create_database():
    """Veritabanını ve tabloları oluştur"""
    
    # instance dizinini oluştur
    if not os.path.exists("instance"):
        os.makedirs("instance")
        print("✅ instance dizini oluşturuldu")
    
    # Veritabanı bağlantısı
    conn = sqlite3.connect("instance/data.db")
    cur = conn.cursor()
    
    print("📊 Veritabanı tabloları oluşturuluyor...")
    
    # Posts tablosu
    cur.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        company_name TEXT,
        country TEXT,
        sector TEXT,
        impact_level TEXT,
        website TEXT,
        description TEXT,
        hack_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✅ posts tablosu oluşturuldu")
    
    # Groups tablosu
    cur.execute('''
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        description TEXT,
        website TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✅ groups tablosu oluşturuldu")
    
    # Wallets tablosu
    cur.execute('''
    CREATE TABLE IF NOT EXISTS wallets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        address TEXT UNIQUE,
        balance REAL,
        balance_usd REAL,
        blockchain TEXT,
        family TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✅ wallets tablosu oluşturuldu")
    
    # Transactions tablosu
    cur.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_id INTEGER,
        hash TEXT UNIQUE,
        time TIMESTAMP,
        amount REAL,
        amount_usd REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (wallet_id) REFERENCES wallets (id)
    )
    ''')
    print("✅ transactions tablosu oluşturuldu")
    
    # Kripto değişim tablosu
    cur.execute('''
    CREATE TABLE IF NOT EXISTS kripto_degisim (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarih TIMESTAMP,
        cuzdanno TEXT,
        degismeden_once REAL,
        degisimden_sonra REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✅ kripto_degisim tablosu oluşturuldu")
    
    # HackedCompany tablosu (Flask model ile uyumlu)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS hacked_company (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        country TEXT,
        sector TEXT,
        impact_level TEXT,
        hack_date TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("✅ hacked_company tablosu oluşturuldu")
    
    # Değişiklikleri kaydet
    conn.commit()
    conn.close()
    
    print("✅ Veritabanı kurulumu tamamlandı!")

def check_database():
    """Veritabanı durumunu kontrol et"""
    if not os.path.exists("instance/data.db"):
        print("❌ Veritabanı bulunamadı!")
        return False
    
    conn = sqlite3.connect("instance/data.db")
    cur = conn.cursor()
    
    # Tabloları listele
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    
    print("📊 Mevcut tablolar:")
    for table in tables:
        table_name = table[0]
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cur.fetchone()[0]
        print(f"  📋 {table_name}: {count} kayıt")
    
    conn.close()
    return True

if __name__ == "__main__":
    print("🔧 CTI-BOT Veritabanı Kurulumu")
    print("=" * 40)
    
    # Veritabanını oluştur
    create_database()
    
    # Durumu kontrol et
    print("\n🔍 Veritabanı durumu:")
    check_database()
    
    print("\n✅ Kurulum tamamlandı!")
    print("💡 Şimdi 'python app.py' ile uygulamayı başlatabilirsiniz")

