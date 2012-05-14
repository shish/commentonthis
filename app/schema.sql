CREATE TABLE account (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
	password char(40) NOT NULL
);
CREATE TABLE comment (
    id SERIAL PRIMARY KEY,
	page_owner_id INTEGER NOT NULL REFERENCES account(id),
	page_url TEXT NOT NULL,
	item_id TEXT NOT NULL,
	commenter_id INTEGER REFERENCES account(id),
	content TEXT NOT NULL,
	date_posted TIMESTAMP NOT NULL DEFAULT now(),
	private BOOLEAN NOT NULL DEFAULT FALSE
);
