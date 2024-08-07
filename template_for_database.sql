-- MySQL dump 10.13  Distrib 8.0.35, for Win64 (x86_64)
--
-- Host: localhost    Database: banking_app
-- ------------------------------------------------------
-- Server version	8.0.35

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `accounts`
--

DROP TABLE IF EXISTS `accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
  CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`),
  CONSTRAINT `accounts_ibfk_2` FOREIGN KEY (`currency_code`) REFERENCES `currencies` (`currency_code`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `accounts`
--

LOCK TABLES `accounts` WRITE;
/*!40000 ALTER TABLE `accounts` DISABLE KEYS */;
INSERT INTO `accounts` VALUES (7,4,284.00,'checking','Active','AFN','asdadsa'),(8,5,NULL,'checking','Active','AFN','sadasdasdsadsad'),(9,NULL,0.00,'checking','Active','AFN','saff'),(10,5,134.00,'checking','Active','AFN','blablabla');
/*!40000 ALTER TABLE `accounts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `countries`
--

DROP TABLE IF EXISTS `countries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `countries` (
  `code` char(2) NOT NULL,
  `name` varchar(255) NOT NULL,
  `currency` varchar(3) NOT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `countries`
--

LOCK TABLES `countries` WRITE;
/*!40000 ALTER TABLE `countries` DISABLE KEYS */;
/*!40000 ALTER TABLE `countries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `currencies`
--

DROP TABLE IF EXISTS `currencies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `currencies` (
  `currency_code` varchar(3) NOT NULL,
  `currency_name` varchar(255) NOT NULL,
  PRIMARY KEY (`currency_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `currencies`
--

LOCK TABLES `currencies` WRITE;
/*!40000 ALTER TABLE `currencies` DISABLE KEYS */;
INSERT INTO `currencies` VALUES ('AED','UAE Dirham'),('AFN','Afghani'),('ALL','Lek'),('AMD','Armenian Dram'),('ANG','Netherlands Antillean Guilder'),('AOA','Kwanza'),('ARS','Argentine Peso'),('AUD','Australian Dollar'),('AWG','Aruban Florin'),('AZN','Azerbaijan Manat'),('BAM','Convertible Mark'),('BBD','Barbados Dollar'),('BDT','Taka'),('BGN','Bulgarian Lev'),('BHD','Bahraini Dinar'),('BIF','Burundi Franc'),('BMD','Bermudian Dollar'),('BND','Brunei Dollar'),('BOB','Boliviano'),('BRL','Brazilian Real'),('BSD','Bahamian Dollar'),('BWP','Pula'),('BYN','Belarusian Ruble'),('BZD','Belize Dollar'),('CAD','Canadian Dollar'),('CDF','Congolese Franc'),('CHF','Swiss Franc'),('CLP','Chilean Peso'),('CNY','Yuan Renminbi'),('COP','Colombian Peso'),('CRC','Costa Rican Colon'),('CVE','Cabo Verde Escudo'),('CZK','Czech Koruna'),('DJF','Djibouti Franc'),('DKK','Danish Krone'),('DOP','Dominican Peso'),('DZD','Algerian Dinar'),('EGP','Egyptian Pound'),('ERN','Nakfa'),('ETB','Ethiopian Birr'),('EUR','Euro'),('FJD','Fiji Dollar'),('GBP','Pound Sterling'),('GEL','Lari'),('GHS','Ghana Cedi'),('GIP','Gibraltar Pound'),('GMD','Dalasi'),('GNF','Guinean Franc'),('GTQ','Quetzal'),('GYD','Guyana Dollar'),('HKD','Hong Kong Dollar'),('HNL','Lempira'),('HRK','Kuna'),('HUF','Forint'),('IDR','Rupiah'),('ILS','New Israeli Sheqel'),('INR','Indian Rupee'),('IQD','Iraqi Dinar'),('IRR','Iranian Rial'),('ISK','Iceland Krona'),('JMD','Jamaican Dollar'),('JOD','Jordanian Dinar'),('JPY','Yen'),('KES','Kenyan Shilling'),('KGS','Som'),('KHR','Riel'),('KMF','Comorian Franc'),('KPW','North Korean Won'),('KRW','Won'),('KWD','Kuwaiti Dinar'),('KYD','Cayman Islands Dollar'),('KZT','Tenge'),('LAK','Lao Kip'),('LBP','Lebanese Pound'),('LKR','Sri Lanka Rupee'),('LRD','Liberian Dollar'),('LYD','Libyan Dinar'),('MAD','Moroccan Dirham'),('MDL','Moldovan Leu'),('MGA','Malagasy Ariary'),('MKD','Denar'),('MMK','Kyat'),('MNT','Tugrik'),('MOP','Pataca'),('MRU','Ouguiya'),('MUR','Mauritius Rupee'),('MVR','Rufiyaa'),('MWK','Malawi Kwacha'),('MXN','Mexican Peso'),('MYR','Malaysian Ringgit'),('MZN','Mozambique Metical'),('NGN','Naira'),('NIO','Cordoba Oro'),('NOK','Norwegian Krone'),('NPR','Nepalese Rupee'),('NZD','New Zealand Dollar'),('OMR','Rial Omani'),('PEN','Sol'),('PGK','Kina'),('PHP','Philippine Peso'),('PKR','Pakistan Rupee'),('PLN','Zloty'),('PYG','Guarani'),('QAR','Qatari Rial'),('RON','Romanian Leu'),('RSD','Serbian Dinar'),('RUB','Russian Ruble'),('RWF','Rwanda Franc'),('SAR','Saudi Riyal'),('SBD','Solomon Islands Dollar'),('SCR','Seychelles Rupee'),('SDG','Sudanese Pound'),('SEK','Swedish Krona'),('SGD','Singapore Dollar'),('SHP','Saint Helena Pound'),('SLL','Leone'),('SOS','Somali Shilling'),('SRD','Surinam Dollar'),('SSP','South Sudanese Pound'),('STN','Dobra'),('SYP','Syrian Pound'),('SZL','Lilangeni'),('THB','Baht'),('TJS','Somoni'),('TMT','Turkmenistan New Manat'),('TND','Tunisian Dinar'),('TOP','PaÔÇÖanga'),('TRY','Turkish Lira'),('TTD','Trinidad and Tobago Dollar'),('TZS','Tanzanian Shilling'),('UAH','Hryvnia'),('UGX','Uganda Shilling'),('USD','US Dollar'),('UYU','Peso Uruguayo'),('UZS','Uzbekistan Sum'),('VES','Bol├¡var'),('VND','Dong'),('VUV','Vatu'),('WST','Tala'),('XAF','CFA Franc BEAC'),('XCD','East Caribbean Dollar'),('XOF','CFA Franc BCEAO'),('XPF','CFP Franc'),('YER','Yemeni Rial'),('ZAR','Rand'),('ZMW','Zambian Kwacha'),('ZWL','Zimbabwe Dollar');
/*!40000 ALTER TABLE `currencies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recurringpayments`
--

DROP TABLE IF EXISTS `recurringpayments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recurringpayments` (
  `payment_id` int NOT NULL AUTO_INCREMENT,
  `from_user_id` int DEFAULT NULL,
  `to_account_id` int DEFAULT NULL,
  `amount` decimal(20,2) DEFAULT NULL,
  `start_date` date DEFAULT NULL,
  `end_date` date DEFAULT NULL,
  `frequency` enum('DAILY','WEEKLY','MONTHLY','YEARLY') DEFAULT NULL,
  `last_executed` date DEFAULT NULL,
  `status` enum('ACTIVE','PAUSED','COMPLETED','FAILED') DEFAULT NULL,
  PRIMARY KEY (`payment_id`),
  KEY `from_user_id` (`from_user_id`),
  KEY `to_account_id` (`to_account_id`),
  CONSTRAINT `recurringpayments_ibfk_1` FOREIGN KEY (`from_user_id`) REFERENCES `user` (`user_id`),
  CONSTRAINT `recurringpayments_ibfk_2` FOREIGN KEY (`to_account_id`) REFERENCES `accounts` (`account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recurringpayments`
--

LOCK TABLES `recurringpayments` WRITE;
/*!40000 ALTER TABLE `recurringpayments` DISABLE KEYS */;
/*!40000 ALTER TABLE `recurringpayments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `signed_documents`
--

DROP TABLE IF EXISTS `signed_documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
  CONSTRAINT `signed_documents_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `signed_documents`
--

LOCK TABLES `signed_documents` WRITE;
/*!40000 ALTER TABLE `signed_documents` DISABLE KEYS */;
/*!40000 ALTER TABLE `signed_documents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transactions`
--

DROP TABLE IF EXISTS `transactions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transactions` (
  `transaction_id` int NOT NULL AUTO_INCREMENT,
  `from_account_id` int DEFAULT NULL,
  `to_account_id` int DEFAULT NULL,
  `amount` decimal(20,2) DEFAULT NULL,
  `transaction_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `transaction_type` varchar(255) DEFAULT NULL,
  `transaction_status` varchar(255) DEFAULT NULL,
  `description` text,
  PRIMARY KEY (`transaction_id`),
  KEY `from_account_id` (`from_account_id`),
  KEY `to_account_id` (`to_account_id`),
  CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`from_account_id`) REFERENCES `accounts` (`account_id`),
  CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`to_account_id`) REFERENCES `accounts` (`account_id`)
) ENGINE=InnoDB AUTO_INCREMENT=91 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transactions`
--

LOCK TABLES `transactions` WRITE;
/*!40000 ALTER TABLE `transactions` DISABLE KEYS */;
INSERT INTO `transactions` VALUES (4,NULL,NULL,123.00,'2023-11-15 00:26:12','deposit',NULL,'Deposit into account'),(5,NULL,NULL,233.00,'2023-11-15 00:26:18','deposit',NULL,'Deposit into account'),(6,NULL,NULL,213.00,'2023-11-15 00:26:27','deposit',NULL,'Deposit into account'),(7,NULL,NULL,233.00,'2023-11-15 00:27:25','deposit',NULL,'Deposit into account'),(8,NULL,NULL,1234.00,'2023-11-19 15:27:25','deposit',NULL,'Deposit into account'),(9,NULL,NULL,22.00,'2023-11-19 15:54:00','deposit',NULL,'Deposit into account'),(10,NULL,NULL,22.00,'2023-11-19 15:54:29','deposit',NULL,'Deposit into account'),(11,NULL,NULL,22.00,'2023-11-19 15:56:29','deposit',NULL,'Deposit into account'),(12,NULL,NULL,123.00,'2023-11-19 16:03:09','deposit',NULL,'Deposit into account'),(13,NULL,NULL,1234.00,'2023-11-19 16:10:14','deposit',NULL,'Deposit into account'),(14,NULL,NULL,123.00,'2023-11-19 16:15:22','deposit',NULL,'Deposit into account'),(15,NULL,NULL,3333.00,'2023-11-19 16:15:46','deposit',NULL,'Deposit into account'),(16,8,NULL,223.00,'2023-11-19 16:24:45','deposit',NULL,'Deposit into account'),(17,8,NULL,23.00,'2023-11-19 17:29:28','withdrawal',NULL,'Withdrawal from account'),(18,8,NULL,20.00,'2023-11-19 20:31:03','withdrawal',NULL,'Withdrawal from account'),(19,8,NULL,12.00,'2024-01-31 01:25:16','deposit',NULL,'Deposit into account'),(20,8,NULL,12.00,'2024-01-31 01:33:13','deposit',NULL,'Deposit into account'),(21,8,NULL,12.00,'2024-01-31 01:33:45','deposit',NULL,'Deposit into account'),(22,8,NULL,12.00,'2024-01-31 01:43:05','deposit',NULL,'Deposit into account'),(23,8,NULL,22.00,'2024-01-31 01:43:19','deposit',NULL,'Deposit into account'),(24,8,NULL,234.00,'2024-01-31 01:43:50','deposit',NULL,'Deposit into account'),(25,8,NULL,22.00,'2024-01-31 02:26:54','deposit',NULL,'Deposit into account'),(26,8,NULL,NULL,'2024-01-31 02:27:23','deposit',NULL,'Deposit into account'),(27,8,NULL,20.00,'2024-02-03 01:50:29','deposit',NULL,'Deposit into account'),(28,8,NULL,12.00,'2024-02-03 02:04:35','deposit',NULL,'Deposit into account'),(29,10,NULL,23.00,'2024-02-03 02:11:02','deposit',NULL,'Deposit into account'),(30,10,NULL,23.00,'2024-02-03 02:11:59','deposit',NULL,'Deposit into account'),(31,10,NULL,234.00,'2024-02-03 02:40:26','deposit',NULL,'Deposit into account'),(32,10,NULL,22.00,'2024-02-03 02:40:34','withdrawal',NULL,'Withdrawal from account'),(33,8,NULL,22.00,'2024-02-03 11:49:12','deposit',NULL,'Deposit into account'),(34,10,NULL,10.00,'2024-02-05 17:32:39','deposit',NULL,'Deposit into account'),(35,10,NULL,20.00,'2024-02-05 17:32:51','withdrawal',NULL,'Withdrawal from account'),(36,10,NULL,10.00,'2024-02-05 18:02:37','deposit',NULL,'Deposit into account'),(37,10,NULL,10.00,'2024-02-05 18:02:45','withdrawal',NULL,'Withdrawal from account'),(38,8,NULL,10.00,'2024-02-06 16:03:01','deposit',NULL,'Deposit into account'),(39,10,7,12.00,'2024-02-06 23:58:33','transfer',NULL,'Transfer to another account'),(40,10,7,12.00,'2024-02-06 23:58:33','transfer',NULL,'Transfer from another account'),(41,10,7,13.00,'2024-02-07 00:01:26','transfer',NULL,'Transfer to another account'),(42,10,7,13.00,'2024-02-07 00:01:26','transfer',NULL,'Transfer from another account'),(43,10,7,15.00,'2024-02-07 00:07:13','transfer',NULL,'Transfer from account 10 to account 7'),(44,10,7,15.00,'2024-02-07 00:07:13','transfer',NULL,'Transfer from account 10 to account 7'),(45,10,7,16.00,'2024-02-07 00:10:52','transfer',NULL,'Transfer from account 10 to account 7'),(46,7,10,16.00,'2024-02-07 00:10:52','transfer',NULL,'Transfer from account 7 to account 10'),(47,10,NULL,22.00,'2024-02-08 02:18:02','deposit',NULL,'Deposit into account'),(48,10,NULL,33.00,'2024-02-08 02:18:10','deposit',NULL,'Deposit into account'),(49,10,NULL,22.00,'2024-02-08 02:18:14','withdrawal',NULL,'Withdrawal from account'),(50,10,7,12.00,'2024-02-09 00:18:48','transfer',NULL,'Transfer from account 10 to account 7'),(51,7,10,12.00,'2024-02-09 00:18:48','transfer',NULL,'Transfer from account 7 to account 10'),(52,10,7,24.00,'2024-02-09 00:19:22','transfer',NULL,'Transfer from account 10 to account 7'),(53,7,10,24.00,'2024-02-09 00:19:22','transfer',NULL,'Transfer from account 7 to account 10'),(54,10,NULL,10.00,'2024-02-09 00:57:59','deposit',NULL,'Deposit into account'),(55,10,NULL,1.00,'2024-02-09 00:58:07','deposit',NULL,'Deposit into account'),(56,10,7,12.00,'2024-02-09 00:58:17','transfer',NULL,'Transfer from account 10 to account 7'),(57,7,10,12.00,'2024-02-09 00:58:17','transfer',NULL,'Transfer from account 7 to account 10'),(58,10,7,12.00,'2024-02-09 11:23:48','transfer',NULL,'Transfer from account 10 to account 7'),(59,7,10,12.00,'2024-02-09 11:23:48','transfer',NULL,'Transfer from account 7 to account 10'),(60,10,7,12.00,'2024-02-09 11:23:54','transfer',NULL,'Transfer from account 10 to account 7'),(61,7,10,12.00,'2024-02-09 11:23:54','transfer',NULL,'Transfer from account 7 to account 10'),(62,10,7,10.00,'2024-02-09 11:24:30','transfer',NULL,'Transfer from account 10 to account 7'),(63,7,10,10.00,'2024-02-09 11:24:30','transfer',NULL,'Transfer from account 7 to account 10'),(64,10,7,11.00,'2024-02-09 22:07:08','transfer',NULL,'Transfer from account 10 to account 7'),(65,7,10,11.00,'2024-02-09 22:07:08','transfer',NULL,'Transfer from account 7 to account 10'),(66,10,7,10.00,'2024-02-09 22:32:45','transfer',NULL,'Transfer from account 10 to account 7'),(67,7,10,10.00,'2024-02-09 22:32:45','transfer',NULL,'Transfer from account 7 to account 10'),(68,10,7,10.00,'2024-02-09 23:01:39','transfer',NULL,'Transfer from account 10 to account 7'),(69,7,10,10.00,'2024-02-09 23:01:39','transfer',NULL,'Transfer from account 7 to account 10'),(70,10,7,10.00,'2024-02-09 23:12:14','transfer',NULL,'Transfer from account 10 to account 7'),(71,7,10,10.00,'2024-02-09 23:12:14','transfer',NULL,'Transfer from account 7 to account 10'),(72,10,7,10.00,'2024-02-09 23:17:30','transfer',NULL,'Transfer from account 10 to account 7'),(73,7,10,10.00,'2024-02-09 23:17:30','transfer',NULL,'Transfer from account 7 to account 10'),(74,10,7,11.00,'2024-02-09 23:31:10','transfer',NULL,'Transfer from account 10 to account 7'),(75,7,10,11.00,'2024-02-09 23:31:10','transfer',NULL,'Transfer from account 7 to account 10'),(76,10,7,2.00,'2024-02-09 23:35:54','transfer',NULL,'Transfer from account 10 to account 7'),(77,7,10,2.00,'2024-02-09 23:35:54','transfer',NULL,'Transfer from account 7 to account 10'),(78,10,7,1.00,'2024-02-09 23:38:11','transfer',NULL,'Transfer from account 10 to account 7'),(79,7,10,1.00,'2024-02-09 23:38:11','transfer',NULL,'Transfer from account 7 to account 10'),(80,10,7,1.00,'2024-02-09 23:42:22','transfer',NULL,'Transfer from account 10 to account 7'),(81,7,10,1.00,'2024-02-09 23:42:22','transfer',NULL,'Transfer from account 7 to account 10'),(82,10,NULL,50.00,'2024-02-10 01:16:08','deposit',NULL,'Deposit into account'),(83,10,NULL,100.00,'2024-02-10 11:46:32','deposit',NULL,'Deposit into account'),(84,10,NULL,1.00,'2024-02-16 03:14:36','deposit',NULL,'Deposit into account'),(85,10,7,12.00,'2024-03-07 23:36:10','transfer',NULL,'Transfer from account 10 to account 7'),(86,7,10,12.00,'2024-03-07 23:36:10','transfer',NULL,'Transfer from account 7 to account 10'),(87,10,7,12.00,'2024-03-07 23:37:45','transfer',NULL,'Transfer from account 10 to account 7'),(88,7,10,12.00,'2024-03-07 23:37:45','transfer',NULL,'Transfer from account 7 to account 10'),(89,10,7,22.00,'2024-03-07 23:39:49','transfer',NULL,'Transfer from account 10 to account 7'),(90,7,10,22.00,'2024-03-07 23:39:49','transfer',NULL,'Transfer from account 7 to account 10');
/*!40000 ALTER TABLE `transactions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
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
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'kokelej','ivankokalovic@protonmail.ch','$2b$12$Z/v5BhdXwxHhZog1OJDrvewwUdckGWUvw.BakG9.eKxhW1UITQzKO',NULL,'2023-10-29 18:54:48',NULL),(3,'kokelej1','ivankokalovic1@protonmail.ch','$2b$12$IdrerZ9.1LwZydjuXIPY3u1tP8XZH1B1u27Ii0F7BOTQSnNiJUgz2',NULL,'2023-10-29 18:56:13',NULL),(4,'kokelej12','ivankokalovic@protonmail.ch12','$2b$12$FWyJaFzb0LWTpyoOCMNHrO9b7sypysDeeWI6wN5hEmjgnRDj8MEQe',NULL,'2023-10-29 22:00:36',NULL),(5,'kokelej123456','ivankokalovic123456@protonmail.ch1123','$2b$12$cFPrmiLuG361d5L934tt3.z0aTvWjjBREB9JlygE4Hw0eTtWquz2a',NULL,'2023-11-04 22:47:47',NULL),(6,'kokelej1224','ivankokalovic22222@protonmail.ch','$2b$12$nocwbdprGqPGCt7gSrPEYuAn3j1Y09zFMHWl6a8hpNQpTiVzTrQB6',NULL,'2023-11-19 17:38:57',NULL),(7,'kokelej1234567','ivankokalovic@prot2323232onmail.ch','$2b$12$FwZJfV5hdB2li26Z5bUzL.YeSLYsk5F8mRm6MrumWd2ZVRqXAPcJO',NULL,'2024-01-31 02:14:15',NULL),(8,'kokelej12345678910','ivankokal23214241ovic@protonmail.ch','$2b$12$4fBG2MYiuOVkMk84BFhJkeWAvjdcDiJFD/3ujzVoR8ycFvv3oDbk.',NULL,'2024-01-31 02:21:07',NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-07-30  1:58:52
