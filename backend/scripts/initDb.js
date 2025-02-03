import {db, settings} from '../src/lib/server/db.js';

const sleepDataQuery = `
CREATE TABLE IF NOT EXISTS sleep_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    timestamp TEXT NOT NULL UNIQUE,
    light INTEGER NOT NULL,
    temperature REAL NOT NULL,
    motion BOOLEAN NOT NULL
  )
`;

db.prepare(sleepDataQuery).run();
const settingsQuery = `
CREATE TABLE IF NOT EXISTS settings (
id INTEGER PRIMARY KEY AUTOINCREMENT,
date TEXT NOT NULL,
bed_time TEXT NOT NULL,
wake_time TEXT NOT NULL
)
`
settings.prepare(settingsQuery).run();
console.log('Databases initialized successfully!');


