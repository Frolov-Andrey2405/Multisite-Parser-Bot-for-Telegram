import mysql.connector
import json
import os


cnx = mysql.connector.connect(
    user='root', password='PASSWORD',
    host='127.0.0.1', database='allocation_parsing')

cursor = cnx.cursor()


def read_json(json_file):
    data = []
    with open(json_file, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def insert_rows(data, table_name):
    '''Define a function to insert rows into the database table'''
    for row in data:
        column_names = ", ".join(row.keys())
        placeholders = ", ".join(["%s"] * len(row))
        query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        values = tuple(row.values())
        cursor.execute(query, values)
        cnx.commit()


# Read the .json files and insert the rows into the appropriate tables
links = read_json('vfxmed/json/links.json')
insert_rows(links, 'Vault')

headers = read_json('vfxmed/json/headers.json')
insert_rows(headers, 'Vault')

download_links = read_json('vfxmed/json/download_link.json')
insert_rows(download_links, 'Vault')

official_links = read_json('blendermarket/json/official_links.json')
insert_rows(official_links, 'Vault')

official_image_links = read_json(
    'blendermarket/json/official_image_links.json')
insert_rows(official_links, 'Vault')

# Close the connection
cursor.close()
cnx.close()
