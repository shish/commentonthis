DROP TABLE IF EXISTS cot_user CASCADE;
DROP TABLE IF EXISTS cot_item CASCADE;
DROP TABLE IF EXISTS cot_comment CASCADE;
DROP TABLE IF EXISTS cot_message CASCADE;
DROP TABLE IF EXISTS cot_session CASCADE;

CREATE TABLE cot_user (
	name TEXT UNIQUE NOT NULL PRIMARY KEY,
	password CHAR(40) NOT NULL,
	email TEXT UNIQUE NOT NULL,
	mailmode VARCHAR(8) NOT NULL DEFAULT 'all',
	description TEXT NOT NULL DEFAULT '',
	whitelist TEXT NOT NULL DEFAULT ''
);
CREATE TABLE cot_comment (
	id SERIAL NOT NULL PRIMARY KEY,
	item_host TEXT NOT NULL,
	item_path TEXT NOT NULL,
	item_name TEXT NOT NULL,
	item_user TEXT NOT NULL REFERENCES cot_user(name) ON UPDATE CASCADE,
	user_name TEXT NOT NULL REFERENCES cot_user(name) ON UPDATE CASCADE,
	date_posted TIMESTAMP NOT NULL DEFAULT now(),
	content TEXT NOT NULL,
	private BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE TABLE cot_message (
	id SERIAL NOT NULL PRIMARY KEY,
	user_from TEXT NOT NULL REFERENCES cot_user(name) ON UPDATE CASCADE,
	user_to TEXT NOT NULL REFERENCES cot_user(name) ON UPDATE CASCADE,
	date_posted TIMESTAMP NOT NULL DEFAULT now(),
	content TEXT NOT NULL
);
CREATE TABLE cot_session (
	session_id CHAR(128) UNIQUE NOT NULL,
	atime TIMESTAMP NOT NULL DEFAULT current_timestamp,
	data TEXT
);

CREATE UNIQUE INDEX cot_user__name__lower ON cot_user(lower(name));
CREATE UNIQUE INDEX cot_user__email__lower ON cot_user(lower(email));

INSERT INTO cot_user(name, password, email, mailmode) VALUES('Anonymous', '', '', 'none');
INSERT INTO cot_user(name, password, email, mailmode) VALUES('Shish', '6f90969f138be3c75101028711871a27972d1fe8', 'webmaster@shishnet.org', 'all');
