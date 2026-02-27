PRAGMA foreign_keys = ON;

DELETE FROM messages;
DELETE FROM workout_categories;
DELETE FROM workouts;
DELETE FROM users;


INSERT INTO users (username, password_hash)
VALUES
  ('anna', 'demo'),
  ('matti', 'demo'),
  ('liisa', 'demo');


INSERT INTO workouts (user_id, date, type, duration, description)
VALUES
  (1, '2026-01-10', 'voima', 60, 'Jalkatreeni salilla'),
  (1, '2026-01-12', 'cardio', 45, 'Juoksulenkki'),
  (2, '2026-01-11', 'voima', 50, 'Ylävartalo'),
  (3, '2026-01-13', 'venyttely', 30, 'Kevyt palauttava'),
  (1, '2026-01-15', 'cardio', 70, 'Pitkä rauhallinen lenkki, syke pysyi matalana');


INSERT INTO workout_categories (workout_id, category_id)
VALUES
  (1, 4),
  (2, 1),
  (3, 4),
  (4, 5),
  (5, 1),
  (5, 6);


INSERT INTO messages (workout_id, sender_id, receiver_id, content)
VALUES
  (1, 2, 1, 'Hyvä treeni!'),
  (1, 3, 1, 'Kuulostaa rankalta'),
  (2, 1, 2, 'Vau! hyvä!');