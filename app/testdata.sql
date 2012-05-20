INSERT INTO "user"(username, password, email) VALUES('Anonymous', '-', '-');
INSERT INTO "user"(username, password, email) VALUES('Shish', '1f204934f622ca6c89f3cf98b98a55cf6dedf4cf', 'shish@shishnet.org');

INSERT INTO "comment"(page_owner_id, page_url, item_id, content) VALUES (1, 'http://www.commentonthis.net/static/demo.html', 'p3', 'here''s a comment');
INSERT INTO "comment"(page_owner_id, page_url, item_id, content) VALUES (1, 'http://www.commentonthis.net/static/demo.html', 'p3', 'here''s another comment on the same item');
INSERT INTO "comment"(page_owner_id, page_url, item_id, content) VALUES (1, 'http://www.commentonthis.net/static/demo.html', 'p4', 'comment on a different item');
