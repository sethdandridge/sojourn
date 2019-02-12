DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS user_reservation_limits;
DROP TABLE IF EXISTS reservation;
DROP TABLE IF EXISTS reservation_status;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  is_admin INTEGER NOT NULL
);

CREATE TABLE user_reservation_limits (
  user_id INTEGER NOT NULL,
  max_upcoming INTEGER,
  max_duration INTEGER,
  max_per_month INTEGER,
  max_per_year INTEGER,
  max_days_in_advance INTEGER,
  min_days_between INTEGER,
  is_owner_presence_required INTEGER NOT NULL,
  is_owner_confirmation_requred INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE reservation_status (
  id INTEGER PRIMARY KEY,
  status TEXT NOT NULL
);

CREATE TABLE reservation (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  name TEXT,
  arrival TEXT NOT NULL,
  departure TEXT NOT NULL,
  reservation_status_id INTEGER NOT NULL,
  FOREIGN KEY (reservation_status_id) REFERENCES reservation_status (id)
);

INSERT INTO reservation_status (id, status)
VALUES 
  (1, "active"),
  (2, "pending approval"),
  (3, "deleted");
