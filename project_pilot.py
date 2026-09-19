project_pilot.py(6.9 kB)
#!/usr/bin/env python
# coding: utf-8

# # pilot_ai — Notebook
# 
# Regenerated Notebook
# 
# This notebook was regenerated on 2025-10-13 to provide a clean starting point. Replace or expand the cells below with project-specific analysis, experiments, or demonstrations.

# In[ ]:


import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class CodexIndex:
    def __init__(self, db_path: str = ".codex/index.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        # SQLite disables foreign keys by default
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._initialize()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _initialize(self) -> None:
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT UNIQUE NOT NULL,
            hash TEXT,
            language TEXT,
            indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS symbols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            kind TEXT,
            line INTEGER,
            FOREIGN KEY (file_id)
                REFERENCES files(id)
                ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS references (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol_id INTEGER NOT NULL,
            file_id INTEGER NOT NULL,
            line INTEGER,
            FOREIGN KEY (symbol_id)
                REFERENCES symbols(id)
                ON DELETE CASCADE,
            FOREIGN KEY (file_id)
                REFERENCES files(id)
                ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);
        CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name);
        CREATE INDEX IF NOT EXISTS idx_references_symbol ON references(symbol_id);
        """)
        self.conn.commit()

    def add_file(
        self,
        path: str,
        file_hash: Optional[str] = None,
        language: Optional[str] = None,
    ) -> int:
        """Upserts a file record and returns its database ID."""
        cursor = self.conn.execute(
            """
            INSERT INTO files (path, hash, language)
            VALUES (?, ?, ?)
            ON CONFLICT(path) DO UPDATE SET
                hash = excluded.hash,
                language = excluded.language,
                indexed_at = CURRENT_TIMESTAMP
            RETURNING id
            """,
            (str(path), file_hash, language),
        )
        file_id = cursor.fetchone()["id"]
        self.conn.commit()
        return file_id

    def add_symbols_bulk(
        self,
        file_id: int,
        symbols: List[Tuple[str, str, int]],
    ) -> None:
        """Efficiently batch-inserts symbols for a given file ID.
        
        `symbols` expects a list of tuples: `[(name, kind, line), ...]`
        """
        self.conn.executemany(
            """
            INSERT INTO symbols (file_id, name, kind, line)
            VALUES (?, ?, ?, ?)
            """,
            [(file_id, name, kind, line) for name, kind, line in symbols],
        )
        self.conn.commit()

    def add_reference(self, symbol_id: int, file_id: int, line: int) -> None:
        """Records a reference to a symbol."""
        self.conn.execute(
            """
            INSERT INTO references (symbol_id, file_id, line)
            VALUES (?, ?, ?)
            """,
            (symbol_id, file_id, line),
        )
        self.conn.commit()

    def search_symbol(self, name: str) -> List[Dict[str, Any]]:
        cursor = self.conn.execute(
            """
            SELECT
                symbols.id AS symbol_id,
                symbols.name,
                symbols.kind,
                symbols.line,
                files.path
            FROM symbols
            JOIN files ON symbols.file_id = files.id
            WHERE symbols.name LIKE ?
            ORDER BY files.path, symbols.line
            """,
            (f"%{name}%",),
        )
        return [dict(row) for row in cursor.fetchall()]

    def find_references(self, symbol_name: str) -> List[Dict[str, Any]]:
        """Finds all code locations referencing symbols matching the given name."""
        cursor = self.conn.execute(
            """
            SELECT
                s.name AS symbol_name,
                f_ref.path AS referencing_file,
                r.line AS line_number
            FROM references r
            JOIN symbols s ON r.symbol_id = s.id
            JOIN files f_ref ON r.file_id = f_ref.id
            WHERE s.name = ?
            ORDER BY f_ref.path, r.line
            """,
            (symbol_name,),
        )
        return [dict(row) for row in cursor.fetchall()]

    def close(self) -> None:
        self.conn.close()


if __name__ == "__main__":
    with CodexIndex(":memory:") as index:
        file_id = index.add_file(
            "src/main.py",
            file_hash="abc123",
            language="python",
        )

        index.add_symbols_bulk(
            file_id,
            [("CodexIndex", "class", 7), ("search_symbol", "method", 85)],
        )

        for result in index.search_symbol("Codex"):
            print(result)

<ElicitationsGroup message="Where would you like to take this script next?">
  <Elicitation label="Add SQLite FTS5 for full-text search" query="Implement SQLite FTS5 full-text search in codex_index.py to support fast multi-token and fuzzy symbol searching." />
  <Elicitation label="Integrate Python ast module parsing" query="Write a Python AST visitor function that automatically extracts classes, functions, and lines from source files to index using CodexIndex." />
</ElicitationsGroup>


# In[ ]:





# In[ ]:


# Environment info
import sys
import platform
import json
import os

info = {
    'python_version': sys.version.split('\n')[0],
    'platform': platform.platform(),
    'cwd': os.getcwd(),
    'files_in_cwd': os.listdir('.')[:50]  # sample
}
print(json.dumps(info, indent=2))


# In[ ]:


# Minimal demo function — replace with your project code
def hello_pilot_ai(name='World'):
    """Simple demo function to confirm notebook is running."""
    return f'Hello, {name}! This notebook is ready for pilot_ai work.'

if __name__ == '__main__':
    print(hello_pilot_ai('pilot_ai'))


# ## Next steps
# - Add project-specific imports and helper functions.
# - Load datasets (from repo or external sources) and run experiments.
# - Add visualization cells and save results into /notebook or a results/ 
