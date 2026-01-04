CREATE DATABASE  IF NOT EXISTS `eskala_production` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `eskala_production`;
-- MySQL dump 10.13  Distrib 8.0.43, for macos15 (arm64)
--
-- Host: localhost    Database: eskala_production
-- ------------------------------------------------------
-- Server version	9.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `app_settings`
--

DROP TABLE IF EXISTS `app_settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_settings` (
  `setting_key` varchar(64) NOT NULL,
  `value_num` decimal(18,6) DEFAULT NULL,
  `value_text` varchar(255) DEFAULT NULL,
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`setting_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_settings`
--

LOCK TABLES `app_settings` WRITE;
/*!40000 ALTER TABLE `app_settings` DISABLE KEYS */;
INSERT INTO `app_settings` VALUES ('PROFIT_VALUE_MULTIPLE',5.000000,NULL,'2025-10-17 15:49:14');
/*!40000 ALTER TABLE `app_settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_log`
--

DROP TABLE IF EXISTS `audit_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_log` (
  `audit_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `table_name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `row_pk` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `action` enum('INSERT','UPDATE','DELETE') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `diff_json` json DEFAULT NULL,
  `changed_by` bigint unsigned DEFAULT NULL,
  `changed_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`audit_id`),
  KEY `ix_audit_table_time` (`table_name`,`changed_at`),
  KEY `fk_audit_user` (`changed_by`),
  CONSTRAINT `fk_audit_user` FOREIGN KEY (`changed_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `audit_log`
--

LOCK TABLES `audit_log` WRITE;
/*!40000 ALTER TABLE `audit_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `audit_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `community_rep_profile`
--

DROP TABLE IF EXISTS `community_rep_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `community_rep_profile` (
  `user_id` bigint unsigned NOT NULL,
  `first_name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `title` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bank_name` varchar(160) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rtn_number` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `region_id` bigint unsigned DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  KEY `fk_cr_region` (`region_id`),
  CONSTRAINT `fk_cr_region` FOREIGN KEY (`region_id`) REFERENCES `regions` (`region_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_cr_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `community_rep_profile`
--

LOCK TABLES `community_rep_profile` WRITE;
/*!40000 ALTER TABLE `community_rep_profile` DISABLE KEYS */;
INSERT INTO `community_rep_profile` VALUES (72,'Noah','Dolnick','IT','Wells Fargo','123456789',NULL);
/*!40000 ALTER TABLE `community_rep_profile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `conversion_statuses`
--

DROP TABLE IF EXISTS `conversion_statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `conversion_statuses` (
  `status_id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `status_code` varchar(24) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`status_id`),
  UNIQUE KEY `status_code` (`status_code`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `conversion_statuses`
--

LOCK TABLES `conversion_statuses` WRITE;
/*!40000 ALTER TABLE `conversion_statuses` DISABLE KEYS */;
INSERT INTO `conversion_statuses` VALUES (2,'APPROVED'),(4,'PAID'),(3,'REJECTED'),(1,'SUBMITTED');
/*!40000 ALTER TABLE `conversion_statuses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `currencies`
--

DROP TABLE IF EXISTS `currencies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `currencies` (
  `currency_code` char(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`currency_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `currencies`
--

LOCK TABLES `currencies` WRITE;
/*!40000 ALTER TABLE `currencies` DISABLE KEYS */;
INSERT INTO `currencies` VALUES ('HNL','Honduran Lempira'),('USD','US Dollar');
/*!40000 ALTER TABLE `currencies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dividend_payout_form_submissions`
--

DROP TABLE IF EXISTS `dividend_payout_form_submissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dividend_payout_form_submissions` (
  `submission_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `bank_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT 'RTN Number',
  `partner_name` varchar(180) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `reported_shares` decimal(15,2) DEFAULT NULL,
  `investment_hnl` decimal(18,2) DEFAULT NULL,
  `investment_usd` decimal(18,2) DEFAULT NULL,
  `payout_date` date DEFAULT NULL,
  `amount_paid` decimal(18,2) DEFAULT NULL,
  `payment_method` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `payment_proof_path` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `comments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `confirmed` tinyint(1) DEFAULT '0',
  `edited_by` bigint unsigned DEFAULT NULL,
  `edited_at` datetime DEFAULT NULL,
  `status` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'SUBMITTED',
  `submitted_by` bigint unsigned DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`submission_id`),
  KEY `idx_dividend_partner` (`partner_name`),
  KEY `idx_dividend_bank` (`bank_id`),
  KEY `idx_dividend_date` (`payout_date`),
  KEY `idx_dividend_status` (`status`),
  KEY `fk_dividend_editor` (`edited_by`),
  KEY `idx_dividend_submitted_by` (`submitted_by`),
  CONSTRAINT `fk_dividend_editor` FOREIGN KEY (`edited_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_dividend_submitted_by` FOREIGN KEY (`submitted_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dividend_payout_form_submissions`
--

LOCK TABLES `dividend_payout_form_submissions` WRITE;
/*!40000 ALTER TABLE `dividend_payout_form_submissions` DISABLE KEYS */;
INSERT INTO `dividend_payout_form_submissions` VALUES (12,'123456789','Wells Fargo',125.00,46000.00,1821.78,'2025-11-28',10500.00,'bank','/uploads/proof-1764451557-1764451557765.pdf','Test',1,NULL,NULL,'SUBMITTED',48,'2025-11-29 16:25:57',NULL);
/*!40000 ALTER TABLE `dividend_payout_form_submissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `dividend_payouts`
--

DROP TABLE IF EXISTS `dividend_payouts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `dividend_payouts` (
  `payout_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `investment_id` bigint unsigned NOT NULL,
  `period_month` date NOT NULL,
  `profit_local` decimal(18,2) DEFAULT NULL,
  `profit_usd` decimal(18,2) DEFAULT NULL,
  `dividend_local` decimal(18,2) DEFAULT NULL,
  `dividend_usd` decimal(18,2) DEFAULT NULL,
  `fx_rate_id` bigint unsigned DEFAULT NULL,
  `calc_formula_id` bigint unsigned DEFAULT NULL,
  `created_by` bigint unsigned DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`payout_id`),
  UNIQUE KEY `uk_payout_month` (`investment_id`,`period_month`),
  KEY `fk_dp_fx` (`fx_rate_id`),
  KEY `fk_dp_formula` (`calc_formula_id`),
  KEY `fk_dp_created_by` (`created_by`),
  CONSTRAINT `fk_dp_created_by` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_dp_formula` FOREIGN KEY (`calc_formula_id`) REFERENCES `formulas` (`formula_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_dp_fx` FOREIGN KEY (`fx_rate_id`) REFERENCES `fx_rates` (`fx_rate_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_dp_investment` FOREIGN KEY (`investment_id`) REFERENCES `investments` (`investment_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `dividend_payouts`
--

LOCK TABLES `dividend_payouts` WRITE;
/*!40000 ALTER TABLE `dividend_payouts` DISABLE KEYS */;
/*!40000 ALTER TABLE `dividend_payouts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equity_conversion_form_submissions`
--

DROP TABLE IF EXISTS `equity_conversion_form_submissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equity_conversion_form_submissions` (
  `submission_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `bank_name` varchar(180) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rtn_number` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `representative_name` varchar(180) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone_number` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `loan_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `original_loan_amount` decimal(18,2) DEFAULT NULL,
  `loan_approval_date` date DEFAULT NULL,
  `interest_paid` decimal(18,2) DEFAULT NULL,
  `loan_amount_remaining` decimal(18,2) DEFAULT NULL,
  `repayment_frequency` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `proposed_conversion_amount` decimal(18,2) DEFAULT NULL,
  `proposed_conversion_ratio` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `proposed_equity_percentage` decimal(5,2) DEFAULT NULL,
  `desired_conversion_date` date DEFAULT NULL,
  `comments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `attachment_path` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `confirmed` tinyint(1) DEFAULT '0',
  `edited_by` bigint unsigned DEFAULT NULL,
  `edited_at` datetime DEFAULT NULL,
  `status` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'SUBMITTED',
  `submitted_by` bigint unsigned DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`submission_id`),
  KEY `idx_conversion_bank` (`bank_name`),
  KEY `idx_conversion_rtn` (`rtn_number`),
  KEY `idx_conversion_status` (`status`),
  KEY `idx_conversion_date` (`created_at`),
  KEY `fk_conversion_editor` (`edited_by`),
  KEY `idx_conversion_submitted_by` (`submitted_by`),
  CONSTRAINT `fk_conversion_editor` FOREIGN KEY (`edited_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_conversion_submitted_by` FOREIGN KEY (`submitted_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equity_conversion_form_submissions`
--

LOCK TABLES `equity_conversion_form_submissions` WRITE;
/*!40000 ALTER TABLE `equity_conversion_form_submissions` DISABLE KEYS */;
INSERT INTO `equity_conversion_form_submissions` VALUES (14,'Wells Fargo','123456789','Noah Dolnick','941-373-5682','LN-100-4672',250000.00,'2025-11-29',12500.00,137000.00,'monthly',75000.00,'1',25.00,'2025-12-31','Test',NULL,1,NULL,NULL,'SUBMITTED',48,'2025-11-29 18:38:25',NULL);
/*!40000 ALTER TABLE `equity_conversion_form_submissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equity_conversion_requests`
--

DROP TABLE IF EXISTS `equity_conversion_requests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equity_conversion_requests` (
  `request_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `investment_id` bigint unsigned NOT NULL,
  `request_date` date NOT NULL,
  `requested_local` decimal(18,2) DEFAULT NULL,
  `requested_usd` decimal(18,2) DEFAULT NULL,
  `fx_rate_id` bigint unsigned DEFAULT NULL,
  `status_id` tinyint unsigned NOT NULL,
  `approved_by` bigint unsigned DEFAULT NULL,
  `approved_at` datetime DEFAULT NULL,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`request_id`),
  KEY `fk_ecr_investment` (`investment_id`),
  KEY `fk_ecr_fx` (`fx_rate_id`),
  KEY `fk_ecr_approver` (`approved_by`),
  KEY `ix_ecr_status` (`status_id`),
  KEY `ix_ecr_date` (`request_date`),
  CONSTRAINT `fk_ecr_approver` FOREIGN KEY (`approved_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_ecr_fx` FOREIGN KEY (`fx_rate_id`) REFERENCES `fx_rates` (`fx_rate_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_ecr_investment` FOREIGN KEY (`investment_id`) REFERENCES `investments` (`investment_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ecr_status` FOREIGN KEY (`status_id`) REFERENCES `conversion_statuses` (`status_id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equity_conversion_requests`
--

LOCK TABLES `equity_conversion_requests` WRITE;
/*!40000 ALTER TABLE `equity_conversion_requests` DISABLE KEYS */;
/*!40000 ALTER TABLE `equity_conversion_requests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equity_programs`
--

DROP TABLE IF EXISTS `equity_programs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equity_programs` (
  `program_id` smallint unsigned NOT NULL AUTO_INCREMENT,
  `program_code` varchar(24) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`program_id`),
  UNIQUE KEY `program_code` (`program_code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equity_programs`
--

LOCK TABLES `equity_programs` WRITE;
/*!40000 ALTER TABLE `equity_programs` DISABLE KEYS */;
INSERT INTO `equity_programs` VALUES (1,'MATCHING','Matching Equity Program'),(2,'PROFIT','Profit-Sharing Program');
/*!40000 ALTER TABLE `equity_programs` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formulas`
--

DROP TABLE IF EXISTS `formulas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formulas` (
  `formula_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `formula_key` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `expression` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `version` int NOT NULL DEFAULT '1',
  `effective_from` datetime NOT NULL,
  `effective_to` datetime DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `changed_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `change_reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`formula_id`),
  UNIQUE KEY `uk_formula` (`formula_key`,`version`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formulas`
--

LOCK TABLES `formulas` WRITE;
/*!40000 ALTER TABLE `formulas` DISABLE KEYS */;
INSERT INTO `formulas` VALUES (2,'profit_investment_l','company_value_l * (expected_profit_pct / 100)',1,'2025-12-05 19:34:37',NULL,'Investment Amount (L) - Auto-Calculated|Profit Form|Investment Amount (L) = Company Value * (Expected Profit % / 100)',NULL,NULL),(3,'profit_investment_usd','investment_l / exchange_rate',1,'2025-12-05 19:34:37',NULL,'Investment Amount ($) - Auto-Calculated|Profit Form|Investment Amount ($) = Investment Amount (L) / Exchange Rate',NULL,NULL),(5,'matching_investment_usd','investment_l / exchange_rate',1,'2025-12-05 19:34:37',NULL,'Investment Amount ($) - Auto-Calculated|Matching Form|Investment Amount ($) = Investment Amount (L) / Exchange Rate',NULL,NULL),(22,'profit_company_value_l','profit_l * 5',1,'2025-12-05 19:34:37',NULL,'Company Value (L) - Auto-Calculated|Profit Form|Wrong formula',NULL,NULL);
/*!40000 ALTER TABLE `formulas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fx_rates`
--

DROP TABLE IF EXISTS `fx_rates`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fx_rates` (
  `fx_rate_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `from_currency` char(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `to_currency` char(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `rate` decimal(18,6) NOT NULL,
  `valid_from` datetime NOT NULL,
  `valid_to` datetime DEFAULT NULL,
  PRIMARY KEY (`fx_rate_id`),
  KEY `fk_fx_to` (`to_currency`),
  KEY `ix_fx_pair_from` (`from_currency`,`to_currency`,`valid_from`),
  KEY `ix_fx_current` (`from_currency`,`to_currency`,`valid_to`),
  CONSTRAINT `fk_fx_from` FOREIGN KEY (`from_currency`) REFERENCES `currencies` (`currency_code`) ON DELETE RESTRICT,
  CONSTRAINT `fk_fx_to` FOREIGN KEY (`to_currency`) REFERENCES `currencies` (`currency_code`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fx_rates`
--

LOCK TABLES `fx_rates` WRITE;
/*!40000 ALTER TABLE `fx_rates` DISABLE KEYS */;
INSERT INTO `fx_rates` VALUES (2,'USD','HNL',25.250000,'2025-12-05 19:34:37',NULL),(14,'HNL','USD',25.250000,'2025-12-05 19:34:37',NULL);
/*!40000 ALTER TABLE `fx_rates` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `investment_statuses`
--

DROP TABLE IF EXISTS `investment_statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `investment_statuses` (
  `status_id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `status_code` varchar(24) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`status_id`),
  UNIQUE KEY `status_code` (`status_code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `investment_statuses`
--

LOCK TABLES `investment_statuses` WRITE;
/*!40000 ALTER TABLE `investment_statuses` DISABLE KEYS */;
INSERT INTO `investment_statuses` VALUES (2,'ACTIVE'),(3,'CLOSED'),(1,'PLANNED');
/*!40000 ALTER TABLE `investment_statuses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `investments`
--

DROP TABLE IF EXISTS `investments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `investments` (
  `investment_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `partner_id` bigint unsigned NOT NULL,
  `program_id` smallint unsigned NOT NULL,
  `start_date` date NOT NULL,
  `principal_local` decimal(18,2) DEFAULT NULL,
  `last_loan_l` decimal(18,2) DEFAULT NULL,
  `principal_usd` decimal(18,2) DEFAULT NULL,
  `difference_l` decimal(18,2) DEFAULT NULL,
  `init_fx_rate_id` bigint unsigned DEFAULT NULL,
  `status_id` tinyint unsigned NOT NULL,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_by` bigint unsigned DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`investment_id`),
  KEY `fk_inv_partner` (`partner_id`),
  KEY `fk_inv_program` (`program_id`),
  KEY `fk_inv_status` (`status_id`),
  KEY `fk_inv_fx_init` (`init_fx_rate_id`),
  CONSTRAINT `fk_inv_fx_init` FOREIGN KEY (`init_fx_rate_id`) REFERENCES `fx_rates` (`fx_rate_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_inv_partner` FOREIGN KEY (`partner_id`) REFERENCES `partners` (`partner_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_inv_program` FOREIGN KEY (`program_id`) REFERENCES `equity_programs` (`program_id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_inv_status` FOREIGN KEY (`status_id`) REFERENCES `investment_statuses` (`status_id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `investments`
--

LOCK TABLES `investments` WRITE;
/*!40000 ALTER TABLE `investments` DISABLE KEYS */;
INSERT INTO `investments` VALUES (53,2,1,'2024-01-01',46320.00,25000.00,NULL,21320.00,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(54,3,1,'2024-01-01',46320.00,25000.00,NULL,21320.00,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(55,4,1,'2024-01-01',46320.00,25000.00,NULL,21320.00,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(56,5,1,'2024-01-01',46320.00,200000.00,NULL,-153680.00,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(57,6,1,'2024-01-01',39705.02,100000.00,NULL,-60294.98,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(58,7,1,'2024-01-01',132645.93,500000.00,NULL,-367354.07,NULL,1,'Expected Profit: 2.38%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(59,8,1,'2024-01-01',117495.00,300000.00,NULL,-182505.00,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(60,9,1,'2024-01-01',NULL,400000.00,NULL,-400000.00,NULL,1,NULL,1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(61,10,1,'2024-01-01',80141.00,200000.00,NULL,-119859.00,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(62,11,1,'2024-01-01',105269.00,400000.00,NULL,-294731.00,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(63,12,1,'2024-01-01',62300.00,300000.00,NULL,-237700.00,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(64,13,1,'2024-01-01',76979.55,NULL,NULL,NULL,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(65,14,1,'2024-01-01',NULL,200000.00,NULL,-200000.00,NULL,1,NULL,1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(66,15,1,'2024-01-01',60208.00,250000.00,NULL,-189792.00,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(67,16,1,'2024-01-01',212798.59,523000.00,NULL,-310201.41,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(68,17,1,'2024-01-01',112870.00,500000.00,NULL,-387130.00,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(69,18,1,'2024-01-01',NULL,300000.00,NULL,-300000.00,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(70,19,1,'2024-01-01',165000.00,200000.00,NULL,-35000.00,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21'),(71,20,1,'2024-01-01',71665.00,525000.00,NULL,-453335.00,NULL,1,'Expected Profit: 20%',1,'2025-11-07 20:01:21','2025-11-07 20:01:21');
/*!40000 ALTER TABLE `investments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ivl_form_entries`
--

DROP TABLE IF EXISTS `ivl_form_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ivl_form_entries` (
  `investment_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `partner_name` varchar(180) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `expected_profit_pct` decimal(5,2) DEFAULT NULL,
  `investment_amount` decimal(18,2) DEFAULT NULL,
  `last_loan` decimal(18,2) DEFAULT NULL,
  `difference` decimal(18,2) DEFAULT NULL,
  `comments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `start_date` date DEFAULT NULL,
  `created_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'System',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'System',
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`investment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=79 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ivl_form_entries`
--

LOCK TABLES `ivl_form_entries` WRITE;
/*!40000 ALTER TABLE `ivl_form_entries` DISABLE KEYS */;
INSERT INTO `ivl_form_entries` VALUES (48,'CARUPPAHG',20.00,46320.00,NULL,25000.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:10:48'),(49,'Crac Bendicion de Nahuaterique',20.00,46320.00,25000.00,25000.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:11:46'),(50,'Crac Lenca Nuevo Amanecer',20.00,46320.00,25000.00,25000.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:11:57'),(51,'Crac Maria Auxiliadora',20.00,46320.00,200000.00,153680.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:13:57'),(52,'CRAC LA ESPERANZA DE TEUPASENTI',20.00,39705.02,100000.00,60294.98,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:13:47'),(53,'Crac Fe y Esperanza del Espinito',2.38,132645.93,500000.00,367354.07,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:14:41'),(54,'Crac MANANTIALES DE VIDA',20.00,117495.00,300000.00,182505.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:14:34'),(55,'CRAC NUEVO PARAISO - EL JUNQUILLO',0.00,NULL,400000.00,400000.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:15:27'),(56,'Crac Agua Escondida',20.00,80141.00,200000.00,119859.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:16:40'),(57,'Crac Barrera Viva',20.00,105269.00,400000.00,294731.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:16:33'),(58,'Crac Cilca #2',20.00,62300.00,300000.00,237700.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:16:26'),(59,'Crac Cuscateca',20.00,76979.55,NULL,NULL,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:17:20'),(60,'Crac Cerro Bonito',0.00,NULL,200000.00,NULL,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:17:49'),(61,'Crac UNION SOCIEDAD - LAS FLORES',20.00,60208.00,250000.00,189792.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:20:23'),(62,'ESM PUEBLO ORGANIZADO DEL PEDERNAL',20.00,212798.59,523000.00,310201.41,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:20:31'),(63,'Crac LOS COPETES UNIDOS POR MAS',20.00,112870.00,500000.00,387130.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:20:37'),(64,'Crac El Guayabal',20.00,NULL,300000.00,300000.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:20:43'),(65,'Crac Union de Sisiguara',20.00,165000.00,200000.00,35000.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:20:49'),(66,'Crac VISION AL DESARROLLO DE ZACATE BLANCO',20.00,71665.00,525000.00,453335.00,'Historical data import',NULL,'2025-11-07','ndolnick','2025-11-07 20:04:32','ndolnick','2025-11-07 20:20:56'),(77,'Wells Fargo',20.00,46000.00,25000.00,21000.00,'Test','File: /uploads/ivl-1764613680-1764613680485.pdf','2025-12-01','ndolnick','2025-12-01 13:28:00','ndolnick',NULL);
/*!40000 ALTER TABLE `ivl_form_entries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `matching_equity_entries`
--

DROP TABLE IF EXISTS `matching_equity_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matching_equity_entries` (
  `investment_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `bank_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `partner_name` varchar(180) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `year` smallint unsigned DEFAULT NULL,
  `reported_shares` decimal(15,2) DEFAULT NULL,
  `share_capital_multiplied` decimal(15,2) DEFAULT NULL,
  `technician` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `comments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `notes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `profit_l` decimal(18,2) DEFAULT NULL,
  `expected_profit_pct` decimal(5,2) DEFAULT NULL,
  `company_value_l` decimal(18,2) DEFAULT NULL,
  `investment_l` decimal(18,2) DEFAULT NULL,
  `investment_usd` decimal(18,2) DEFAULT NULL,
  `exchange_rate` decimal(18,6) DEFAULT NULL,
  `proposal_state` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `transaction_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `business_category` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `company_type` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `community` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `municipality` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `january_l` decimal(15,2) DEFAULT '0.00',
  `february_l` decimal(15,2) DEFAULT '0.00',
  `march_l` decimal(15,2) DEFAULT '0.00',
  `april_l` decimal(15,2) DEFAULT '0.00',
  `may_l` decimal(15,2) DEFAULT '0.00',
  `june_l` decimal(15,2) DEFAULT '0.00',
  `july_l` decimal(15,2) DEFAULT '0.00',
  `august_l` decimal(15,2) DEFAULT '0.00',
  `september_l` decimal(15,2) DEFAULT '0.00',
  `october_l` decimal(15,2) DEFAULT '0.00',
  `november_l` decimal(15,2) DEFAULT '0.00',
  `december_l` decimal(15,2) DEFAULT '0.00',
  `start_date` date DEFAULT NULL,
  `created_by` bigint unsigned DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'System',
  PRIMARY KEY (`investment_id`),
  KEY `fk_matching_creator` (`created_by`),
  KEY `idx_matching_partner` (`partner_name`),
  KEY `idx_matching_year` (`year`),
  KEY `idx_matching_state` (`proposal_state`),
  KEY `idx_matching_bank` (`bank_id`),
  KEY `idx_matching_updated_by` (`updated_by`),
  CONSTRAINT `fk_matching_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `matching_equity_entries`
--

LOCK TABLES `matching_equity_entries` WRITE;
/*!40000 ALTER TABLE `matching_equity_entries` DISABLE KEYS */;
INSERT INTO `matching_equity_entries` VALUES (1,'RTN-GRANADILLOS','Crac Renacer de Granadillos',2024,141457.00,424371.00,'MIGUEL RODRIGUEZ','No cumplieron con el Pago de Intereses. Queda sin efecto cualquier negociacion previa.',NULL,NULL,30.00,NULL,NULL,5602.26,NULL,'Rejected','Conversion','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','GRANADILLOS','EL PARAISO','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:26:28',NULL,'System'),(2,'RTN-CARUPPAHG','CARUPPAHG',2024,29390.00,88170.00,'MIGUEL RODRIGUEZ','Eskala Pilot | Cash + Starlink',NULL,NULL,20.00,NULL,46320.00,1163.96,NULL,'Executed','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','HOYA GRANDE MOROCELI','EL PARAISO','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:26:28',NULL,'System'),(3,'RTN-FEDEC','FEDEC',2024,792507.30,1981268.25,'MIGUEL RODRIGUEZ','Big Partner Proposal',NULL,NULL,15.00,NULL,NULL,31386.43,NULL,'To Pitch','Conversion','COMMERCE','CAJA RURAL DE AHORRO Y CREDITO','CATACAMAS','CATACAMAS','OLANCHO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:26:28',NULL,'System'),(4,'RTN-NAHUATERIQUE','Crac Bendicion de Nahuaterique',2024,12707.00,31767.50,'CARLOS CONTRERAS','SENPRENDE | Cash + Starlink',NULL,NULL,20.00,NULL,46320.00,503.25,NULL,'Executed','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','SANTA ELENA','LA PAZ','LA PAZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:26:28',NULL,'System'),(5,'RTN-LENCA','Crac Lenca Nuevo Amanecer',2024,11000.00,27500.00,'CARLOS CONTRERAS','SENPRENDE | Cash + Starlink',NULL,NULL,20.00,NULL,46320.00,435.64,NULL,'Executed','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','SANTA ELENA','LA PAZ','LA PAZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:26:28',NULL,'System'),(6,'RTN-AUXILIADORA','Crac Maria Auxiliadora',2024,33148.00,NULL,'CARLOS CONTRERAS','SENPRENDE | Cash + Starlink',NULL,NULL,20.00,NULL,46320.00,1312.79,NULL,'Executed','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','SANTA ELENA','LA PAZ','LA PAZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:26:28',NULL,'System'),(7,'RTN-TERRONES','CRAC LOS TERRONES',NULL,NULL,NULL,'MIGUEL RODRIGUEZ','GB',NULL,NULL,20.00,NULL,25000.00,NULL,NULL,'Rejected','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','LOS TERRONES','EL PARAISO','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:26:28',NULL,'System'),(8,'RTN-TEUPASENTI','CRAC LA ESPERANZA DE TEUPASENTI',2024,28982.00,NULL,'MIGUEL RODRIGUEZ','Cash + (Laptop & Printer)',NULL,NULL,20.00,NULL,39810.01,1147.80,NULL,'Executed','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','SANTA ROSA #1','TEUPASENTI','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:26:28',NULL,'System'),(9,'RTN-SANJOSE','CRAC Amor y Fe San Jose',2024,NULL,NULL,'CARLOS CONTRERAS','Cash',NULL,NULL,20.00,NULL,25000.00,NULL,NULL,'Accepted','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','EL GUAYABAL','SAN JOSE','LA PAZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:26:28',NULL,'System'),(10,'RTN-CAMPO7','Crac Campo 7',NULL,NULL,NULL,'MIGUEL RODRIGUEZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','CAMPO 7','YORITO','YORO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:26:28',NULL,'System'),(11,'RTN-LUZYESFUERZO','Crac Luz y Esfuerzo',NULL,NULL,NULL,'MIGUEL RODRIGUEZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Rejected','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','LAS LOMAS','YORO','YORO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:26:28',NULL,'System'),(12,'RTN-14SEPT','Crac Nuevo Amanecer Colonia 14 de Septiembre',NULL,NULL,NULL,'MIGUEL RODRIGUEZ','SENPRENDE',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','14 DE SEPTIEMBRE','VICTORIA','YORO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:26:28',NULL,'System'),(27,NULL,'Wells Fargo',2025,1000.00,25000.00,'Noah Dolnick','Test','File: matching-1764541427-1764541427158.pdf',NULL,10.00,NULL,110000.00,4230.77,26.000000,'To Pitch','Conversion','Coffee','Coopertive','SANTA ROSA #1','TEUPASENTI','EL PARAISO',100.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,'2025-11-30',48,'2025-11-30 17:23:47',NULL,'48');
/*!40000 ALTER TABLE `matching_equity_entries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `partner_representatives`
--

DROP TABLE IF EXISTS `partner_representatives`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `partner_representatives` (
  `partner_id` bigint unsigned NOT NULL,
  `rep_user_id` bigint unsigned NOT NULL,
  `since_date` date DEFAULT NULL,
  PRIMARY KEY (`partner_id`,`rep_user_id`),
  KEY `fk_pr_rep` (`rep_user_id`),
  CONSTRAINT `fk_pr_partner` FOREIGN KEY (`partner_id`) REFERENCES `partners` (`partner_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pr_rep` FOREIGN KEY (`rep_user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `partner_representatives`
--

LOCK TABLES `partner_representatives` WRITE;
/*!40000 ALTER TABLE `partner_representatives` DISABLE KEYS */;
/*!40000 ALTER TABLE `partner_representatives` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `partners`
--

DROP TABLE IF EXISTS `partners`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `partners` (
  `partner_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `partner_name` varchar(180) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `details` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `region_id` bigint unsigned DEFAULT NULL,
  `created_by` bigint unsigned DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`partner_id`),
  UNIQUE KEY `uk_partner_name_region` (`partner_name`,`region_id`),
  KEY `fk_partner_region` (`region_id`),
  KEY `fk_partner_creator` (`created_by`),
  CONSTRAINT `fk_partner_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_partner_region` FOREIGN KEY (`region_id`) REFERENCES `regions` (`region_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=123 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `partners`
--

LOCK TABLES `partners` WRITE;
/*!40000 ALTER TABLE `partners` DISABLE KEYS */;
INSERT INTO `partners` VALUES (1,'Wells Fargo',NULL,NULL,NULL,'2025-10-18 00:07:01',NULL),(2,'CARUPPAHG',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(3,'Crac Bendicion de Nahuaterique',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(4,'Crac Lenca Nuevo Amanecer',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(5,'Crac Maria Auxiliadora',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(6,'CRAC LA ESPERANZA DE TEUPASENTI',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(7,'Crac Fe y Esperanza del Espinito',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(8,'Crac MANANTIALES DE VIDA',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(9,'CRAC NUEVO PARAISO - EL JUNQUILLO',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(10,'Crac Agua Escondida',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(11,'Crac Barrera Viva',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(12,'Crac Cilca #2',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(13,'Crac Cuscateca',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(14,'Crac Cerro Bonito',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(15,'Crac UNION SOCIEDAD - LAS FLORES',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(16,'ESM PUEBLO ORGANIZADO DEL PEDERNAL',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(17,'Crac LOS COPETES UNIDOS POR MAS',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(18,'Crac El Guayabal',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(19,'Crac Union de Sisiguara',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(20,'Crac VISION AL DESARROLLO DE ZACATE BLANCO',NULL,NULL,NULL,'2025-10-18 00:11:17',NULL),(21,'CARUPPAHG',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(22,'Crac Bendicion de Nahuaterique',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(23,'Crac Lenca Nuevo Amanecer',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(24,'Crac Maria Auxiliadora',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(25,'CRAC LA ESPERANZA DE TEUPASENTI',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(26,'Crac Fe y Esperanza del Espinito',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(27,'Crac MANANTIALES DE VIDA',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(28,'CRAC NUEVO PARAISO - EL JUNQUILLO',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(29,'Crac Agua Escondida',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(30,'Crac Barrera Viva',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(31,'Crac Cilca #2',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(32,'Crac Cuscateca',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(33,'Crac Cerro Bonito',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(34,'Crac UNION SOCIEDAD - LAS FLORES',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(35,'ESM PUEBLO ORGANIZADO DEL PEDERNAL',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(36,'Crac LOS COPETES UNIDOS POR MAS',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(37,'Crac El Guayabal',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(38,'Crac Union de Sisiguara',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(39,'Crac VISION AL DESARROLLO DE ZACATE BLANCO',NULL,NULL,NULL,'2025-10-18 18:20:47',NULL),(40,'CARUPPAHG',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(41,'Crac Bendicion de Nahuaterique',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(42,'Crac Lenca Nuevo Amanecer',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(43,'Crac Maria Auxiliadora',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(44,'CRAC LA ESPERANZA DE TEUPASENTI',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(45,'Crac Fe y Esperanza del Espinito',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(46,'Crac MANANTIALES DE VIDA',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(47,'CRAC NUEVO PARAISO - EL JUNQUILLO',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(48,'Crac Agua Escondida',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(49,'Crac Barrera Viva',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(50,'Crac Cilca #2',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(51,'Crac Cuscateca',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(52,'Crac Cerro Bonito',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(53,'Crac UNION SOCIEDAD - LAS FLORES',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(54,'ESM PUEBLO ORGANIZADO DEL PEDERNAL',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(55,'Crac LOS COPETES UNIDOS POR MAS',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(56,'Crac El Guayabal',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(57,'Crac Union de Sisiguara',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(58,'Crac VISION AL DESARROLLO DE ZACATE BLANCO',NULL,NULL,NULL,'2025-10-18 18:28:48',NULL),(59,'CARUPPAHG',NULL,NULL,NULL,'2025-10-18 18:59:41',NULL),(60,'Crac Bendicion de Nahuaterique',NULL,NULL,NULL,'2025-10-18 19:00:30',NULL),(61,'Crac Lenca Nuevo Amanecer',NULL,NULL,NULL,'2025-10-18 19:00:42',NULL),(62,'ESM PUEBLO ORGANIZADO DEL PEDERNAL',NULL,NULL,NULL,'2025-10-19 09:42:44',NULL),(63,'Wells Fargo',NULL,NULL,NULL,'2025-10-19 09:45:27',NULL),(64,'Wells Fargo',NULL,NULL,NULL,'2025-10-22 14:33:10',NULL),(65,'Wells Fargo',NULL,NULL,NULL,'2025-10-22 14:53:53',NULL),(66,'ESM PUEBLO ORGANIZADO DEL PEDERNAL',NULL,NULL,NULL,'2025-10-22 14:54:21',NULL),(67,'Wells Fargo',NULL,NULL,NULL,'2025-10-22 14:55:10',NULL),(68,'Wells Fargo',NULL,NULL,NULL,'2025-10-22 14:55:39',NULL),(69,'Wells Fargo',NULL,NULL,NULL,'2025-10-22 15:13:33',NULL),(70,'Wells Fargo',NULL,NULL,NULL,'2025-10-22 15:14:38',NULL),(71,'Wells Fargo',NULL,NULL,NULL,'2025-10-22 15:14:51',NULL),(72,'Wells Fargo',NULL,NULL,NULL,'2025-10-22 15:26:02',NULL),(73,'Wells Fargo',NULL,NULL,NULL,'2025-10-22 15:26:36',NULL),(74,'Wells Fargo',NULL,NULL,NULL,'2025-10-22 17:11:12',NULL),(75,'Wells Fargo',NULL,NULL,NULL,'2025-10-22 17:11:32',NULL),(76,'Wells Fargo',NULL,NULL,NULL,'2025-10-24 13:04:48',NULL),(77,'Wells Fargo',NULL,NULL,NULL,'2025-10-24 13:05:37',NULL),(78,'Comercial El Progreso',NULL,NULL,NULL,'2025-11-07 19:06:59',NULL),(79,'Agroindustrias del Sur',NULL,NULL,NULL,'2025-11-07 19:06:59',NULL),(80,'Distribuidora La Paz',NULL,NULL,NULL,'2025-11-07 19:06:59',NULL),(81,'Servicios Empresariales del Norte',NULL,NULL,NULL,'2025-11-07 19:06:59',NULL),(82,'Exportadora de Productos Agrícolas',NULL,NULL,NULL,'2025-11-07 19:06:59',NULL),(83,'Industrias Manufactureras Unidos',NULL,NULL,NULL,'2025-11-07 19:06:59',NULL),(84,'Tecnología y Logística SA',NULL,NULL,NULL,'2025-11-07 19:06:59',NULL),(85,'CARUPPAHG',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(86,'Crac Bendicion de Nahuaterique',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(87,'Crac Lenca Nuevo Amanecer',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(88,'Crac Maria Auxiliadora',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(89,'CRAC LA ESPERANZA DE TEUPASENTI',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(90,'Crac Fe y Esperanza del Espinito',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(91,'Crac MANANTIALES DE VIDA',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(92,'CRAC NUEVO PARAISO - EL JUNQUILLO',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(93,'Crac Agua Escondida',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(94,'Crac Barrera Viva',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(95,'Crac Cilca #2',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(96,'Crac Cuscateca',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(97,'Crac Cerro Bonito',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(98,'Crac UNION SOCIEDAD - LAS FLORES',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(99,'ESM PUEBLO ORGANIZADO DEL PEDERNAL',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(100,'Crac LOS COPETES UNIDOS POR MAS',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(101,'Crac El Guayabal',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(102,'Crac Union de Sisiguara',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(103,'Crac VISION AL DESARROLLO DE ZACATE BLANCO',NULL,NULL,NULL,'2025-11-07 19:56:47',NULL),(104,'CARUPPAHG',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(105,'Crac Bendicion de Nahuaterique',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(106,'Crac Lenca Nuevo Amanecer',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(107,'Crac Maria Auxiliadora',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(108,'CRAC LA ESPERANZA DE TEUPASENTI',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(109,'Crac Fe y Esperanza del Espinito',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(110,'Crac MANANTIALES DE VIDA',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(111,'CRAC NUEVO PARAISO - EL JUNQUILLO',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(112,'Crac Agua Escondida',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(113,'Crac Barrera Viva',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(114,'Crac Cilca #2',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(115,'Crac Cuscateca',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(116,'Crac Cerro Bonito',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(117,'Crac UNION SOCIEDAD - LAS FLORES',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(118,'ESM PUEBLO ORGANIZADO DEL PEDERNAL',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(119,'Crac LOS COPETES UNIDOS POR MAS',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(120,'Crac El Guayabal',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(121,'Crac Union de Sisiguara',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL),(122,'Crac VISION AL DESARROLLO DE ZACATE BLANCO',NULL,NULL,NULL,'2025-11-07 20:01:21',NULL);
/*!40000 ALTER TABLE `partners` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pipeline_stages`
--

DROP TABLE IF EXISTS `pipeline_stages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pipeline_stages` (
  `stage_id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `stage_code` varchar(32) NOT NULL,
  `stage_label` varchar(64) NOT NULL,
  `sort_order` smallint unsigned NOT NULL,
  PRIMARY KEY (`stage_id`),
  UNIQUE KEY `stage_code` (`stage_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pipeline_stages`
--

LOCK TABLES `pipeline_stages` WRITE;
/*!40000 ALTER TABLE `pipeline_stages` DISABLE KEYS */;
/*!40000 ALTER TABLE `pipeline_stages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `profit_form_entries`
--

DROP TABLE IF EXISTS `profit_form_entries`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `profit_form_entries` (
  `investment_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `bank_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `partner_name` varchar(180) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `year` smallint unsigned DEFAULT NULL,
  `technician` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `comments` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `profit_l` decimal(18,2) DEFAULT NULL,
  `expected_profit_pct` decimal(5,2) DEFAULT NULL,
  `company_value_l` decimal(18,2) DEFAULT NULL,
  `investment_l` decimal(18,2) DEFAULT NULL,
  `investment_usd` decimal(18,2) DEFAULT NULL,
  `exchange_rate` decimal(18,6) DEFAULT NULL,
  `proposal_state` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `transaction_type` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `business_category` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `company_type` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `community` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `municipality` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `state` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `january_l` decimal(15,2) DEFAULT '0.00',
  `february_l` decimal(15,2) DEFAULT '0.00',
  `march_l` decimal(15,2) DEFAULT '0.00',
  `april_l` decimal(15,2) DEFAULT '0.00',
  `may_l` decimal(15,2) DEFAULT '0.00',
  `june_l` decimal(15,2) DEFAULT '0.00',
  `july_l` decimal(15,2) DEFAULT '0.00',
  `august_l` decimal(15,2) DEFAULT '0.00',
  `september_l` decimal(15,2) DEFAULT '0.00',
  `october_l` decimal(15,2) DEFAULT '0.00',
  `november_l` decimal(15,2) DEFAULT '0.00',
  `december_l` decimal(15,2) DEFAULT '0.00',
  `start_date` date DEFAULT NULL,
  `created_by` bigint unsigned DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `updated_by` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`investment_id`),
  KEY `fk_profit_creator` (`created_by`),
  KEY `idx_profit_partner` (`partner_name`),
  KEY `idx_profit_year` (`year`),
  KEY `idx_profit_state` (`proposal_state`),
  KEY `idx_profit_bank` (`bank_id`),
  KEY `idx_updated_by` (`updated_by`),
  CONSTRAINT `fk_profit_creator` FOREIGN KEY (`created_by`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `profit_form_entries`
--

LOCK TABLES `profit_form_entries` WRITE;
/*!40000 ALTER TABLE `profit_form_entries` DISABLE KEYS */;
INSERT INTO `profit_form_entries` VALUES (1,NULL,'ESMUPROMARG #2',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Conversion',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(2,NULL,'CREDIESPERANZA',2024,NULL,NULL,NULL,10.00,NULL,NULL,NULL,NULL,'Presented','Conversion',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(3,NULL,'Crac Fe y Esperanza del Espinito',2024,'MIGUEL RODRIGUEZ',NULL,1113259.33,2.38,5566296.67,132645.93,5253.30,NULL,'Executed','Disbursement',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,132645.93,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(4,NULL,'Crac Nueva Esperzanza del Canton',2024,'MIGUEL RODRIGUEZ',NULL,160628.43,12.50,803142.15,100392.77,3975.95,NULL,'Rejected','Disbursement','AGRICULTURE (CASHEW)','ESM','RIO GRANDE','EL TRIUNFO','CHOLUTECA',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(5,NULL,'Crac Unidos para el Desarrollo',2024,'MIGUEL RODRIGUEZ','Big Partner Proposal',278234.00,8.00,1391170.00,111293.60,4407.67,NULL,'Presented','Disbursement','COMMERCE','CAJA DE AHORRO Y CREDITO','BARRIO PIEDRAS AZULES','CHOLUTECA','CHOLUTECA',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(6,NULL,'Crac El Porvenir de Santa Rosa #2',2024,'MIGUEL RODRIGUEZ','Cash + Laptop',233322.00,10.00,1166610.00,116661.00,4620.24,NULL,'Rejected','Conversion','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','EL ESPINITO','SAN MATIAS','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(7,NULL,'Crac Ebenezer El Corralito',2023,'MIGUEL RODRIGUEZ','Ellos aceptaron la Propuesta Original en el 2020. Podriamos retomar el Tema',485084.00,9.00,2425420.00,218287.80,8645.06,NULL,'Rejected','Conversion','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','EL CANTON','TEUPASENTI','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2023-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(8,NULL,'Crac Renacer 2000',NULL,'MIGUEL RODRIGUEZ','Ellos aceptaron la Propuesta Original en el 2020. Podriamos retomar el Tema',NULL,NULL,NULL,NULL,NULL,NULL,'Rejected','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','EL RETIRO','MOROCELI','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(9,NULL,'Crac El Pinabetal',NULL,'MIGUEL RODRIGUEZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Rejected','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','SANTA ROSA #2','TEUPASENTI','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(10,NULL,'Crac Nuevo Amanecer',NULL,'MIGUEL RODRIGUEZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Rejected','Disbursement','AGRICULTURE (VEGGIES)','CAJA RURAL DE AHORRO Y CREDITO','EL CORRALITO','OROPOLI','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(11,NULL,'ADPROCADE',2024,'MIGUEL RODRIGUEZ',NULL,150986.00,10.00,754930.00,75493.00,2989.82,NULL,'Rejected','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','VILLA RICA','DANLI','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(12,NULL,'Crac MANANTIALES DE VIDA',2024,'MIGUEL RODRIGUEZ',NULL,117495.00,20.00,587475.00,117495.00,4653.27,NULL,'Executed','Conversion','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','GUINOPE','GUINOPE','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(13,NULL,'Crac Uniendo Esfuerzos de San Jose de Ramos',2024,'MIGUEL RODRIGUEZ',NULL,NULL,10.00,NULL,NULL,NULL,NULL,'Rejected','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','EL PORTILLO','TEUPASENTI','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(14,NULL,'CRAC Tierras del Sol',NULL,'CARLOS CONTRERAS',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Rejected','Disbursement','FOOTWEAR','ASOCIACION DE PRODUCTORES',NULL,NULL,'FRANCISCO MORAZAN',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(15,NULL,'CRAC Union y Esfuerzo Culguaque',NULL,'CARLOS CONTRERAS','Loan Convertion (L.100,000) + Laptop + Printer + Starlink',NULL,NULL,NULL,117495.00,NULL,NULL,'Rejected','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','EL TENCHON','CANTARRANAS','FRANCISCO MORAZAN',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(16,NULL,'CRAC Café del Junacate',NULL,'CARLOS CONTRERAS',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Rejected','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','SAN JOSE DE RAMOS','CANTARRANAS','FRANCISCO MORAZAN',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(17,NULL,'CRAC NUEVO PARAISO - EL JUNQUILLO',2024,'CARLOS CONTRERAS',NULL,320514.67,10.00,1602573.35,160257.34,6346.83,NULL,'Accepted','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','REGADILLOS','LEPATERIQUE','FRANCISCO MORAZAN',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(18,NULL,'Crac Agua Escondida',2024,'CARLOS CONTRERAS',NULL,80141.00,20.00,400705.00,80141.00,3173.90,NULL,'Executed','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','CULGUAQUE','LEPATERIQUE','FRANCISCO MORAZAN',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(19,NULL,'Crac Barrera Viva',2024,'CARLOS CONTRERAS',NULL,105269.00,20.00,526345.00,105269.00,4169.07,NULL,'Executed','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','JUNACATE','LEPATERIQUE','FRANCISCO MORAZAN',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(20,NULL,'Crac Cilca #2',2024,'MIGUEL RODRIGUEZ','Cash + Laptop',62300.00,20.00,311500.00,62300.00,2467.33,NULL,'Executed','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','EL JUNQUILLO','GOASCORAN','VALLE',NULL,NULL,NULL,NULL,NULL,NULL,160257.34,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(21,NULL,'Crac El Encanto de Danli',2024,'CARLOS CONTRERAS','Cash + Starlink',35529.00,20.00,177645.00,35529.00,1407.09,NULL,'Accepted','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','AGUA ESCONDIDA','LEPATERIQUE','FRANCISCO MORAZAN',NULL,NULL,NULL,NULL,101461.00,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(22,NULL,'Crac Nueva Finca',2024,'CARLOS CONTRERAS',NULL,38742.00,20.00,193710.00,38742.00,1534.34,NULL,'Accepted','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','LOS NICHOS','LA PAZ','LA PAZ',NULL,NULL,NULL,NULL,NULL,105269.00,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(23,NULL,'Crac Cuscateca',2024,'CARLOS CONTRERAS','Cash + Laptop + Printer',64205.89,20.00,321029.47,64205.89,2542.81,NULL,'Accepted','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','SAN PEDRO','TUTULE','LA PAZ',NULL,NULL,NULL,NULL,NULL,62300.00,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(24,NULL,'Crac Cerro Bonito',NULL,'MIGUEL RODRIGUEZ','They said YES to Proposal, However, they would like to Pay the Current Loan First. So basically, the execution will be for next year',NULL,NULL,NULL,NULL,NULL,NULL,'Accepted','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','EL ENCANTO','DANLI','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(25,NULL,'Crac UNION SOCIEDAD - LAS FLORES',2024,'MIGUEL RODRIGUEZ','Estan tramitando RTN y Cuenta',60208.00,20.00,301040.00,60208.00,2384.48,NULL,'Executed','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','EL ENCINO','TEUPASENTI','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(26,NULL,'Crac Indepediente Renovacion',NULL,'MIGUEL RODRIGUEZ','Cash + Laptop + Printer',NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','CUSCATECA','DANLI','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,64205.89,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(27,NULL,'Crac CASILLAS HACIA EL FUTURO',NULL,'CARLOS CONTRERAS','They said YES to Proposal, However, they would like to Pay the Current Loan First. So basically, the execution will be for the end of the year',NULL,NULL,NULL,NULL,NULL,NULL,'Rejected','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','CERRO BONITO','CANTARRANAS','FRANCISCO MORAZAN',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(28,NULL,'ESM PUEBLO ORGANIZADO DEL PEDERNAL',2024,'CARLOS CONTRERAS','Cash',212798.59,20.00,1063992.95,212798.59,8427.67,NULL,'Executed','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','LAS FLORES','MARCALA','LA PAZ',NULL,NULL,NULL,NULL,NULL,60208.00,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(29,NULL,'Crac LOS COPETES UNIDOS POR MAS',2024,'MIGUEL RODRIGUEZ',NULL,112870.00,20.00,564350.00,112870.00,4470.10,NULL,'Accepted','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','EL OLINGO','DANLI','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(30,NULL,'Crac El Guayabal',2024,'CARLOS CONTRERAS',NULL,252530.00,20.00,1262650.00,252530.00,10001.19,NULL,'Accepted','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','CASILLAS','TALANGA','EL PARAISO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(31,NULL,'Crac Union de Sisiguara',2024,'CARLOS CONTRERAS','Cash',60855.00,20.00,304275.00,60855.00,2410.10,NULL,'Accepted','Disbursement','AGRICULTURE (COFFEE)','EMPRESA DE SERVICIOS MULTIPLES','SAN JOSE','LA PAZ','LA PAZ',NULL,NULL,NULL,NULL,NULL,NULL,212798.59,NULL,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(32,NULL,'Crac VISION AL DESARROLLO DE ZACATE BLANCO',2024,'CARLOS CONTRERAS','Cash',71665.00,20.00,358325.00,71665.00,2838.22,NULL,'Executed','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','LOS COPETES','CANTARRANAS','FRANCISCO MORAZAN',NULL,NULL,NULL,NULL,NULL,NULL,NULL,112870.00,NULL,NULL,NULL,NULL,'2024-01-01',NULL,'2025-11-07 19:51:28',NULL,NULL),(33,NULL,'CRAC Union, Esfuerzo, y Esperanza',NULL,'CARLOS CONTRERAS','Cash + Laptop + Impresora Termica',NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','ELL GUAYABAL','SAN JOSE','LA PAZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,252530.00,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(34,NULL,'CRAC LUZ Y ESPERANZA - EL OJOCHAL',NULL,'CARLOS CONTRERAS','Cash',NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','SISIGUARA','MARCALA','LA PAZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,60855.00,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(35,NULL,'CRAC LA LUZ DE SAN AGUSTIN',NULL,'CARLOS CONTRERAS','Cash',NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','ZACATE BLANCO','SANTA ANA','LA PAZ',NULL,NULL,NULL,NULL,NULL,71665.00,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(36,NULL,'APROCAL',NULL,'MIGUEL RODRIGUEZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','COYOL DE LINACA','CHOLUTECA','CHOLUTECA',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(37,NULL,'CRAC NUEVO AMANECER Y ESPERANZA DE YORITO',NULL,'MIGUEL RODRIGUEZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','EL OJOCHAL','MARCOVIA','CHOLUTECA',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(38,NULL,'Crac Nuevo Horizonte de la Patastera',NULL,'MIGUEL RODRIGUEZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','SAN AGUSTIN','NAMASIGUE','CHOLUTECA',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(39,NULL,'Crac Nuevo Esperanza Ayapa',NULL,'MIGUEL RODRIGUEZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (COFFEE)','ASOCIACION DE PRODUCTORES','EL CHAGUITILLO','SULACO','YORO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(40,NULL,'ASOCIACION DE PRODUCTORES AGRICOLAS INMENSA JORNADA',NULL,'MIGUEL RODRIGUEZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','LA ESPERANZA','YORITO','YORO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(41,NULL,'Crac Pueblo Viejo',NULL,'MIGUEL RODRIGUEZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (STAPLE GRAINS)','CAJA RURAL DE AHORRO Y CREDITO','LA PATASTERA','YORITO','YORO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(42,NULL,'CRAC FAMILIAR SAN CARLO ACUSTIS',NULL,'MIGUEL RODRIGUEZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','AGUAS BUENAS','YORO','YORO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(43,NULL,'CRAC Capiro',NULL,'MIGUEL RODRIGUEZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','CAPIRO','YORITO','YORO',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(44,NULL,'CRAC Pueblo Viejo Marcala',NULL,'CARLOS CONTRERAS',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','PUEBLO VIEJO','MARCALA','LA PAZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(45,NULL,'CRAC San Jose La Paz',NULL,'CARLOS CONTRERAS',NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Presented','Disbursement','AGRICULTURE (COFFEE)','CAJA RURAL DE AHORRO Y CREDITO','SAN JOSE','LA PAZ','LA PAZ',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-11-07 19:51:28',NULL,NULL),(50,'1','Wells Fargo',2025,'Noah Dolnick','Test',110000.00,10.00,660000.00,66000.00,2538.46,26.000000,'pitched','conversion','Coffee','Coopertive','SANTA ROSA #1','TEUPASENTI','EL PARAISO',100.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,'2025-11-30',48,'2025-11-30 18:55:02',NULL,'48');
/*!40000 ALTER TABLE `profit_form_entries` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proposal_states`
--

DROP TABLE IF EXISTS `proposal_states`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proposal_states` (
  `proposal_state_id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `state_code` varchar(32) NOT NULL,
  `state_label` varchar(64) NOT NULL,
  PRIMARY KEY (`proposal_state_id`),
  UNIQUE KEY `state_code` (`state_code`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proposal_states`
--

LOCK TABLES `proposal_states` WRITE;
/*!40000 ALTER TABLE `proposal_states` DISABLE KEYS */;
INSERT INTO `proposal_states` VALUES (1,'SUBMITTED','Submitted'),(2,'IN_REVIEW','In Review'),(3,'APPROVED','Approved'),(4,'REJECTED','Rejected'),(5,'PITCHED','Pitched'),(6,'PRESENTED','Presented'),(7,'ACCEPTED','Accepted'),(8,'EXECUTED','Executed'),(9,'TO_PITCH','To Pitch');
/*!40000 ALTER TABLE `proposal_states` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `regions`
--

DROP TABLE IF EXISTS `regions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `regions` (
  `region_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `region_name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `country_code` char(3) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`region_id`),
  UNIQUE KEY `uk_region_name_country` (`region_name`,`country_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `regions`
--

LOCK TABLES `regions` WRITE;
/*!40000 ALTER TABLE `regions` DISABLE KEYS */;
/*!40000 ALTER TABLE `regions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `role_id` smallint unsigned NOT NULL AUTO_INCREMENT,
  `role_name` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`role_id`),
  UNIQUE KEY `role_name` (`role_name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES (1,'ADMIN',NULL),(2,'STAFF',NULL),(3,'COMMUNITY_REP',NULL);
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `staff_profile`
--

DROP TABLE IF EXISTS `staff_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `staff_profile` (
  `user_id` bigint unsigned NOT NULL,
  `first_name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `last_name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  CONSTRAINT `fk_staff_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `staff_profile`
--

LOCK TABLES `staff_profile` WRITE;
/*!40000 ALTER TABLE `staff_profile` DISABLE KEYS */;
INSERT INTO `staff_profile` VALUES (28,'Lakshmi','Nair'),(48,'Noah','Dolnick');
/*!40000 ALTER TABLE `staff_profile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `transaction_types`
--

DROP TABLE IF EXISTS `transaction_types`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transaction_types` (
  `txn_type_id` tinyint unsigned NOT NULL AUTO_INCREMENT,
  `type_code` varchar(32) NOT NULL,
  `type_label` varchar(64) NOT NULL,
  PRIMARY KEY (`txn_type_id`),
  UNIQUE KEY `type_code` (`type_code`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `transaction_types`
--

LOCK TABLES `transaction_types` WRITE;
/*!40000 ALTER TABLE `transaction_types` DISABLE KEYS */;
INSERT INTO `transaction_types` VALUES (1,'DISBURSEMENT','Disbursement'),(2,'DIVIDEND','Dividend'),(3,'CONVERSION','Conversion');
/*!40000 ALTER TABLE `transaction_types` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_roles`
--

DROP TABLE IF EXISTS `user_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_roles` (
  `user_id` bigint unsigned NOT NULL,
  `role_id` smallint unsigned NOT NULL,
  `assigned_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`role_id`),
  KEY `fk_ur_role` (`role_id`),
  CONSTRAINT `fk_ur_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`role_id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_ur_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_roles`
--

LOCK TABLES `user_roles` WRITE;
/*!40000 ALTER TABLE `user_roles` DISABLE KEYS */;
INSERT INTO `user_roles` VALUES (28,2,'2025-11-18 16:14:01'),(48,2,'2025-11-24 17:17:38'),(72,3,'2025-12-05 13:19:31');
/*!40000 ALTER TABLE `user_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `username` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `is_approved` tinyint(1) NOT NULL DEFAULT '0',
  `email_verified` tinyint(1) NOT NULL DEFAULT '0',
  `verification_token` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `verification_token_expiry` datetime DEFAULT NULL,
  `reset_token` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reset_token_expiry` datetime DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `username` (`username`),
  KEY `idx_users_verification_token` (`verification_token`),
  KEY `idx_users_reset_token` (`reset_token`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (28,'lnair@umd.edu','lnair','$2b$12$j3jQ5rg1Goe.Y9qO8Ho2XetD5BNkFSN56XZLJAvsBauuIA9W2sFUy',1,1,1,NULL,NULL,NULL,NULL,'2025-11-18 16:14:01','2025-11-24 12:55:13'),(48,'ndolnick@umd.edu','ndolnick','$2b$12$dW/jmoe8UBgtrzgtjA3nEun04PKZd1nHWWgqerQQZEfz8gXZdKN7O',1,1,1,NULL,NULL,NULL,NULL,'2025-11-24 17:17:38','2025-11-24 20:28:36'),(72,'noahdolnick@gmail.com','noahdolnick','$2b$12$wIdM8w3oUiLAFqoT2gZjGeJjxK3l6N.d65QPBOOYlD4gSKVK5NWya',1,1,1,NULL,NULL,NULL,NULL,'2025-12-05 13:19:31','2025-12-05 14:26:17');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `v_current_exchange_rates`
--

DROP TABLE IF EXISTS `v_current_exchange_rates`;
/*!50001 DROP VIEW IF EXISTS `v_current_exchange_rates`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_current_exchange_rates` AS SELECT 
 1 AS `fx_rate_id`,
 1 AS `from_currency`,
 1 AS `to_currency`,
 1 AS `rate`,
 1 AS `valid_from`,
 1 AS `days_active`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_equity_pipeline_norm`
--

DROP TABLE IF EXISTS `vw_equity_pipeline_norm`;
/*!50001 DROP VIEW IF EXISTS `vw_equity_pipeline_norm`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_equity_pipeline_norm` AS SELECT 
 1 AS `source`,
 1 AS `proposal_state`,
 1 AS `state`,
 1 AS `business_category`,
 1 AS `january_l`,
 1 AS `february_l`,
 1 AS `march_l`,
 1 AS `april_l`,
 1 AS `may_l`,
 1 AS `june_l`,
 1 AS `july_l`,
 1 AS `august_l`,
 1 AS `september_l`,
 1 AS `october_l`,
 1 AS `november_l`,
 1 AS `december_l`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_fx_current`
--

DROP TABLE IF EXISTS `vw_fx_current`;
/*!50001 DROP VIEW IF EXISTS `vw_fx_current`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_fx_current` AS SELECT 
 1 AS `fx_rate_id`,
 1 AS `from_currency`,
 1 AS `to_currency`,
 1 AS `rate`,
 1 AS `valid_from`,
 1 AS `valid_to`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `v_current_exchange_rates`
--

/*!50001 DROP VIEW IF EXISTS `v_current_exchange_rates`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_current_exchange_rates` AS select `fx_rates`.`fx_rate_id` AS `fx_rate_id`,`fx_rates`.`from_currency` AS `from_currency`,`fx_rates`.`to_currency` AS `to_currency`,`fx_rates`.`rate` AS `rate`,`fx_rates`.`valid_from` AS `valid_from`,(to_days(now()) - to_days(`fx_rates`.`valid_from`)) AS `days_active` from `fx_rates` where (`fx_rates`.`valid_to` is null) order by `fx_rates`.`from_currency`,`fx_rates`.`to_currency` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_equity_pipeline_norm`
--

/*!50001 DROP VIEW IF EXISTS `vw_equity_pipeline_norm`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_equity_pipeline_norm` AS select 'MATCHING' AS `source`,`matching_equity_entries`.`proposal_state` AS `proposal_state`,`matching_equity_entries`.`state` AS `state`,`matching_equity_entries`.`business_category` AS `business_category`,`matching_equity_entries`.`january_l` AS `january_l`,`matching_equity_entries`.`february_l` AS `february_l`,`matching_equity_entries`.`march_l` AS `march_l`,`matching_equity_entries`.`april_l` AS `april_l`,`matching_equity_entries`.`may_l` AS `may_l`,`matching_equity_entries`.`june_l` AS `june_l`,`matching_equity_entries`.`july_l` AS `july_l`,`matching_equity_entries`.`august_l` AS `august_l`,`matching_equity_entries`.`september_l` AS `september_l`,`matching_equity_entries`.`october_l` AS `october_l`,`matching_equity_entries`.`november_l` AS `november_l`,`matching_equity_entries`.`december_l` AS `december_l` from `matching_equity_entries` union all select 'PROFIT' AS `source`,`profit_form_entries`.`proposal_state` AS `proposal_state`,`profit_form_entries`.`state` AS `state`,`profit_form_entries`.`business_category` AS `business_category`,`profit_form_entries`.`january_l` AS `january_l`,`profit_form_entries`.`february_l` AS `february_l`,`profit_form_entries`.`march_l` AS `march_l`,`profit_form_entries`.`april_l` AS `april_l`,`profit_form_entries`.`may_l` AS `may_l`,`profit_form_entries`.`june_l` AS `june_l`,`profit_form_entries`.`july_l` AS `july_l`,`profit_form_entries`.`august_l` AS `august_l`,`profit_form_entries`.`september_l` AS `september_l`,`profit_form_entries`.`october_l` AS `october_l`,`profit_form_entries`.`november_l` AS `november_l`,`profit_form_entries`.`december_l` AS `december_l` from `profit_form_entries` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_fx_current`
--

/*!50001 DROP VIEW IF EXISTS `vw_fx_current`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_fx_current` AS select `fr1`.`fx_rate_id` AS `fx_rate_id`,`fr1`.`from_currency` AS `from_currency`,`fr1`.`to_currency` AS `to_currency`,`fr1`.`rate` AS `rate`,`fr1`.`valid_from` AS `valid_from`,`fr1`.`valid_to` AS `valid_to` from (`fx_rates` `fr1` left join `fx_rates` `fr2` on(((`fr1`.`from_currency` = `fr2`.`from_currency`) and (`fr1`.`to_currency` = `fr2`.`to_currency`) and (((`fr1`.`valid_to` is null) and (`fr2`.`valid_to` is null) and (`fr2`.`valid_from` > `fr1`.`valid_from`)) or ((`fr1`.`valid_to` is null) and (`fr2`.`valid_to` is not null)) or ((`fr1`.`valid_to` is not null) and (`fr2`.`valid_to` is not null) and (`fr2`.`valid_from` > `fr1`.`valid_from`)))))) where (`fr2`.`fx_rate_id` is null) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-05 14:40:19
