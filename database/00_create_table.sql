CREATE TABLE IF NOT EXISTS tweets (
        id INTEGER NOT NULL PRIMARY KEY,
        account TEXT NOT NULL,
        fav INTEGER NOT NULL,
        rt INTEGER NOT NULL,
        tweet TEXT,
        created_at TIMESTAMP NOT NULL
);
