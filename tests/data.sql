INSERT INTO "user" (email, password, first_name, last_name)
VALUES
  ('admin@admin.com', 
  'pbkdf2:sha256:50000$Io4fJIjy$f1738f6c8b5be582c608e201c2d915a0387b4d97ca141b2dea8e30185e1f39ed',
  'admin',
  'admin'),
  ('user@user.com',
  'pbkdf2:sha256:50000$Io4fJIjy$f1738f6c8b5be582c608e201c2d915a0387b4d97ca141b2dea8e30185e1f39ed',
  'user',
  'user'),
  ('notguest@notguest.com',
  'pbkdf2:sha256:50000$Io4fJIjy$f1738f6c8b5be582c608e201c2d915a0387b4d97ca141b2dea8e30185e1f39ed',
  'notguest',
  'notguest'),
  ('limited@limited.com',
  'pbkdf2:sha256:50000$Io4fJIjy$f1738f6c8b5be582c608e201c2d915a0387b4d97ca141b2dea8e30185e1f39ed',
  'limited',
  'limited'),
  ('unlimited@unlimited.com',
  'pbkdf2:sha256:50000$Io4fJIjy$f1738f6c8b5be582c608e201c2d915a0387b4d97ca141b2dea8e30185e1f39ed',
  'unlimited',
  'unlimited');

INSERT INTO property (name, owner_user_id)
VALUES
  ('Morro Bay',
  1),
  ('Mexico',
  1);

INSERT INTO user_to_property (user_id, property_id, is_admin)
VALUES
  (1, 1, TRUE),
  (1, 2, TRUE),
  (2, 1, FALSE),
  (2, 2, FALSE),
  (4, 1, FALSE),
  (5, 1, FALSE);

INSERT INTO user_to_property_reservation_limits (user_id, property_id, max_upcoming, max_duration, max_per_month, max_per_year, max_days_in_advance, min_days_between, is_owner_presence_required, is_owner_confirmation_required)
VALUES
  (4, 1, 1, 1, 1, 1, 1, 10, True, True);

INSERT INTO user_to_property_reservation_limits (user_id, property_id, max_upcoming, max_duration, max_per_month, max_per_year, max_days_in_advance, min_days_between, is_owner_presence_required, is_owner_confirmation_required)
VALUES
  (5, 1, NULL, NULL, NULL, NULL, NULL, NULL, False, False);

INSERT INTO invite (property_id, email)
VALUES
  (1, 'invited@invited.com');

INSERT INTO invite_reservation_limits (invite_id, max_upcoming, max_duration, max_per_month, max_per_year, max_days_in_advance, min_days_between, is_owner_presence_required, is_owner_confirmation_required)
VALUES
  (1, NULL, NULL, NULL, NULL, NULL, NULL, False, False);
