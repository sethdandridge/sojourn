DROP TABLE IF EXISTS "user" CASCADE;
DROP TABLE IF EXISTS property_status CASCADE;
DROP TABLE IF EXISTS property CASCADE;
DROP TABLE IF EXISTS user_to_property CASCADE;
DROP TABLE IF EXISTS user_to_property_reservation_limits CASCADE;
DROP TABLE IF EXISTS invite CASCADE;
DROP TABLE IF EXISTS invite_reservation_limits CASCADE;
DROP TABLE IF EXISTS reservation CASCADE;
DROP TABLE IF EXISTS reservation_status CASCADE;
DROP TABLE IF EXISTS property_log CASCADE;

CREATE TABLE "user" (
  id SERIAL PRIMARY KEY,
  email VARCHAR(320) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  first_name VARCHAR(255) NOT NULL,
  last_name VARCHAR(255) NOT NULL,
  is_confirmed BOOLEAN NOT NULL DEFAULT FALSE
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

CREATE TABLE property_log (
  id SERIAL PRIMARY KEY,
  logged TIMESTAMP NOT NULL DEFAULT NOW(),
  property_id INTEGER NOT NULL REFERENCES property (id) ON DELETE CASCADE,
  user_id INTEGER NOT NULL REFERENCES "user" (id) ON DELETE CASCADE,
  message VARCHAR(512) NOT NULL
);

CREATE OR REPLACE FUNCTION log_reservation_cancelled() RETURNS TRIGGER AS
$$
  BEGIN
    INSERT INTO property_log(property_id, user_id, message)
    VALUES (
      new.property_id,
      new.user_id,
      CONCAT(
        '''s ',
        new.departure - new.arrival,
        ' night reservation (',
        TO_CHAR(new.arrival, 'Dy FMMM/FMDD/YY'),
        '–',
        TO_CHAR(new.departure, 'Dy FMMM/FMDD/YY'),
        ') was canceled.' 
      )
    );
    RETURN NEW;
  END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER reservation_canceled AFTER UPDATE ON reservation
  FOR EACH ROW
  WHEN ( (OLD.status_id IN (1,2)) AND (NEW.status_id = 4) )
  EXECUTE PROCEDURE log_reservation_cancelled();

CREATE OR REPLACE FUNCTION log_property_created() RETURNS TRIGGER AS
$$
  BEGIN
    INSERT INTO property_log(property_id, user_id, message)
    VALUES (
      new.id,
      new.owner_user_id,
      ' created this property.'
    );
    RETURN NEW;
  END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER property_created AFTER INSERT ON property
  FOR EACH ROW EXECUTE PROCEDURE log_property_created();

CREATE OR REPLACE FUNCTION log_reservation_created() RETURNS TRIGGER AS 
$$
  BEGIN
    INSERT INTO property_log(property_id, user_id, message)
    VALUES (
      new.property_id,
      new.user_id,
      CONCAT(
        ' booked a ',
        new.departure - new.arrival,
        ' night reservation (',
        TO_CHAR(new.arrival, 'Dy FMMM/FMDD/YY'),
        '–',
        TO_CHAR(new.departure, 'Dy FMMM/FMDD/YY'),
        ').',
        CASE
          WHEN new.status_id = 2 THEN ' Owner approval is required.'
        END
      )
    );
    RETURN NEW;
  END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER reservation_created AFTER INSERT ON reservation
  FOR EACH ROW EXECUTE PROCEDURE log_reservation_created();

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

-- INSERT INTO "user" (first_name, last_name, email, password)
-- VALUES
-- ('Seth', 'Dandridge', 'sethdan@gmail.com', 'pbkdf2:sha256:50000$RSFSs9gk$a043e05e9221d5509ffaf944859cedf0c894d7aa63b699bba7f1660a4dea6fac');
