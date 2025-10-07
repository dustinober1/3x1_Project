# 3x1_Project

This project is a persistent random-tester for the Collatz (3x+1) conjecture. It generates very large random starting numbers, runs each through the Collatz sequence until they reach 1 (or a safety limit), and uses an efficient SQLite database to track tested numbers across runs.

## What it does

- Generates large random integers (default range: 10 billion to 1e33).
- Runs the Collatz sequence for each number, recording the number of steps and the highest peak encountered.
- **Efficiently stores tested numbers in a compact SQLite database using SHA-256 hashes** (32 bytes per entry).
- Uses batch inserts and session caching for optimal performance.
- Appends a human-readable summary of each session to `collatz_results_log.txt`.

## Files

- `3x1.py` - Main script with efficient SQLite backend. Runs non-interactively by default (1M tests).
- `collatz_tested.db` - SQLite database storing SHA-256 hashes of tested numbers (much more efficient than JSON).
- `collatz_results_log.txt` - Human-readable session summaries (appended each session).
- `migrate_to_sqlite.py` - Migration utility to convert legacy JSON data to SQLite.
- `3x1_json_backup.py` - Backup of the previous JSON-based version (for reference).
- `README.md` - This file.

## Storage Efficiency

The project now uses **SQLite with SHA-256 hashes** instead of JSON for tested numbers:

| Method | Storage per number | 2.14M numbers | Notes |
|--------|-------------------|---------------|-------|
| JSON (old) | ~36-40 bytes + overhead | 45.7 MB | Slow load times, high memory |
| SQLite (new) | ~32 bytes hash + DB overhead | 84.4 MB | Fast lookups, scalable, disk-backed |

**Why the DB is slightly larger but better:**
- JSON stores decimal strings with quotes and commas (compact but slow to load/search)
- SQLite stores raw 32-byte hashes with index structures (slightly larger but instant lookups)
- SQLite uses WAL mode for better concurrency and batch inserts for speed
- No need to load all numbers into memory — queries happen on disk

## Recent Changes

### v2.0 - SQLite Backend (Latest)
- ✅ Replaced JSON storage with efficient SQLite database
- ✅ Uses SHA-256 hashes for compact, fixed-size storage (32 bytes per number)
- ✅ Added batch inserts (commits every 5% for performance)
- ✅ Session caching to avoid redundant DB lookups
- ✅ Database auto-creates with optimized PRAGMA settings (WAL mode, 64MB cache)
- ✅ Migration script provided (`migrate_to_sqlite.py`)

### v1.0 - Non-interactive Mode
- Removed interactive prompt; automatically tests 1,000,000 numbers
- Added scheduled GitHub Actions workflow (runs every 4 hours)

## How to Run

### First Time Setup (Migration from JSON)

If you have an existing `collatz_tested_numbers.json` file:

```bash
python3 migrate_to_sqlite.py
```

This will:
- Read all numbers from the JSON file
- Import them into the new SQLite database
- Create a timestamped backup
- Show space savings and verification

### Normal Usage

Run the script with Python 3. It automatically tests 1,000,000 new numbers:

```bash
python3 3x1.py
```

**Performance:**
- Typical speed: ~4,000-5,000 tests/second
- 1M tests complete in ~3-4 minutes
- Progress updates every 5%
- Efficient batch commits reduce I/O

### Scheduled Runs

The project includes a GitHub Actions workflow (`.github/workflows/scheduled_collatz.yml`) that:
- Runs every 4 hours automatically
- Tests 1M new numbers each run
- Commits updated database and logs back to the repository
- Can be triggered manually via Actions tab

## Technical Details

### Database Schema

```sql
CREATE TABLE tested (
    hash BLOB PRIMARY KEY
) WITHOUT ROWID;

CREATE TABLE stats (
    key TEXT PRIMARY KEY,
    value TEXT
) WITHOUT ROWID;
```

### Hash Function

Numbers are hashed using SHA-256 of their decimal string representation:
```python
hash = hashlib.sha256(str(number).encode('utf-8')).digest()
```

This provides:
- Fixed 32-byte storage per number
- Deterministic hashing
- Astronomically low collision risk (~2^-256)
- Fast lookups via PRIMARY KEY index

### Performance Optimizations

- **WAL mode**: Better concurrency, allows reads during writes
- **PRAGMA synchronous=NORMAL**: Good speed/safety tradeoff  
- **64MB cache**: Keeps hot data in memory
- **Batch inserts**: Groups 1000 numbers per transaction
- **Session cache**: Avoids DB lookups for numbers tested in current session

## Migration Guide

If you're upgrading from the JSON version:

1. **Backup your data** (script does this automatically):
   ```bash
   cp collatz_tested_numbers.json collatz_tested_numbers.json.backup
   ```

2. **Run migration**:
   ```bash
   python3 migrate_to_sqlite.py
   ```

3. **Verify**:
   ```bash
   python3 3x1.py  # Should show correct count
   ```

4. **Optional - Delete old JSON** (after confirming everything works):
   ```bash
   rm collatz_tested_numbers.json
   ```

## Future Enhancements

- Add CLI arguments to override default test count
- Support environment variable for CI/test runs
- Add database vacuum/optimize command
- Consider Bloom filter for even faster duplicate checks
- Add database statistics and health check commands

## License

Open source - use for school projects, research, or fun!
```
# 3x1_Project
