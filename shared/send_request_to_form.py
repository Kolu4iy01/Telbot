import asyncio
import random
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit


from shared.config import (USE_PROXY_1, USE_PROXY_2, USE_PROXY_3, PROXY_IP_1, PROXY_PORT_1, PROXY_LOGIN_1,
    PROXY_PASSWORD_1, PROXY_IP_2, PROXY_PORT_2, PROXY_LOGIN_2, PROXY_PASSWORD_2, PROXY_IP_3, PROXY_PORT_3,
    PROXY_LOGIN_3, PROXY_PASSWORD_3, user_request_counter, logger)
from shared.funcs import generate_name, generate_phone_number, load_proxies


async def send_request_to_form(url, user_id):
    logger.info(f"Запит до форми: {url}")

    # Завантаження проксі з файлу
    proxies = load_proxies()
    active_proxies = [proxy for proxy in proxies if proxy.get('enabled')]  # Фільтрація активних проксі

    attempts = 3  # Загальна кількість спроб

    for attempt in range(attempts):
        proxy_url = random.choice(active_proxies) if active_proxies else None
        proxy_string = f"http://{proxy_url['ip']}:{proxy_url['port']}" if proxy_url else None
        logger.info(f"Використання запиту з проксі: {proxy_string}" if proxy_string else "Використання запиту без проксі.")

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            try:
                logger.info(f"Надсилаємо GET запит до: {url}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
                }

                async with session.get(url, proxy=proxy_url, headers=headers) as response:
                    logger.info(f"Отримано відповідь: {response.status}")
                    if response.status != 200:
                        if attempt < attempts - 1:  # Якщо це не остання спроба
                            logger.warning(
                                "Сайт недоступний. Спробуємо ще раз...")
                            await asyncio.sleep(10)  # Затримка перед повтором
                            continue  # Повертаємось до початку циклу
                        return f"Сайт недоступний. Код статусу: {response.status}."

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    form = soup.find('form')

                    if not form:
                        return "Форма не знайдена."

                    action = form.get('action')
                    if action:
                        if not action.startswith('http'):
                            # base_url = user_urls[user_id]
                            base_url = url
                            split_url = urlsplit(base_url)
                            base_url_without_query = urlunsplit(
                                (split_url.scheme, split_url.netloc, split_url.path.rstrip('/') + '/', '', ''))
                            action = f"{base_url_without_query}{action.lstrip('/')}"

                        logger.info(f"Формований URL дії: {action}")

                    data = {}
                    inputs = form.find_all('input')
                    for input_tag in inputs:
                        input_name = input_tag.get('name')
                        input_type = input_tag.get('type')

                        if input_type == 'name' or input_name == 'name':
                            data[input_name] = generate_name()

                        elif input_type == 'tel' or input_name == 'phone' or input_name == 'tel':
                            data[input_name] = generate_phone_number()

                        elif input_type == 'checkbox':
                            data[input_name] = 'on'

                    selects = form.find_all('select')
                    for select in selects:
                        select_name = select.get('name')
                        options = select.find_all('option')
                        valid_options = [
                            option for option in options if option.get('value')]
                        if valid_options:
                            selected_option = random.choice(valid_options).get('value')
                            data[select_name] = selected_option

                    logger.info(f"Дані, які будуть надіслані: {data}")

                    for post_attempt in range(attempts):
                        async with session.post(action, data=data, proxy=proxy_url) as post_response:
                            if post_response.status == 200:
                                logger.info(
                                    f"Запит на {action} успішно надіслано.")
                                user_request_counter[user_id][url] += 1
                                return None  # Успішно відправлено
                            else:
                                logger.error(f"Помилка при відправці: {post_response.status}")
                                if post_attempt < attempts - 1:  # Якщо це не остання спроба
                                    # Затримка 10 секунд перед повтором
                                    await asyncio.sleep(10)
                                else:
                                    return "Не вдалося відправити заявку."

            except aiohttp.ClientError as e:
                logger.error(f"Помилка при використанні проксі: {e}")
                if attempt < attempts - 1:  # Якщо це не остання спроба
                    # Затримка 10 секунд перед повтором
                    await asyncio.sleep(10)
                else:
                    return "Проблема з проксі."

    return None  # Успішно відправлено