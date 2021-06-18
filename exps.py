import gspread


# Подключаемся к google sheet
gc = gspread.service_account(filename='src/creds.json')
sh = gc.open('Инв')
# Выбираем вкладку
worksheet = sh.worksheet("BTC")

values = worksheet.get_all_records()

print(values)