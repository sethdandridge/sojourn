DROP TABLE IF EXISTS "user" CASCADE;
DROP TABLE IF EXISTS property_status CASCADE;
DROP TABLE IF EXISTS property CASCADE;
DROP TABLE IF EXISTS user_to_property CASCADE;
DROP TABLE IF EXISTS user_to_property_reservation_limits CASCADE;
DROP TABLE IF EXISTS invite CASCADE;
DROP TABLE IF EXISTS invite_reservation_limits CASCADE;
DROP TABLE IF EXISTS reservation CASCADE;
DROP TABLE IF EXISTS reservation_status CASCADE;

CREATE TABLE "user" (
  id SERIAL PRIMARY KEY,
  email VARCHAR(320) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  first_name VARCHAR(255) NOT NULL,
  last_name VARCHAR(255) NOT NULL,
  is_confirmed BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE property_status (
  id INTEGER PRIMARY KEY,
  status VARCHAR(255) NOT NULL
);

CREATE TABLE property (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  owner_user_id INTEGER NOT NULL REFERENCES "user" (id) ON DELETE CASCADE,
  status_id INTEGER NOT NULL DEFAULT 1 REFERENCES property_status (id)
);

CREATE TABLE user_to_property (
  user_id INTEGER NOT NULL REFERENCES "user" (id) ON DELETE CASCADE,
  property_id INTEGER NOT NULL REFERENCES property (id) ON DELETE CASCADE,
  is_admin BOOLEAN NOT NULL DEFAULT FALSE,
  note VARCHAR(255)
);

CREATE TABLE user_to_property_reservation_limits (
  user_id INTEGER NOT NULL REFERENCES "user" (id) ON DELETE CASCADE,
  property_id INTEGER NOT NULL REFERENCES property (id) ON DELETE CASCADE,
  max_upcoming INTEGER CHECK (max_upcoming >= 0),
  max_duration INTEGER CHECK (max_duration >= 0),
  max_per_month INTEGER CHECK (max_per_month >= 0),
  max_per_year INTEGER CHECK (max_per_year >= 0),
  max_days_in_advance INTEGER CHECK (max_days_in_advance >= 0),
  min_days_between INTEGER CHECK (min_days_between >= 0),
  is_owner_presence_required BOOLEAN NOT NULL DEFAULT FALSE,
  is_owner_confirmation_required BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE invite (
  id SERIAL PRIMARY KEY,
  property_id INTEGER NOT NULL REFERENCES property (id) ON DELETE CASCADE,
  email VARCHAR(320) NOT NULL,
  note VARCHAR(255)
);

CREATE TABLE invite_reservation_limits (
  invite_id INTEGER NOT NULL REFERENCES invite (id) ON DELETE CASCADE,
  max_upcoming INTEGER CHECK (max_upcoming >= 0),
  max_duration INTEGER CHECK (max_duration >= 0),
  max_per_month INTEGER CHECK (max_per_month >= 0),
  max_per_year INTEGER CHECK (max_per_year >= 0),
  max_days_in_advance INTEGER CHECK (max_days_in_advance >= 0),
  min_days_between INTEGER CHECK (min_days_between >= 0),
  is_owner_presence_required BOOLEAN NOT NULL DEFAULT FALSE,
  is_owner_confirmation_required BOOLEAN NOT NULL DEFAULT FALSE
);


CREATE TABLE reservation_status (
  id INTEGER PRIMARY KEY,
  status VARCHAR(255) NOT NULL
);

CREATE TABLE reservation (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES "user" (id) ON DELETE CASCADE,
  property_id INTEGER NOT NULL REFERENCES property (id) ON DELETE CASCADE,
  name VARCHAR(255),
  arrival DATE NOT NULL,
  departure DATE NOT NULL CHECK (departure > arrival),
  status_id INTEGER NOT NULL REFERENCES reservation_status (id),
  created TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO reservation_status (id, status)
VALUES 
  (1, 'approved'),
  (2, 'pending approval'),
  (3, 'denied'),
  (4, 'canceled');

INSERT INTO property_status (id, status)
VALUES
  (0, 'disabled'),
  (1, 'active');
