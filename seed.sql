PRAGMA foreign_keys = OFF;

DELETE FROM messages;
DELETE FROM workout_categories;
DELETE FROM workouts;
DELETE FROM categories;
DELETE FROM users;

PRAGMA foreign_keys = ON;

INSERT INTO users (id, username, password_hash)
VALUES
  (1, 'anna', 'demo'),
  (2, 'matti', 'demo'),
  (3, 'liisa', 'demo');

INSERT INTO categories (id, name)
VALUES
  (1, 'voima'),
  (2, 'cardio'),
  (3, 'venyttely');

INSERT INTO workouts (id, user_id, date, type, duration, description)
VALUES
  (1, 1, '2026-01-10', 'voima', 60, 'Jalkatreeni salilla'),
  (2, 1, '2026-01-12', 'cardio', 45, 'Juoksulenkki'),
  (3, 2, '2026-01-11', 'voima', 50, 'Ylävartalo'),
  (4, 3, '2026-01-13', 'venyttely', 30, 'Kevyt palauttava');

INSERT INTO workout_categories (workout_id, category_id)
VALUES
  (1, 1),
  (2, 2),
  (4, 3);

INSERT INTO messages (workout_id, sender_id, receiver_id, content)
VALUES
  (1, 2, 1, 'Hyvä treeni! 💪'),
  (1, 3, 1, 'Kuulostaa rankalta'),
  (2, 1, 2, 'Lenkki kulki hyvin');
