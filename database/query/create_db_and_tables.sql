CREATE DATABASE allocation_parsing;

USE allocation_parsing;

CREATE TABLE
    vfx (
        link VARCHAR(300) NOT NULL UNIQUE,
        download_link VARCHAR(300) NOT NULL UNIQUE,
    );


CREATE TABLE
    blend(
        off_link VARCHAR(300) NOT NULL UNIQUE,
        url_on_image 
    )