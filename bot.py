import requests

# Замените <TOKEN> и <ADMIN_CHAT_ID> вашими значениями
TOKEN = "YOUR_TOKEN"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"
ADMIN_CHAT_ID = "YOUR_ADMIN_CHAT_ID"
# Словарь для хранения ID группы/чата для каждого пользователя
user_groups = {}

# Инициализируем сессию для оптимизации запросов
session = requests.Session()


def get_updates(offset=None):
    response = session.get(
        BASE_URL + "getUpdates", params={"timeout": 100, "offset": offset}
    )
    return response.json().get("result", [])


def send_message(chat_id, text):
    response = session.post(
        BASE_URL + "sendMessage", params={"chat_id": chat_id, "text": text}
    )
    if response.json().get("ok"):
        print(f"Сообщение успешно отправлено в чат {chat_id}: {text}")
    else:
        print(f"Ошибка при отправке сообщения в чат {chat_id}: {response.json()}")


def handle_message(message):
    chat_id = message["chat"]["id"]
    text = message.get("text")
    user_id = message["from"]["id"]
    chat_type = message["chat"]["type"]
    # Обрабатываем сообщения от пользователей
    if chat_id != int(ADMIN_CHAT_ID):
        if chat_type in ["group", "supergroup"] and text:
            # Сохраняем пользователя и группу
            user_groups[user_id] = chat_id
            print(f"Сохраняем пользователя {user_id} и группу {chat_id} в user_groups")
            send_message(
                ADMIN_CHAT_ID, f"User [{user_id}] in group [{chat_id}] says: {text}"
            )
        elif text:
            # Личное сообщение от пользователя
            send_message(ADMIN_CHAT_ID, f"User [{chat_id}] says: {text}")
    elif chat_id == int(ADMIN_CHAT_ID) and text:
        # Обработка ответа от администратора
        process_admin_response(text)


def process_admin_response(text):
    parts = text.split(":", 1)
    if len(parts) == 2:
        try:
            target_user_id = int(parts[0].strip())
            admin_response = parts[1].strip()
            group_id = user_groups.get(target_user_id)

            if group_id:
                print(
                    f"Отправляем ответ в группу {group_id} для пользователя {target_user_id}"
                )
                send_message(
                    group_id,
                    f"Ответ для пользователя [{target_user_id}]: {admin_response}",
                )
            else:
                print(
                    f"Не найден ID группы для пользователя {target_user_id} в user_groups"
                )
        except ValueError:
            print(
                "Ошибка: Неверный формат user_id. Убедитесь, что user_id — это число."
            )
    else:
        print(
            "Ошибка: Неверный формат сообщения от администратора. Используйте формат 'user_id: сообщение'."
        )


def main():
    update_id = None
    while True:
        updates = get_updates(update_id)
        for update in updates:
            update_id = update["update_id"] + 1  # Обновляем offset
            if "message" in update:
                handle_message(update["message"])


if __name__ == "__main__":
    main()
