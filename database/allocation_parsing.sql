CREATE DATABASE allocation_parsing;

USE allocation_parsing;

CREATE TABLE
    Vfxmed (
        link VARCHAR(300) NOT NULL,
        title VARCHAR(300) NOT NULL,
        download_link VARCHAR(300) NOT NULL
    );

CREATE TABLE
    BlenderMarket(
        off_link VARCHAR(300) NOT NULL,
        name_of_tools VARCHAR(300) NOT NULL,
        url_on_image VARCHAR(1000) NOT NULL
    );

SELECT
    v.link,
    v.title,
    v.download_link,
    b.off_link,
    b.name_of_tools,
    b.url_on_image
FROM Vfxmed AS v
    LEFT JOIN BlenderMarket AS b ON v.title LIKE CONCAT('%', b.name_of_tools, '%')