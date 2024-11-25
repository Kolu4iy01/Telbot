from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from routers.command_router import show_whitelist_menu, UserState
from shared import extract_domain, save_users, users


white_list_router = Router()

# Додавання доменів до вайтлиста
@white_list_router.message(lambda message: message.text == "Додати домен")
async def request_domain(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_data = users.get(user_id, {})
    user_domains = user_data.get('whitelist', [])

    # Перевірка статусу користувача
    if user_data.get('status') == 'demo':
        return await message.answer("❌ Ця функція доступна тільки у платній версії боту.")

    # Перевірка, чи користувач досяг ліміту на 3 домени
    if user_data.get('status') != 'admin' and len(user_domains) >= 3:
        return await message.answer("❌ Ви не можете додати більше 3-х доменів.")

    await message.answer("📩 Відправте посилання на сайт, домен якого ви хочете додати.")
    await state.set_state(UserState.waiting_for_domain)

# Функція для обробки натискання на кнопку "Список доменів"
@white_list_router.message(lambda message: message.text == "Список доменів")
async def list_domains(message: Message, user_id=None):
    user_id = user_id or message.from_user.id
    user_data = users.get(user_id, {})
    user_domains = user_data.get('whitelist', [])

    if not user_domains:
        await message.answer("📋 Ваш вайтлист порожній.")
    else:
        # Створюємо клавіатуру для видалення доменів
        domain_buttons = []

        # Додаємо кнопки для кожного домену
        for domain in user_domains:
            # Кнопка для домену
            domain_buttons.append([KeyboardButton(text=domain)])

        # Додаємо кнопку "Повернутися назад"
        domain_buttons.append([KeyboardButton(text="Повернутися назад")])

        # Формуємо клавіатуру
        domain_keyboard = ReplyKeyboardMarkup(
            keyboard=domain_buttons,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await message.answer("Виберіть домен, який хочете видалити:", reply_markup=domain_keyboard)

# Функція для обробки натискання на домен в вайтлисті для видалення
@white_list_router.message(lambda message: message.text in [domain for domain in users.get(message.from_user.id, {}).get('whitelist', [])])
async def delete_domain(message: Message):
    user_id = message.from_user.id
    domain_to_remove = message.text

    # Видаляємо домен з вайтлиста
    if domain_to_remove in users[user_id].get('whitelist', []):
        users[user_id]['whitelist'].remove(domain_to_remove)
        save_users(users)
        await message.answer(f"✅ Домен {domain_to_remove} видалено з вайтлиста.")
    else:
        await message.answer("❌ Домен не знайдено у вашому вайтлисті.")

    # Повертаємось до списку доменів
    await list_domains(message)

# Функція для обробки натискання на кнопку "Додати домен"
@white_list_router.message(UserState.waiting_for_domain)
async def add_domain(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_domain = message.text

    # Отримуємо домен з URL
    domain = extract_domain(user_domain)

    # Додаємо домен до користувача
    users[user_id]['whitelist'] = users[user_id].get('whitelist', [])
    if domain not in users[user_id]['whitelist']:
        users[user_id]['whitelist'].append(domain)
        save_users(users)  # Зберегти оновлення
        await message.answer(f"✅ Домен {domain} успішно додано до вайтлиста.")
    else:
        await message.answer("❌ Цей домен вже додано до вайтлиста.")

    # Повертаємося до меню вайтлиста
    await show_whitelist_menu(message, state)
