DROP TABLE IF EXISTS "comment";
DROP TABLE IF EXISTS "user";
DROP TABLE IF EXISTS "session";

CREATE TABLE "user" (
	id SERIAL PRIMARY KEY,
	username TEXT UNIQUE NOT NULL,
	password char(40) NOT NULL,
	email TEXT NOT NULL
);
CREATE TABLE "comment" (
	id SERIAL PRIMARY KEY,
	page_owner_id INTEGER NOT NULL REFERENCES "user"(id),
	page_url TEXT NOT NULL,
	item_id TEXT NOT NULL,
	commenter_id INTEGER REFERENCES "user"(id),
	content TEXT NOT NULL,
	date_posted TIMESTAMP NOT NULL DEFAULT now(),
	private BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE TABLE "session" (
	session_id CHAR(128) UNIQUE NOT NULL,
	atime TIMESTAMP NOT NULL default current_timestamp,
	data TEXT
);
