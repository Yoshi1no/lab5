import json
import requests


with open("config.json", "r") as config_file:
    config = json.load(config_file)


API_KEY = config["api_key"]
BASE_URL = "https://api.ataix.kz"



def make_api_request(endpoint):

    url = f"{BASE_URL}{endpoint}"
    headers = {
        "API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Проверка на ошибки HTTP
        return response.json()
    except requests.exceptions.Timeout:
        return "⏳ Ошибка: Превышено время ожидания ответа от сервера."
    except requests.exceptions.RequestException as e:
        return f"❌ Ошибка запроса: {e}"



def fetch_currencies():

    return make_api_request("/api/currencies")



def fetch_symbols():

    return make_api_request("/api/symbols")



def fetch_prices():

    return make_api_request("/api/prices")



def main():

    print("🌟 Добро пожаловать в программу для работы с API биржи Ataix! 🌟")

    while True:
        print("\n" + "=" * 50)
        print("Выберите действие:")
        print("1 - Получить список всех валют")
        print("2 - Получить список всех торговых пар")
        print("3 - Получить цены всех монет и токенов")
        print("exit - Выйти из программы")
        print("=" * 50)

        command = input("Введите команду: ").strip().lower()

        if command == "1":
            print("\n🪙 Список всех валют:")
            result = fetch_currencies()
            print(json.dumps(result, indent=4))  # Красивый вывод JSON
        elif command == "2":
            print("\n💹 Список всех торговых пар:")
            result = fetch_symbols()
            print(json.dumps(result, indent=4))
        elif command == "3":
            print("\n💰 Цены всех монет и токенов:")
            result = fetch_prices()
            print(json.dumps(result, indent=4))
        elif command == "exit":
            print("\n🚪 Выход из программы. До свидания! 👋")
            break
        else:
            print("\n❌ Неизвестная команда. Пожалуйста, попробуйте снова.")



if __name__ == "__main__":
    main()