INSERT INTO user (email, password, first_name, last_name, is_admin, is_approved)
VALUES
  ('admin@admin.com', 
  'pbkdf2:sha256:50000$Io4fJIjy$f1738f6c8b5be582c608e201c2d915a0387b4d97ca141b2dea8e30185e1f39ed',
  'admin',
  'admin',
  1,
  1),
  ('user@user.com',
  'pbkdf2:sha256:50000$Io4fJIjy$f1738f6c8b5be582c608e201c2d915a0387b4d97ca141b2dea8e30185e1f39ed',
  'user',
  'user',
  0,
  1);
