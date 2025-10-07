#!/usr/bin/env python3
"""
Migration script to convert legacy JSON storage to efficient SQLite database.
This script reads the old collatz_tested_numbers.json file and imports all 
tested numbers into the new SQLite database using compact SHA-256 hashes.
"""

import json
import os
import sys
import sqlite3
import hashlib
from datetime import datetime


def hash_number(n: int) -> bytes:
    """Generate a compact SHA-256 hash of a number for storage."""
    return hashlib.sha256(str(n).encode('utf-8')).digest()


def migrate_json_to_sqlite(json_path='collatz_tested_numbers.json', 
                           db_path='collatz_tested.db',
                           backup=True):
    """
    Migrate from JSON to SQLite database.
    
    Args:
        json_path: Path to the legacy JSON file
        db_path: Path to the new SQLite database
        backup: If True, create a backup of existing DB before migration
    """
    print("="*70)
    print("COLLATZ DATABASE MIGRATION: JSON → SQLite")
    print("="*70)
    
    # Check if JSON file exists
    if not os.path.exists(json_path):
        print(f"\n⚠️  JSON file not found: {json_path}")
        print("   Nothing to migrate. Starting with fresh database.")
        return
    
    print(f"\n📂 Reading JSON file: {json_path}")
    
    # Load JSON data
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        numbers = data.get('tested_numbers', [])
        all_time_stats = data.get('all_time_stats', {})
        
        print(f"   ✓ Found {len(numbers):,} tested numbers")
        print(f"   ✓ Found all-time statistics")
        
    except Exception as e:
        print(f"   ❌ Error reading JSON: {e}")
        sys.exit(1)
    
    # Backup existing database if requested
    backup_path = None
    if backup and os.path.exists(db_path):
        backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n💾 Creating backup: {backup_path}")
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"   ✓ Backup created")
    
    # Initialize SQLite database
    print(f"\n🗄️  Initializing SQLite database: {db_path}")
    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('PRAGMA synchronous=NORMAL;')
    conn.execute('PRAGMA cache_size=-64000;')  # 64MB cache
    
    # Create tables
    conn.execute('''CREATE TABLE IF NOT EXISTS tested (
        hash BLOB PRIMARY KEY
    ) WITHOUT ROWID''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS stats (
        key TEXT PRIMARY KEY,
        value TEXT
    ) WITHOUT ROWID''')
    
    conn.commit()
    print("   ✓ Database initialized")
    
    # Import numbers in batches
    print(f"\n🔄 Importing {len(numbers):,} numbers...")
    print("   (This may take a few minutes for large datasets)")
    
    batch_size = 10000
    total_imported = 0
    duplicates_skipped = 0
    
    for i in range(0, len(numbers), batch_size):
        batch = numbers[i:i + batch_size]
        hashes = [(hash_number(n),) for n in batch]
        
        # Use INSERT OR IGNORE to skip duplicates
        cursor = conn.executemany('INSERT OR IGNORE INTO tested (hash) VALUES (?)', hashes)
        imported_in_batch = cursor.rowcount
        total_imported += imported_in_batch
        duplicates_skipped += (len(batch) - imported_in_batch)
        
        if (i + batch_size) % 100000 == 0 or (i + batch_size) >= len(numbers):
            progress = min(100, ((i + batch_size) / len(numbers)) * 100)
            print(f"   Progress: {progress:5.1f}% | {total_imported:,} imported | "
                  f"{duplicates_skipped:,} duplicates skipped")
        
        # Commit periodically
        if (i + batch_size) % 50000 == 0:
            conn.commit()
    
    conn.commit()
    print(f"   ✓ Imported {total_imported:,} unique numbers")
    
    # Import statistics
    if all_time_stats:
        print(f"\n📊 Importing all-time statistics...")
        conn.execute(
            'INSERT OR REPLACE INTO stats (key, value) VALUES (?, ?)',
            ('all_time_stats', json.dumps(all_time_stats))
        )
        conn.commit()
        print("   ✓ Statistics imported")
    
    # Verify database
    print(f"\n✅ Verifying database...")
    cursor = conn.execute('SELECT COUNT(*) FROM tested')
    db_count = cursor.fetchone()[0]
    print(f"   Database contains: {db_count:,} tested numbers")
    
    conn.close()
    
    # Final summary
    print(f"\n{'='*70}")
    print("✓ MIGRATION COMPLETE!")
    print(f"{'='*70}")
    print(f"\n📈 Summary:")
    print(f"   Numbers migrated: {total_imported:,}")
    print(f"   Duplicates skipped: {duplicates_skipped:,}")
    print(f"   Database size: {os.path.getsize(db_path) / 1024 / 1024:.2f} MB")
    
    if os.path.exists(json_path):
        json_size = os.path.getsize(json_path) / 1024 / 1024
        db_size = os.path.getsize(db_path) / 1024 / 1024
        savings = ((json_size - db_size) / json_size * 100) if json_size > 0 else 0
        print(f"   Original JSON size: {json_size:.2f} MB")
        print(f"   Space savings: {savings:.1f}%")
    
    print(f"\n💡 Next steps:")
    print(f"   1. Test the new system: python3 3x1.py")
    print(f"   2. If everything works, you can delete: {json_path}")
    print(f"   3. Keep the backup until you're confident: {backup_path if backup else 'N/A'}")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate Collatz tested numbers from JSON to SQLite'
    )
    parser.add_argument(
        '--json',
        default='collatz_tested_numbers.json',
        help='Path to legacy JSON file (default: collatz_tested_numbers.json)'
    )
    parser.add_argument(
        '--db',
        default='collatz_tested.db',
        help='Path to new SQLite database (default: collatz_tested.db)'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup of existing database'
    )
    
    args = parser.parse_args()
    
    migrate_json_to_sqlite(
        json_path=args.json,
        db_path=args.db,
        backup=not args.no_backup
    )
