-- Bankarstvo Database Setup Script

-- Disable foreign key checks temporarily for clean setup
SET FOREIGN_KEY_CHECKS = 0;

-- Create tables based on template
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `two_factor_auth` varchar(255) DEFAULT NULL,
  `account_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `last_login` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `currencies`;
CREATE TABLE `currencies` (
  `currency_code` varchar(3) NOT NULL,
  `currency_name` varchar(255) NOT NULL,
  PRIMARY KEY (`currency_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert some common currencies
INSERT INTO `currencies` VALUES 
('USD', 'US Dollar'),
('EUR', 'Euro'),
('GBP', 'British Pound'),
('JPY', 'Japanese Yen'),
('CNY', 'Chinese Yuan'),
('AFN', 'Afghani');

DROP TABLE IF EXISTS `accounts`;
CREATE TABLE `accounts` (
  `account_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `balance` decimal(20,2) DEFAULT '0.00',
  `account_type` varchar(255) DEFAULT NULL,
  `account_status` varchar(255) DEFAULT 'Active',
  `currency_code` varchar(3) DEFAULT NULL,
  `account_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`account_id`),
  KEY `user_id` (`user_id`),
  KEY `currency_code` (`currency_code`),
  CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `accounts_ibfk_2` FOREIGN KEY (`currency_code`) REFERENCES `currencies` (`currency_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `transactions`;
CREATE TABLE `transactions` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `from_account_id` int DEFAULT NULL,
  `to_account_id` int DEFAULT NULL,
  `amount` decimal(20,2) DEFAULT NULL,
  `transaction_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `transaction_type` varchar(255) DEFAULT NULL,
  `transaction_status` varchar(255) DEFAULT 'Completed',
  `description` text,
  PRIMARY KEY (`transaction_id`),
  KEY `from_account_id` (`from_account_id`),
  KEY `to_account_id` (`to_account_id`),
  CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`from_account_id`) REFERENCES `accounts` (`account_id`) ON DELETE CASCADE,
  CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`to_account_id`) REFERENCES `accounts` (`account_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `countries`;
CREATE TABLE `countries` (
  `code` char(2) NOT NULL,
  `name` varchar(255) NOT NULL,
  `currency` varchar(3) NOT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `recurringpayments`;
CREATE TABLE `recurringpayments` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `from_user_id` int DEFAULT NULL,
  `to_account_id` int DEFAULT NULL,
  `amount` decimal(20,2) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `frequency` enum('DAILY','WEEKLY','MONTHLY','YEARLY') DEFAULT NULL,
  `last_executed` date DEFAULT NULL,
  `status` enum('ACTIVE','PAUSED','COMPLETED','FAILED') DEFAULT 'ACTIVE',
  PRIMARY KEY (`payment_id`),
  KEY `from_user_id` (`from_user_id`),
  KEY `to_account_id` (`to_account_id`),
  CONSTRAINT `recurringpayments_ibfk_1` FOREIGN KEY (`from_user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `recurringpayments_ibfk_2` FOREIGN KEY (`to_account_id`) REFERENCES `accounts` (`account_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

DROP TABLE IF EXISTS `signed_documents`;
CREATE TABLE `signed_documents` (
  `document_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `document_type` varchar(255) DEFAULT NULL,
  `signature` text,
  `signed_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `validity` enum('valid','invalid','pending') DEFAULT 'pending',
  `additional_info` text,
  `document_hash` char(64) DEFAULT NULL,
  `image_data` text,
  PRIMARY KEY (`document_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `signed_documents_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Insert demo data
-- Create a demo user for testing (password is 'demo123')
INSERT INTO `user` VALUES (1, 'demo_user', 'demo@example.com', '$2b$12$Z/v5BhdXwxHhZog1OJDrvewwUdckGWUvw.BakG9.eKxhW1UITQzKO', NULL, CURRENT_TIMESTAMP, NULL);

-- Create accounts for the demo user
INSERT INTO `accounts` (`user_id`, `balance`, `account_type`, `account_status`, `currency_code`, `account_name`) 
VALUES 
(1, 1000.00, 'checking', 'Active', 'USD', 'Primary Checking'),
(1, 5000.00, 'savings', 'Active', 'USD', 'Savings Account'),
(1, 500.00, 'checking', 'Active', 'EUR', 'Euro Account');

-- Add sample transactions
INSERT INTO `transactions` (`from_account_id`, `to_account_id`, `amount`, `transaction_type`, `transaction_status`, `description`)
VALUES 
(NULL, 1, 500.00, 'deposit', 'Completed', 'Initial deposit'),
(NULL, 2, 5000.00, 'deposit', 'Completed', 'Savings deposit'),
(NULL, 3, 500.00, 'deposit', 'Completed', 'Euro account opening');

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;