-- MySQL initialization script
CREATE DATABASE IF NOT EXISTS insider_threat_new
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE insider_threat_new;

-- Grant privileges
GRANT ALL PRIVILEGES ON insider_threat_new.* TO 'itbis_user'@'%';
FLUSH PRIVILEGES;
