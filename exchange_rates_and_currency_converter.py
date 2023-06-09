import requests
import tkinter as tk
from tkinter import ttk


class Currency:                #класс валюты, у каждой валюты есть называние, стоимость (в рублях), номинал( больше 1 если слишком большая разница в цене), стоиость в долларах, CharCode
    def __init__(self, name, value, nominal, value_usd, symbol):
        self.name = name
        self.value = value
        self.nominal = nominal
        self.value_usd = value_usd
        self.symbol = symbol


def take_price(metal_price):                               #метод, берёт цену металла с сайта
    metal_price = metal_price.replace("dict_values(['", "")
    metal_price = metal_price.replace("'])", "")
    return float(metal_price)


def print_all_currencies(currency_data):                   #вывод стоимости всех вают и металлов
    print("Все валюты:")
    currencies = currency_data['Valute']
    for currency in currencies.values():
        name = currency['Name']
        value = currency['Value']
        nominal = currency['Nominal']
        value_usd = currency['Value'] / currency_data['Valute']['USD']['Value']
        symbol = currency['CharCode']
        currency_obj = Currency(name, value, nominal, value_usd, symbol)
        print_currency(currency_obj)

    ruble = Currency("Российский рубль", 100, 100, currency_data['Valute']['USD']['Value'], "RUB")
    print_currency(ruble)


def print_currency(currency):
    print(f"Название: {currency.name} ({currency.symbol})")
    print(f"Номинал: {currency.nominal}")
    print(f"Стоимость в рублях: {currency.value}")
    print(f"Стоимость в долларах: {currency.value_usd:.4f}")
    print("-------------------------")


def get_currency_data():
    try:
        currency_response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
        currency_response.raise_for_status()
        currency_data = currency_response.json()

        metall_response = requests.get('https://api.metals.live/v1/spot')
        metall_response.raise_for_status()
        metall_data = metall_response.json()

        return currency_data, metall_data

    except requests.exceptions.HTTPError as http_err:                          #обработка ошибок связи с сайтом
        print(f"HTTP error occurred: {http_err}")
        return None, None

    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
        return None, None

    except requests.exceptions.Timeout as timeout_err:
        print(f"Request timeout occurred: {timeout_err}")
        return None, None

    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred during the request: {req_err}")
        return None, None


def currency_converter(currency_data):                                    #конвертер валют
    currencies = currency_data['Valute']
    currencies['RUB'] = {'Name': 'Российский рубль', 'Value': 1.0, 'Nominal': 1}

    def convert():
        currency_input_1 = currency_combobox_1.get()                      #выбирается валюта из списка, из которой переводятся средства
        currency_input_2 = currency_combobox_2.get()                      #выбирается вторая из списка, в которую переводятся средства
        amount = float(amount_entry.get())                                #сумма средства в первой валюте
        if amount < 0:
            result_label.config(text="Ошибка: Сумма должна быть положительна.")
        else:
            try:
                value_1 = currencies[currency_input_1]['Value']
                nominal_1 = currencies[currency_input_1]['Nominal']
                value_2 = currencies[currency_input_2]['Value']
                nominal_2 = currencies[currency_input_2]['Nominal']

                ratio = (value_1 / nominal_1) / (value_2 / nominal_2)
                converted_amount = amount * ratio

                result_label.config(text=f"{amount:.2f} {currency_input_1} равно {converted_amount:.2f} {currency_input_2}")

            except KeyError:
                result_label.config(text="Ошибка: Неверная валюта.")

    def refresh():                                        #обновленние данных
        nonlocal currency_data
        currency_data, _ = get_currency_data()
        update_currency_names()

    def update_currency_names():
        currency_names = list(currency_data['Valute'].keys())
        currency_names.append('RUB')
        currency_combobox_1['values'] = currency_names
        currency_combobox_2['values'] = currency_names

    window = tk.Tk()
    window.title("Currency Converter")

    currency_combobox_1 = ttk.Combobox(window, values=[])
    currency_combobox_1.grid(row=0, column=0, padx=10, pady=10)

    amount_entry = ttk.Entry(window)
    amount_entry.grid(row=0, column=1, padx=10, pady=10)

    currency_combobox_2 = ttk.Combobox(window, values=[])
    currency_combobox_2.grid(row=0, column=2, padx=10, pady=10)

    convert_button = ttk.Button(window, text="Convert", command=convert)
    convert_button.grid(row=0, column=3, padx=10, pady=10)

    refresh_button = ttk.Button(window, text="Refresh", command=refresh)
    refresh_button.grid(row=0, column=4, padx=10, pady=10)

    result_label = ttk.Label(window, text="")
    result_label.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

    update_currency_names()

    window.mainloop()


def update_data():
    currency_data, metall_data = get_currency_data()

    date_time = currency_data['Date']
    date = date_time.split("T")[0]
    time = date_time.split("T")[1].replace('"', "")
    date = date.replace('"', "")
    date = date.split("-")

    print()
    print("Время последнего обновления данных: " + date[0] + "." + date[2] + "." + date[1] + ", " + time)         #время последнего обновления данных сервера в формате гг.мм.дд + чп
    print()

    gold_price_USD = str(metall_data[0].values())
    silver_price_USD = str(metall_data[1].values())
    platinum_price_USD = str(metall_data[2].values())
    palladium_price_USD = str(metall_data[3].values())

    print("Цена золота составляет " + str(take_price(gold_price_USD)) + " долларов за унцию")
    print("Цена серебра составляет " + str(take_price(silver_price_USD)) + " долларов за унцию")                  #вывод стоимости металлов
    print("Цена платины составляет " + str(take_price(platinum_price_USD)) + " долларов за унцию")
    print("Цена палладия составляет " + str(take_price(palladium_price_USD)) + " долларов за унцию")
    print()

    print_all_currencies(currency_data)
    return currency_data


def main():
    currency_data, metall_data = get_currency_data()


    while True:                                                               #меню
        print("[1] - Вывести курсы металлов и валют")
        print("[2] - Конвертатор валют")
        print("[0] - Выход")
        print("Введите команду")
        command = int(input())
        if command == 1:
            currency_data = update_data()
            print("Нажмите Enter чтобы продолжить")
            input()
        elif command == 2:
            currency_converter(currency_data)
        elif command == 0:
            break
        else:
            print("Неверная команда. Попробуйте снова.")

    print("Программа завершена.")


if __name__ == "__main__":
    main()
