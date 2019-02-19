INSERT INTO user (email, password, first_name, last_name)
VALUES
  ('admin@admin.com', 
  'pbkdf2:sha256:50000$Io4fJIjy$f1738f6c8b5be582c608e201c2d915a0387b4d97ca141b2dea8e30185e1f39ed',
  'admin',
  'admin'),
  ('user@user.com',
  'pbkdf2:sha256:50000$Io4fJIjy$f1738f6c8b5be582c608e201c2d915a0387b4d97ca141b2dea8e30185e1f39ed',
  'user',
  'user');

INSERT INTO property (name, owner_user_id)
VALUES
  ('Morro Bay',
  2),
  ('Mexico',
  2);

INSERT INTO user_to_property (user_id, property_id, is_admin)
VALUES
  (2,
  1,
  1),
  (2,
  2,
  0);
