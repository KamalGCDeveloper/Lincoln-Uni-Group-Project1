-- -----------------------------------------------------
-- Schema voting_management
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS voting_management;
CREATE SCHEMA voting_management;
USE voting_management;

-- -----------------------------------------------------
-- Drop Tables if they exist
-- -----------------------------------------------------
DROP TABLE IF EXISTS `votes`;
DROP TABLE IF EXISTS `competitors`;
DROP TABLE IF EXISTS `competitions`;
DROP TABLE IF EXISTS `users`;

-- -----------------------------------------------------
-- Table `voting_management`.`users`
-- -----------------------------------------------------
CREATE TABLE `users` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50) NOT NULL,
  `password_hash` CHAR(64) NOT NULL,
  `email` VARCHAR(320) NOT NULL,
  `first_name` VARCHAR(50),
  `last_name` VARCHAR(50),
  `location` VARCHAR(50),
  `user_image` VARCHAR(255) NULL,
  `user_description` VARCHAR(255) NULL,
  `role` ENUM('voter', 'scrutineer', 'admin', 'super_admin') NOT NULL DEFAULT 'voter',
  `status` ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
  PRIMARY KEY (`user_id`),
  UNIQUE (`username`),
  UNIQUE (`email`)
);

-- -----------------------------------------------------
-- Table `voting_management`.`competitions`
-- -----------------------------------------------------
CREATE TABLE `competitions` (
  `competition_id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(255) NOT NULL,
  `category` VARCHAR(255) NOT NULL,
  `competition_description` TEXT NOT NULL,
  `start_date` TIMESTAMP NOT NULL,
  `end_date` TIMESTAMP NOT NULL,
  `is_public` BOOLEAN DEFAULT FALSE,
  `competition_image` VARCHAR(255) NULL,
  `result_finalised` BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (`competition_id`)
);

-- -----------------------------------------------------
-- Table `voting_management`.`competitors`
-- -----------------------------------------------------
CREATE TABLE `competitors` (
  `competitor_id` INT NOT NULL AUTO_INCREMENT,
  `competition_id` INT,
  `competitor_name` VARCHAR(50) NOT NULL,
  `competitor_description` TEXT NOT NULL,
  `competitor_image` VARCHAR(255) NULL,
  PRIMARY KEY (`competitor_id`),
  FOREIGN KEY (`competition_id`) REFERENCES `competitions`(`competition_id`) ON DELETE CASCADE
);

-- -----------------------------------------------------
-- Table `voting_management`.`votes`
-- -----------------------------------------------------
CREATE TABLE `votes` (
  `vote_id` INT NOT NULL AUTO_INCREMENT,
  `competitor_id` INT NOT NULL,
  `competition_id` INT NOT NULL,
  `user_id` INT NOT NULL,
  `ip_address` VARCHAR(45) NOT NULL,
  `voted_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` ENUM('valid', 'invalid') NOT NULL DEFAULT 'valid',
  PRIMARY KEY (`vote_id`),
  FOREIGN KEY (`competitor_id`) REFERENCES `competitors`(`competitor_id`) ON DELETE CASCADE,
  FOREIGN KEY (`competition_id`) REFERENCES `competitions`(`competition_id`) ON DELETE CASCADE,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`) ON DELETE CASCADE,
  UNIQUE (user_id, competition_id)
);
