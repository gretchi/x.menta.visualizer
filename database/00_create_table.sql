CREATE TABLE tweets (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        fav INTEGER NOT NULL,
        rt INTEGER NOT NULL,
        tweet TEXT,
        created_at TIMESTAMP NOT NULL
);
