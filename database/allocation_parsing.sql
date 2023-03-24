CREATE DATABASE allocation_parsing;

USE allocation_parsing;

CREATE TABLE
    Vfx (
        id INT PRIMARY KEY AUTO_INCREMENT,
        link VARCHAR (400) NOT NULL UNIQUE,
        download_link VARCHAR(400) NOT NULL UNIQUE,
        data_created DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP)
    );

CREATE TABLE
    Blend (
        id INT PRIMARY KEY AUTO_INCREMENT,
        off_link VARCHAR(400) NOT NULL UNIQUE, 
        url_on_image VARCHAR(400) DEFAULT NULL,
        data_created DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP)
    );

CREATE TABLE
    Version (
        id INT PRIMARY KEY AUTO_INCREMENT,
        product_name VARCHAR(400) NOT NULL, 
        Vfx_id INT DEFAULT NULL,
        Blend_id INT DEFAULT NULL,
        addon_version VARCHAR(255) DEFAULT NULL,
        data_created DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
        FOREIGN KEY (Vfx_id) REFERENCES Vfx(id) ON DELETE CASCADE,
        FOREIGN KEY (Blend_id) REFERENCES Blend(id) ON DELETE SET NULL,
        UNIQUE (product_name, addon_version)
    );
