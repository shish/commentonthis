INSERT INTO cot_user(name, password, email, mailmode) VALUES('E-Xample', '6f90969f138be3c75101028711871a27972d1fe8', 'spam@shishnet.org', 'none');

INSERT INTO cot_comment(item_host, item_path, item_name, item_user, user_name, content) VALUES('http://www.commentonthis.net', '/about/demo', 'lorem', 'Shish',          'E-Xample', 'here is a comment');
INSERT INTO cot_comment(item_host, item_path, item_name, item_user, user_name, content) VALUES('http://www.commentonthis.net', '/about/demo', 'erroris', 'Shish',        'E-Xample', 'here is a second comment');
INSERT INTO cot_comment(item_host, item_path, item_name, item_user, user_name, content) VALUES('http://www.commentonthis.net', '/about/get-started', 'section', 'Shish', 'E-Xample', 'and a comment on something different');
