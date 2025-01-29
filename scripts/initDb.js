import db from '../src/lib/db.js';

const query = `
CREATE TABLE IF NOT EXISTS sleep_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL UNIQUE,
    light INTEGER NOT NULL,
    temperature REAL NOT NULL,
    motion BOOLEAN NOT NULL
  )
`;

db.prepare(query).run();
console.log('Database initialized successfully!');
