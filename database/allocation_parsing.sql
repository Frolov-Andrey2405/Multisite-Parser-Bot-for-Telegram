CREATE DATABASE allocation_parsing;

USE allocation_parsing;

CREATE TABLE
    Vfx (
        id INT PRIMARY KEY AUTO_INCREMENT,
        link VARCHAR (1000) NOT NULL,
        download_link VARCHAR(1000) NOT NULL
    );

CREATE TABLE
    Blend (
        id INT PRIMARY KEY AUTO_INCREMENT,
        off_link VARCHAR(1000) NOT NULL, 
        url_on_image VARCHAR(1000) DEFAULT NULL
    );

CREATE TABLE
    Version (
        id INT PRIMARY KEY AUTO_INCREMENT,
        product_name VARCHAR(1000) NOT NULL, 
        Vfx_id INT DEFAULT NULL,
        Blend_id INT DEFAULT NULL,
        addon_version VARCHAR(255) DEFAULT NULL,
        FOREIGN KEY (Vfx_id) REFERENCES Vfx(id),
        FOREIGN KEY (Blend_id) REFERENCES Blend(id)
    );
