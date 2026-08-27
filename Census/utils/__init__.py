
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pathlib import Path
import openpyxl as op
import aiohttp
import asyncio
from asgiref.sync import async_to_sync

def excel_extract_data():

    """Extract primitive project registrated in the google sheet : https://docs.google.com/spreadsheets/d/1xEcKM5Q09Q18uC5qTziD0pb1wt5_p2W96kuGoNWo-BE/edit?gid=0

    :return dict:

    """

    BASE_DIR = Path(__file__).resolve().parent
    try:
        projects = op.load_workbook(BASE_DIR / 'project.xlsx', data_only=True)
        sheet = projects.active
    except FileNotFoundError:
        print("Erreur : Le fichier 'project.xlsx' est introuvable.")
        exit()

    project_dict = {}
    categories = []
    current_category = None

    merged_ranges = sheet.merged_cells.ranges

    for row in sheet.iter_rows(min_col=4, max_col=13, min_row=3, max_row=144):
        row_key_cell = row[0]
        row_key_value = row_key_cell.value
        
        if row_key_value == 'Name' or None:
            continue

        is_merged = any(row_key_cell.coordinate in r for r in merged_ranges)

        if is_merged:
            cat_name = str(row_key_value).upper()
            if cat_name not in categories:
                categories.append(cat_name)
            current_category = cat_name
            continue
        if current_category:
            row_data = []
            for cell in row:
                if cell.value is not None:
                    row_data.append(cell.value)
            
            row_data.append(current_category)
            project_dict[row_key_value] = row_data

    return {'project': project_dict, 'categories': categories}


async def get_sync_favicon(url: str) -> str:
    """Get the website icon based on its url (async version)

    :param url: the website url
    :type url: str

    :return full_url: the icon url
    :rtype: str
    """
    try:
        if not url:
            return ''

        if not url.startswith('http'):
            url = 'https://' + url

        headers = {'User-Agent': 'Mozilla/5.0'}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')
        icon_link = soup.find("link", rel=lambda x: x and 'icon' in x.lower())
        favicon_url = icon_link.get('href') if icon_link else '/favicon.ico'
        full_url = urljoin(url, favicon_url)
        return full_url
    except Exception as e:
        print(f"❌ Error : {e}")
        return ''

@async_to_sync
async def get_async_favicon(url: str) -> str:
    """Get the website icon based on its url (async version)

    :param url: the website url
    :type url: str

    :return full_url: the icon url
    :rtype: str
    """
    try:
        if not url:
            return ''

        if not url.startswith('http'):
            url = 'https://' + url

        headers = {'User-Agent': 'Mozilla/5.0'}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                html = await response.text()

        soup = BeautifulSoup(html, 'html.parser')
        icon_link = soup.find("link", rel=lambda x: x and 'icon' in x.lower())
        favicon_url = icon_link.get('href') if icon_link else '/favicon.ico'
        full_url = urljoin(url, favicon_url)
        return full_url
    except Exception as e:
        print(f"❌ Error : {e}")
        return ''
