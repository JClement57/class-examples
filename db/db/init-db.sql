-- Insert data into user table
INSERT INTO user (first_name, last_name, email, password)
VALUES ('Fred', 'Ziffle', 'fred@ziffle.com', 'fred');

INSERT INTO user (first_name, last_name, email, password)
VALUES ('Zelda', 'Ziffle', 'zelda@ziffle.com', 'zelda');

INSERT INTO user (first_name, last_name, email, password)
VALUES ('Phil', 'Collins', 'phcollins@taylor.edu', 'phil');

-- Insert data into comment table.
INSERT INTO comment (id, body, user)
VALUES (1, 'A sample comment.', 'fred@ziffle.com');

INSERT INTO comment (id, body, user)
VALUES (2, 'Another lively comment.', 'zelda@ziffle.com');

INSERT INTO comment (id, body, user)
VALUES (3, 'Phil''s profound comment.', 'phcollins@taylor.edu');

INSERT INTO comment (id, body, user)
VALUES (4, 'Bible Gateway is a helpful partner.', 'phcollins@taylor.edu');

-- Insert data in to account table
INSERT INTO account (id, name, balance) VALUES (1, 'Fred''s Savings Account', 4000);
INSERT INTO account (id, name, balance) VALUES (2, 'Fred''s Checking Account', 600);
INSERT INTO account (id, name, balance) VALUES (3, 'Zelda''s Savings Account', 7565);
INSERT INTO account (id, name, balance) VALUES (4, 'Zelda''s Checking Account', 1435);
