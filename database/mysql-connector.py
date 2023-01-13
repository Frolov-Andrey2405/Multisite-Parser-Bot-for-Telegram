import asyncio
import aiomysql
import json


async def insert_data(conn, data, table):
    async with conn.cursor() as cursor:

        if table == "Vfxmed":
            sql = "INSERT INTO Vfxmed (link, title, download_link) VALUES (%s, %s, %s)"
            values = (
                data["link"],
                data["title"],
                data["download_link"])

        elif table == "BlenderMarket":
            sql = "INSERT INTO BlenderMarket (off_link, name_of_tools, url_on_image) VALUES (%s, %s, %s)"
            values = (
                data["off_link"],
                data["name_of_tools"],
                data["url_on_image"])
        await cursor.execute(sql, values)


async def main():
    async with aiomysql.connect(
        host='127.0.0.1',
        user='root',
        password='Frolov24.05',
        db='allocation_parsing',
        loop=asyncio.get_event_loop()
    ) as conn:

        # Read the data from the vfxmed.json file
        with open("vfxmed/json/vfxmed.json", "r") as file:
            for line in file:
                data = json.loads(line)
                await insert_data(conn, data, "Vfxmed")

        # Read the data from the blend.json file
        with open("blendermarket/json/blend.json", "r") as file:
            for line in file:
                data = json.loads(line)
                await insert_data(conn, data, "BlenderMarket")

        await conn.commit()


if __name__ == '__main__':
    asyncio.run(main())
