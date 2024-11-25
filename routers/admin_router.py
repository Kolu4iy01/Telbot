from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ReplyKeyboardMarkup, KeyboardButton,Message, InlineKeyboardMarkup, InlineKeyboardButton

from routers.command_router import UserState
from shared import user_state, status_translation, get_user_status, get_start_keyboard, save_users, users, load_proxies, save_proxies,is_valid_ip, is_valid_port
from aiogram.fsm.state import State, StatesGroup


admin_router = Router()

# Стан для редагування проксі
class ProxyEditStates(StatesGroup):
    waiting_for_ip = State()
    waiting_for_port = State()
    waiting_for_username = State()
    waiting_for_password = State()

# Обробка запиту на редагування проксі
@admin_router.callback_query(lambda callback_query: callback_query.data.startswith('edit_proxy_'))
async def edit_proxy(callback_query: CallbackQuery, state: FSMContext):
    proxy_index = int(callback_query.data.split('_')[2])
    await callback_query.message.answer("🔄 Введіть новий IP для проксі.")
    await state.update_data(proxy_index=proxy_index)
    await state.set_state(ProxyEditStates.waiting_for_ip)


# Обробка IP
@admin_router.message(ProxyEditStates.waiting_for_ip)
async def process_ip(message: Message, state: FSMContext):
    user_data = await state.get_data()
    proxy_index = user_data['proxy_index']

    if not is_valid_ip(message.text):
        await message.answer("⚠️ Невірний формат IP. Спробуйте ще раз.")
        return

    proxies = load_proxies()
    proxies[proxy_index]['ip'] = message.text
    save_proxies(proxies)

    await message.answer("🔄 Введіть новий порт для проксі.")
    await state.set_state(ProxyEditStates.waiting_for_port)


# Обробка порту
@admin_router.message(ProxyEditStates.waiting_for_port)
async def process_port(message: Message, state: FSMContext):
    user_data = await state.get_data()
    proxy_index = user_data['proxy_index']

    if not message.text.isdigit() or not (1 <= int(message.text) <= 65535):
        await message.answer("⚠️ Невірний формат порту. Порт має бути числом від 1 до 65535. Спробуйте ще раз.")
        return

    proxies = load_proxies()
    proxies[proxy_index]['port'] = message.text
    save_proxies(proxies)

    await message.answer("🔄 Введіть новий логін для проксі.")
    await state.set_state(ProxyEditStates.waiting_for_username)


# Обробка логіна
@admin_router.message(ProxyEditStates.waiting_for_username)
async def process_username(message: Message, state: FSMContext):
    user_data = await state.get_data()
    proxy_index = user_data['proxy_index']

    proxies = load_proxies()
    proxies[proxy_index]['username'] = message.text
    save_proxies(proxies)

    await message.answer("🔄 Введіть новий пароль для проксі.")
    await state.set_state(ProxyEditStates.waiting_for_password)


# Обробка пароля
@admin_router.message(ProxyEditStates.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    user_data = await state.get_data()
    proxy_index = user_data['proxy_index']

    proxies = load_proxies()
    proxies[proxy_index]['password'] = message.text
    save_proxies(proxies)

    await message.answer("✅ Проксі було успішно оновлено!")
    await manage_proxies(message)

    await state.clear()


# Функція для управління проксі
@admin_router.message(lambda message: message.text == "🪄 Керувати проксі")
async def manage_proxies(message: Message):
    proxies = load_proxies()
    if not proxies:
        await message.answer("📋 У вас немає налаштованих проксі.")
        return

    for i, proxy in enumerate(proxies):
        await message.answer(build_proxy_info_message(proxy, i), reply_markup=build_proxy_keyboard(proxy['enabled'], i))


def build_proxy_info_message(proxy, index):
    return (
        f"🌐 Проксі {index + 1}:\n"
        f"IP: {proxy.get('ip', 'Невідомо')}\n"
        f"Порт: {proxy.get('port', 'Невідомо')}\n"
        f"Логін: {proxy.get('username', 'Невідомо')}\n"
        f"Пароль: {proxy.get('password', 'Невідомо')}\n"
    )


def build_proxy_keyboard(is_enabled, proxy_index):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Вимкнути" if is_enabled else "Ввімкнути",
                callback_data=f"toggle_proxy_{proxy_index}_{'off' if is_enabled else 'on'}"
            ),
            InlineKeyboardButton(
                text="Редагувати",
                callback_data=f"edit_proxy_{proxy_index}"
            )
        ]
    ])
    return keyboard


@admin_router.callback_query(lambda callback_query: callback_query.data.startswith('toggle_proxy_'))
async def toggle_proxy(callback_query: CallbackQuery):
    proxy_index = int(callback_query.data.split('_')[2])
    proxies = load_proxies()

    if proxy_index < len(proxies):
        proxy = proxies[proxy_index]
        new_status = not proxy.get('enabled', False)
        proxy['enabled'] = new_status

        # Зберегти новий статус
        save_proxies(proxies)

        await callback_query.answer(f"✅ Проксі {proxy_index + 1} було {'ввімкнено' if new_status else 'вимкнено'}.")

        # Створити новий reply_markup
        new_reply_markup = build_proxy_keyboard(new_status, proxy_index)

        # Оновити reply_markup
        await callback_query.message.edit_reply_markup(reply_markup=new_reply_markup)
    else:
        await callback_query.answer("❌ Проксі не знайдено.")




#___________________________________________________________________________________

# Обробник введення Telegram ID для зміни статусу користувача
@admin_router.message(UserState.waiting_for_user_id)
async def handle_user_id_input(message: Message, state: FSMContext):
    user_id = message.from_user.id
    target_user_id = message.text.strip()
    user_status = get_user_status(user_id)

    if target_user_id.isdigit() and int(target_user_id) in users:
        await state.set_state(UserState.waiting_for_new_status)
        user_state['target_user_id'] = int(target_user_id)
        await message.answer(
            f"🚦 Виберіть новий статус для користувача(Current Status:{user_status}):",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="demo")],
                    [KeyboardButton(text="unlim")],
                    [KeyboardButton(text="admin")]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
    else:
        await message.answer("⚠️ Некоректний ID або користувач не знайдений. Введіть правильний Telegram ID.")

# Обробник вибору нового статусу для користувача
@admin_router.message(UserState.waiting_for_new_status)
async def handle_new_status_selection(message: Message, state: FSMContext):
    admin_id = message.from_user.id
    new_status = message.text.strip()
    target_user_id = user_state.get('target_user_id')

    if new_status in ["demo", "unlim", "admin"]:
        users[target_user_id]['status'] = new_status
        save_users(users)  # Зберігаємо зміни
        await message.answer(f"✅ Статус користувача з ID {target_user_id} змінено на {status_translation.get(new_status, new_status)}.", reply_markup=get_start_keyboard(admin_id))
        await state.set_state(UserState.waiting_for_start)
    else:
        await message.answer("⚠️ Некоректний статус. Будь ласка, виберіть із запропонованих варіантів.")
