CREATE DATABASE allocation_parsing;

USE allocation_parsing;

CREATE TABLE
    Vault (
        id INT AUTO_INCREMENT PRIMARY KEY,
        link VARCHAR(255),
        header VARCHAR(255),
        download_link VARCHAR(255),
        official_link VARCHAR(255),
        official_image_links VARCHAR(225)
    );
