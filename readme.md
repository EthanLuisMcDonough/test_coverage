# Flang node test coverage tool

Requires SQLite (min ver 3.31.1) and Python 3 (min ver 3.8.10). 

1. `git clone https://github.com/EthanLuisMcDonough/test_coverage`
2. `cd test_coverage`
3. `sqlite3 database.db<db.schema`
4. Create a file named `config.json` and set ìts contents to `{ "llvm_root": "YOUR_FLANG_PATH" }`
5. `python3 run_tests.py`
6. `sqlite database.db`
7. Query gathered data.  Some examples can be found in `sample_queries.sql`

*Note: at time of writing, this project depends on a plugin that is not yet upstreamed in LLVM's repository*