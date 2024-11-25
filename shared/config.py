import os
import logging
from dotenv import load_dotenv

# Define the path to the .env file
env_path = '.env'

# Load the environment variables from the .env file
load_dotenv(env_path)

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

USERS_FILE = 'users.json'
PROXY_FILE = 'proxy.json'

def get_env_value(key):
    if key in os.environ:
        return os.environ[key]
    raise KeyError(f"Environment variable '{key}' not found")

API_TOKEN = get_env_value('API_TOKEN')

# Дані проксі
USE_PROXY_1 = get_env_value('USE_PROXY_1') == 'True'
PROXY_IP_1 = get_env_value('PROXY_IP_1')
PROXY_PORT_1 = get_env_value('PROXY_PORT_1')
PROXY_LOGIN_1 = get_env_value('PROXY_LOGIN_1')
PROXY_PASSWORD_1 = get_env_value('PROXY_PASSWORD_1')

USE_PROXY_2 = get_env_value('USE_PROXY_2') == 'True'
PROXY_IP_2 = get_env_value('PROXY_IP_2')
PROXY_PORT_2 = get_env_value('PROXY_PORT_2')
PROXY_LOGIN_2 = get_env_value('PROXY_LOGIN_2')
PROXY_PASSWORD_2 = get_env_value('PROXY_PASSWORD_2')

USE_PROXY_3 = get_env_value('USE_PROXY_3') == 'True'
PROXY_IP_3 = get_env_value('PROXY_IP_3')
PROXY_PORT_3 = get_env_value('PROXY_PORT_3')
PROXY_LOGIN_3 = get_env_value('PROXY_LOGIN_3')
PROXY_PASSWORD_3 = get_env_value('PROXY_PASSWORD_3')

# Глобальні змінні для зберігання стану бота
user_state = {}
user_urls = {}
active_sessions = {}  # Активні сесії (посилання)
active_sending = {} # Маркер активної відправки
active_tasks = {}  # Активні задачі
user_request_counter = {}
user_durations = {}  # Тривалість для кожного користувача
user_frequencies = {}  # Частота для кожного користувача

# Список вибору частоти відправки
frequency_options = ["Без затримки 🚀", "1 заявка в 10 секунд ⏳", "1 заявка в 10 хвилин ⌛", "1 заявка в 60 хвилин ⌛"]

# Список вибору тривалості відправки
duration_options = ["1 хвилина ⏳", "15 хвилин ⏳", "30 хвилин ⏳", "1 година ⏳", "3 години ⏳", "Необмежено ⏳"]
