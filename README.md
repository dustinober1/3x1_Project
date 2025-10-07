```markdown
# 3x1_Project

This project is a persistent random-tester for the Collatz (3x+1) conjecture. It generates very large random starting numbers, runs each through the Collatz sequence until they reach 1 (or a safety limit), and keeps a persistent log so numbers aren't re-tested across runs.

## What it does

- Generates large random integers (default range in the script: 10 billion to 1e33-ish).
- Runs the Collatz sequence for each number, recording the number of steps and the highest peak encountered.
- Persists all tested numbers to `collatz_tested_numbers.json` so future runs skip duplicates.
- Appends a human-readable summary of each session to `collatz_results_log.txt`.

## Files

- `3x1.py` - Main script. Previously interactive; updated to run non-interactively by default.
- `collatz_tested_numbers.json` - JSON database of all unique numbers tested so far (auto-created/updated by the script).
- `collatz_results_log.txt` - Human-readable session summaries (appended each session).
- `README.md` - This file.

## Recent change (automatic default run)

The script was updated to remove the interactive prompt asking how many numbers to test. It now automatically tests 1,000,000 new random numbers when executed. The change preserves all existing logging and behavior (no data loss). The startup message now clearly indicates this non-interactive default.

This update was verified by running the script in the project workspace; it completed a full session of 1,000,000 new tests, saved the updated JSON database, and appended a session summary to `collatz_results_log.txt`.

## How to run

Run the script with Python 3. It's designed to run non-interactively and will automatically test 1,000,000 new numbers:

```bash
python3 3x1.py
```

Notes:
- The run may take several minutes depending on CPU speed. The script prints progress updates every 5%.
- The `collatz_tested_numbers.json` file can grow large over time. Keep an eye on disk usage if you run many sessions.

## Next steps / suggestions

- Add a small CLI (argparse) to allow overriding the default `1_000_000` tests without editing the script.
- Support an environment variable (e.g., `COLLATZ_NUM_TESTS`) to quickly run shorter smoke-tests in CI or development.
- Consider storing only hashed values or using a compact database (e.g., SQLite or LMDB) if the `tested_numbers` set grows too large for memory.

If you'd like, I can implement a CLI override or env-var soon — say the word and I'll add it.
```
# 3x1_Project