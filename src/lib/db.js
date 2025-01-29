// ensure all database interactions use a centralized connection

import path from 'path';
import { fileURLToPath } from 'url';
import Database from 'better-sqlite3';

// Resolve the absolute path to the database file
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const dbPath = path.join(__dirname, '../../data/sleepData.db');

const db = new Database(dbPath);

export default db;
