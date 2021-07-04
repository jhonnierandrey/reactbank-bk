-- reactbank.db is required

CREATE TABLE IF NOT EXISTS users (
    id INTEGER,
    name TEXT NOT NULL,
    lastName TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    balance NUMERIC NOT NULL DEFAULT 1000.00,
    PRIMARY KEY(id));

CREATE UNIQUE INDEX email ON users (email);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount NUMERIC NOT NULL,
    type TEXT NOT NULL,
    description TEXT NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id));