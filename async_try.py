from bs4 import BeautifulSoup as BS
import asyncio
import aiohttp
import csv
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.5249.103 Safari/537.36'
}

def read_codes():
    codes = []
    with open('codes.txt', 'r', encoding='utf-8') as file:
        for line in file.readlines():
            codes.append(line.strip())

    return codes

codes = read_codes()
length = len(codes)

def get_tasks(session):
    tasks = []
    for code in codes:
        tasks.append(asyncio.create_task(session.get(url=code, headers=headers, ssl=False)))
    return tasks

async def get_data():
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session)
        responses = await asyncio.gather(*tasks)

        for i, response in enumerate(responses):
            html = await response.text()
            code = codes[i]

            print(f'{i + 1}/{length}')

            soup = BS(html, 'lxml')
            rows = soup.find('table', 'swift-detail').find('tbody').find_all('tr')

            bank = ''
            branch = ''
            address = ''
            city = ''
            postal_code = ''
            country = ''

            for row in rows:
                if row.find('th').text.strip() == 'Bank / Institution':
                    bank = row.find('td').text.strip()
                elif row.find('th').text.strip() == 'Branch Name':
                    branch = row.find('td').text.strip()
                elif row.find('th').text.strip() == 'Address':
                    address = row.find('td').text.strip()
                elif row.find('th').text.strip() == 'City':
                    city = row.find('td').text.strip()
                elif row.find('th').text.strip() == 'Postcode':
                    postal_code = row.find('td').text.strip()
                elif row.find('th').text.strip() == 'Country':
                    country = row.find('td').text.strip()

            with open('async_result.csv', 'a', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    code.split("/")[-2], code, bank, branch, address, city, postal_code, country
                ])

def main():
    t0 = time.time()
    asyncio.run(get_data())
    print(time.time() - t0)

if __name__ == '__main__':
    main()