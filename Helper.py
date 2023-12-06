import json
import pandas
from datetime import datetime, timedelta
import general_functions as gf

MAIN_SHEET_ID = 0  # 0 is id of main sheet


def analize_average_time():  # Вираховуємо середній час для кожного завершеного заходу
    global MAIN_SHEET_ID
    data = gf.get_my_sheet(MAIN_SHEET_ID)
    df = pandas.DataFrame(data[1:], columns=data[0])
    telegram_text = '\-\- _Середній час_ \-\-\n'
    total_avg = 0
    total_number = 0
    zs = set(num for num in df['zahid'])
    zs_dict = {z: [] for z in zs}
    zs_dict = dict(sorted(zs_dict.items(), key=lambda item: item[0]))
    with open('data/average_zahid_time.json', 'r') as f:
        files_dict = json.load(f)
    for z in zs_dict:
        for i in range(len(df)):
            if df['zahid'][i] == z and int(float(df['step'][i])) == 0:
                t = df['elapsed_time'][i]
                # перетворюємо t формату 00:00:00 в секунди
                try:
                    t = int(t.split(':')[0]) * 3600 + int(t.split(':')[1]) * 60 + int(t.split(':')[2])
                    zs_dict[z].append(t)
                except ValueError as e:
                    print('ValueError:', e)
        avg = 0
        if len(zs_dict[z]) > 0:
            for t in zs_dict[z]:
                avg += t
            avg = avg / len(zs_dict[z])
            zs_dict[z] = avg
            # зберігаємо у json файл середній час у секундах
            files_dict[z] = avg
    with open('data/average_zahid_time.json', 'w') as f:
        json.dump(files_dict, f, indent=2)
    for z, avg in files_dict.items():
        total_avg += avg
        total_number += 1
        # перетворюємо avg в формат 00:00:00
        min = str(int(avg // 60))
        sec = str(int(avg % 60))
        mintext = f'0{min}' if len(min) == 1 else min
        sectext = f'0{sec}' if len(sec) == 1 else sec
        telegram_text += f'*\_{z}\_*    _{mintext}:{sectext}_\n'
    total_avg = total_avg / total_number
    min = str(int(total_avg // 60))
    sec = str(int(total_avg % 60))
    mintext = f'0{min}' if len(min) == 1 else min
    sectext = f'0{sec}' if len(sec) == 1 else sec
    telegram_text += '\-' * 11 + '\n'
    telegram_text += f'*\_A\_*    _{mintext}:{sectext}_\n'
    telegram_text += '\-' * 11 + '\n'
    telegram_text += '\-\- _Загальний час_ \-\-\n'
    # знаходимо загальний час
    dates = set(d for d in df['date'])
    dates_dict = {d: 0 for d in dates}
    dates_dict.update({'Total': 0})
    for dt in dates_dict:
        if dt != 'Total':
            for i in range(len(df)):
                if df['date'][i] == dt:
                    t = df['elapsed_time'][i]
                    # перетворюємо t формату 00:00:00 в секунди
                    try:
                        t = int(t.split(':')[0]) * 3600 + int(t.split(':')[1]) * 60 + int(t.split(':')[2])
                        dates_dict[dt] += t
                        dates_dict['Total'] += t
                    except ValueError as e:
                        print('ValueError:', e)
    # сортуємо словник по значеннях
    dates_dict = dict(sorted(dates_dict.items(), key=lambda item: item[1], reverse=True))
    # переводимо сумарний час в формат 00:00:00
    for dt in dates_dict:
        hours = str(int(dates_dict[dt] // 3600))
        minutes = str(int((dates_dict[dt] % 3600) // 60))
        seconds = str(int(dates_dict[dt] % 60))
        hourtext = f'0{hours}' if len(hours) == 1 else hours
        mintext = f'0{minutes}' if len(minutes) == 1 else minutes
        sectext = f'0{seconds}' if len(seconds) == 1 else seconds
        dt = str(dt).replace('.', '\.')
        telegram_text += f'_{hourtext}:{mintext}:{sectext}_    *\_{dt}\_* \n'
    print(telegram_text)
    return telegram_text


def calculate_output():
    global MAIN_SHEET_ID
    today = datetime.today()
    weektoday = today.weekday()
    remain_days = 6 - weektoday
    last_weekday = (today + timedelta(days=remain_days)).strftime("%d.%m")
    telegram_text = f'До кінця тижня залишилось: {remain_days} днів. Останній день: {last_weekday}\n'
    unspent_accs = 0
    ready_for_delivery = 0
    complete = 0
    pzrd_complete = 0
    pzrd_not_completed = 0
    data = gf.get_my_sheet(MAIN_SHEET_ID)
    df = pandas.DataFrame(data[1:], columns=data[0])
    for i in range(len(df)):
        if df['date'][i] == 'complete':
            complete += 1
            if df['RD'][i] == 'ПЗРД':
                pzrd_complete += 1
            continue
        try:
            date = datetime.strptime(str(df['date'][i]), "%d.%m")
        except ValueError:
            date = None
        if date is not None:
            remain_zahods = (6 - int(df['zahid'][i])) * 2  # заходи ідуть 1 раз в 2 дні
            # якщо залишилось заходів менше чим днів до кінця тижня - то акк здати можна
            if remain_zahods <= remain_days:
                ready_for_delivery += 1
                if df['RD'][i] == 'ПЗРД':
                    pzrd_not_completed += 1
            unspent_accs += 1
    sum = ready_for_delivery + complete
    pzrd_total = pzrd_not_completed + pzrd_complete
    price1 = 2.5
    price2 = 3.5
    if complete >= 35:
        outcome = (complete - pzrd_complete) * price2 + pzrd_complete * (price2 + 1)
    else:
        outcome = (complete - pzrd_complete) * price1 + pzrd_complete * (price1 + 1)
    if sum >= 35:
        possible_outcome = (sum - pzrd_total) * price2 + pzrd_total * (price2 + 1)
    else:
        possible_outcome = (sum - pzrd_total) * price1 + pzrd_total * (price1 + 1)
    telegram_text += '_Результат на поточний тиждень_\n' \
                    f'*Видано: {complete} [{outcome} $]*\n' \
                    f'Не видано: {unspent_accs}\n' \
                    f'Можливо видати: {ready_for_delivery}\n' \
                    f'Можливий результат: {possible_outcome} $'
    print(telegram_text)
    return telegram_text


def prediction():  # аля Коли це закінчиться?
    global MAIN_SHEET_ID
    data = gf.get_my_sheet(MAIN_SHEET_ID)
    df = pandas.DataFrame(data[1:], columns=data[0])
    zahods = {}
    for i in range(len(df)):
        today = datetime.now().strftime('%d.%m')
        last_day = str(df['date'][i])
        d1 = datetime.strptime(today, "%d.%m")
        try:
            d2 = datetime.strptime(last_day, "%d.%m")
        except ValueError:
            # print(f'Format of date is not correct. Skip.')
            continue
        difference = (d1 - d2).days
        if difference >= 2 and int(df['step'][i]) > 0:
            z = df['zahid'][i]
            if z not in zahods:
                zahods.update({z: 1})
            else:
                zahods[z] += 1
        elif difference >= 2:
            z = str(int(df['zahid'][i]) + 1)
            if z not in zahods:
                zahods.update({z: 1})
            else:
                zahods[z] += 1
    with open(r'data/average_zahid_time.json', 'r') as f:  # зчитуємо файл з середнім часом роботи заходів
        zs_avgtime_dict = json.load(f)
    end_time = datetime.now()
    telegram_text = 'Потрібно виконати:\n'
    for zahid in zahods:
        if zahid not in zs_avgtime_dict:
            continue
        q = zahods[zahid]
        zahods[zahid] *= zs_avgtime_dict[zahid]
        end_time += timedelta(seconds=zahods[zahid])
        if q == 1:
            raz_word = 'раз'
        elif q in [2, 3, 4]:
            raz_word = 'рази'
        else:
            raz_word = 'разів'
        telegram_text += f'  {q} {raz_word} {zahid}й захід \[{end_time.strftime("%H:%M")}];\n'
    if end_time.day == datetime.now().day:
        day_word = 'сьогодні'
    elif end_time.day == datetime.now().day + 1:
        day_word = 'завтра'
    else:
        day_word = end_time.strftime("%d/%m")
    telegram_text += f'Приблизне закінчення: *{day_word} о {end_time.strftime("%H:%M")}*.'
    print(telegram_text)
    return telegram_text
