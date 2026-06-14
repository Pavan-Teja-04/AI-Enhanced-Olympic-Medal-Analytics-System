CREATE DATABASE IF NOT EXISTS olympics_db;
USE olympics_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(180) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS olympic_medals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    year INT NOT NULL,
    country VARCHAR(150) NOT NULL,
    sport VARCHAR(150) NOT NULL,
    event_name VARCHAR(255) NOT NULL,
    medal ENUM('Gold', 'Silver', 'Bronze') NOT NULL,
    INDEX idx_country (country),
    INDEX idx_sport (sport),
    INDEX idx_year (year),
    UNIQUE KEY unique_medal_event (year, country, sport, event_name, medal)
);
