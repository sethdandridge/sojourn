DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS property;
DROP TABLE IF EXISTS property_status;
DROP TABLE IF EXISTS user_to_property;
DROP TABLE IF EXISTS user_to_property_reservation_limits;
DROP TABLE IF EXISTS invite;
DROP TABLE IF EXISTS invite_reservation_limits;
DROP TABLE IF EXISTS reservation;
DROP TABLE IF EXISTS reservation_status;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL
);

CREATE TABLE property_status (
  id INTEGER PRIMARY KEY,
  status TEXT NOT NULL
);

CREATE TABLE property (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  owner_user_id INTEGER NOT NULL,
  status_id INTEGER NOT NULL DEFAULT 1,
  FOREIGN KEY (owner_user_id) REFERENCES user (id),
  FOREIGN KEY (status_id) REFERENCES property (status_id)
);

CREATE TABLE user_to_property (
  user_id INTEGER NOT NULL,
  property_id INTEGER NOT NULL,
  is_admin INTEGER NOT NULL DEFAULT 0,
  note TEXT
);

CREATE TABLE user_to_property_reservation_limits (
  user_id INTEGER NOT NULL,
  property_id INTEGER NOT NULL,
  max_upcoming INTEGER,
  max_duration INTEGER,
  max_per_month INTEGER,
  max_per_year INTEGER,
  max_days_in_advance INTEGER,
  min_days_between INTEGER,
  is_owner_presence_required INTEGER NOT NULL,
  is_owner_confirmation_requred INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (property_id) REFERENCES property (id)
);

CREATE TABLE invite (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  property_id INTEGER NOT NULL,
  email TEXT NOT NULL,
  note TEXT,
  FOREIGN KEY (property_id) REFERENCES property (id)
);

CREATE TABLE invite_reservation_limits (
  invite_id INTEGER NOT NULL,
  property_id INTEGER NOT NULL,
  max_upcoming INTEGER,
  max_duration INTEGER,
  max_per_month INTEGER,
  max_per_year INTEGER,
  max_days_in_advance INTEGER,
  min_days_between INTEGER,
  is_owner_presence_required INTEGER NOT NULL,
  is_owner_confirmation_requred INTEGER NOT NULL,
  FOREIGN KEY (invite_id) REFERENCES invite (id),
  FOREIGN KEY (property_id) REFERENCES property (id)
);


CREATE TABLE reservation_status (
  id INTEGER PRIMARY KEY,
  status TEXT NOT NULL
);

CREATE TABLE reservation (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  property_id INTEGER NOT NULL,
  name TEXT,
  arrival TEXT NOT NULL,
  departure TEXT NOT NULL,
  status_id INTEGER NOT NULL,
  created TEXT NOT NULL,
  FOREIGN KEY (status_id) REFERENCES reservation_status (id),
  FOREIGN KEY (user_id) REFERENCES user (id),
  FOREIGN KEY (property_id) REFERENCES property (id)
);

INSERT INTO reservation_status (id, status)
VALUES 
  (1, "approved"),
  (2, "pending approval"),
  (3, "denied"),
  (4, "canceled");

INSERT INTO property_status (id, status)
VALUES
  (0, "disabled"),
  (1, "active");
