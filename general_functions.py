import pandas
import time
from datetime import datetime
import random
import pandas as pd
import requests
import json
import asyncio
import pyppeteer
from pyppeteer import errors
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import string
from aiogram import Bot
from data import access_data
import telegram_keyboards as tkb
from data.second_categories.A import phrases  # Category A need custom choice
import re
import data.second_categories.A.phrases
import data.second_categories.B.phrases
import data.second_categories.C.phrases


API_TOKEN = access_data.API_TOKEN
bot = Bot(token=API_TOKEN)
my_id = access_data.my_id  # тільки адмін може використовувати бота
change_ip_link = access_data.change_ip_link

# Користувацький вибір у боті
userbot_choice = None
# Авторизація в Google Sheets
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(r'data/credentials.json', scope)
client = gspread.authorize(creds)
# Діставання порту
with open(r"C:\Users\username\.indigobrowser\app.properties", 'r') as prop:
    for line in prop:
        if line.startswith("multiloginapp.port="):
            port = line.split("=")[1]
            break
# Змінні
alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяґєії'


def atimer(func):
    async def inner(*args, **kwargs):
        print(datetime.now().strftime('%H:%M'), f"\t---{func.__name__} began---",
              file=open(r'data\log_v0.txt', 'a', encoding='utf-8'))
        print(f"\t---{func.__name__} began---")
        begin = time.time()
        returns = await func(*args, *kwargs)
        end = time.time()
        durtime = time.strftime('%H:%M:%S', time.gmtime(end - begin))
        # запис у таблицю
        df = pd.read_csv('data/timing.csv')
        date = datetime.now().strftime('%d.%m')
        prfl = ''
        for i in args:
            if str(i).startswith('BKN'):
                prfl = i
        df.loc[len(df)] = [prfl, date, func.__name__, durtime]
        df.to_csv("data/timing.csv", index=False)
        # вивід у консоль та логфайл
        print(datetime.now().strftime('%H:%M'), "\t>>>" + func.__name__, "finished for", durtime + "<<<",
              file=open(r'data\log_v0.txt', 'a', encoding='utf-8'))
        print("\t>>>" + func.__name__, "finished for", durtime + "<<<")
        return returns
    return inner


async def refresh_proxy():
    global userbot_choice
    resp = requests.get(change_ip_link)
    resp_text = resp.text.strip('\n')
    print(f'Status refresh_proxy: <{resp.status_code}> {resp_text}')
    if resp.status_code != 200:
        s = await bot.get_session()
        await bot.send_message(my_id,
                               f"Проксі не оновилась: <{resp.status_code}> {resp_text}Натисніть \"Так\", щоб всеодно продовжити.",
                               reply_markup=tkb.kb_yesorno)
        while True:
            if userbot_choice == 'y':
                userbot_choice = None
                await s.close()
                break
            elif userbot_choice == 'n':
                userbot_choice = None
                await bot.send_message(my_id, f"Роботу зупинено❕")
                await s.close()
                raise Exception("Проксі не оновилась")
            else:
                await asyncio.sleep(1)
    return resp_text


def getMyPrfls():
    url_start = f'http://127.0.0.1:{port}/api/v2/profile'
    response2 = requests.get(url_start)
    prfls_data = json.loads(response2.text)
    my_prfls = []
    for prfl in prfls_data:
        if prfl['name'].startswith("ВКN") or prfl['name'].startswith("BKN"):  # 2 BKN because of coding symbol
            my_prfls.append(prfl)
    get_num = lambda x: int(x['name'].replace("BKN", ""))
    my_prfls.sort(key=get_num)
    with open("data/myPrfls.json", 'w', encoding='utf-8') as myPrfls_json:
        json.dump(my_prfls, myPrfls_json, indent=2, ensure_ascii=False)


def get_my_sheet(worksheet_id):
    # Отримання таблиці Google Sheets
    sheet = client.open('TableName').get_worksheet_by_id(worksheet_id)
    # Отримання даних
    data = sheet.get_all_values()
    return data


def update_my_sheet(worksheet_id, data):
    # Отримання таблиці Google Sheets
    sheet = client.open('TableName').get_worksheet_by_id(worksheet_id)
    # Оновлення даних в Google Sheets
    sheet.clear()
    sheet.update(data)
    print(f'Google Sheets {worksheet_id} updated')


# Завантаження CSV-файлу з Google Sheets
def download_csv():
    # Отримання таблиці
    sheet = client.open('TableName').get_worksheet_by_id(0)  # 0 is id of main sheet
    # Отримання даних
    data = sheet.get_all_values()
    # Запис даних у CSV-файл
    with open(r'data/TableName - main.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    # створення резервної копії TableName - main copy.csv
    with open('data/TableName - main copy.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)


# Оновлення даних в Google Sheets
def update_gsheets():
    # Отримання таблиці
    sheet = client.open('TableName').get_worksheet_by_id(0)  # 0 is id of main sheet
    # Отримання даних з CSV-файлу
    with open(r'data/TableName - main.csv', 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        data = list(csvreader)
    # Оновлення даних в Google Sheets
    sheet.clear()
    sheet.update(data)


def increase_step(prflname):
    df = pandas.read_csv("data/TableName - main.csv")
    df.loc[df["id"] == prflname, 'step'] += 1
    df.to_csv("data/TableName - main.csv", index=False)
    update_gsheets()
    print("Step increased to:", df.loc[df["id"] == prflname, 'step'].values[0])


def writeInTable(prflname, columnName, data):
    df = pandas.read_csv("data/TableName - main.csv")
    df.loc[df["id"] == prflname, columnName] = data
    df.to_csv("data/TableName - main.csv", index=False)
    update_gsheets()
    print("В таблицю записано нові значення:", prflname, columnName, data)


def writeInCSV(prflname, columnName, data):
    df = pandas.read_csv("data/TableName - main.csv")
    df.loc[df["id"] == prflname, columnName] = data
    df.to_csv("data/TableName - main.csv", index=False)
    print("В CSV записано нові значення:", prflname, columnName, data)


def getFromTable(prflname, searchData):
    df = pandas.read_csv("data/TableName - main.csv")
    if str(df.loc[df["id"] == prflname, searchData].values[0]) == 'nan':
        return None
    else:
        return df.loc[df["id"] == prflname, searchData].values[0]


def writeDate(prflname):
    date = datetime.now().strftime('%d.%m')
    df = pandas.read_csv("data/TableName - main.csv")
    df.loc[df["id"] == prflname, 'date'] = str(date)
    df.to_csv("data/TableName - main.csv", index=False)
    update_gsheets()


@atimer
async def gather_data(prflname, browser):
    async def get_friends_count(prflname, browser):
        page = await browser.newPage()
        await page.goto("https://www.facebook.com/friends/list", timeout=40000)
        await page.waitForSelector(
            'span[style="-webkit-box-orient: vertical; -webkit-line-clamp: 2; display: -webkit-box;"]')
        spans = await page.JJ(
            'span[style="-webkit-box-orient: vertical; -webkit-line-clamp: 2; display: -webkit-box;"]')
        for span in spans:
            try:
                friends_count = await page.evaluate('(element) => element.textContent', span)
                friends_count = int(friends_count.split(' ')[0])
                break
            except Exception:
                pass
        writeInTable(prflname, "friends", int(friends_count))
        await page.close()

    async def get_pages_count(prflname, browser):
        page = await browser.newPage()
        await page.goto("https://www.facebook.com/pages/?category=liked&ref=bookmarks", timeout=40000)
        await page.waitForSelector(
            'span[style="-webkit-box-orient: vertical; -webkit-line-clamp: 2; display: -webkit-box;"]')
        spans = await page.JJ(
            'span[style="-webkit-box-orient: vertical; -webkit-line-clamp: 2; display: -webkit-box;"]')
        for span in spans:
            try:
                pages_count = await page.evaluate('(element) => element.textContent', span)
                pages_count = int(pages_count.split(" ")[-1].replace("(", "").replace(")", ""))
                break
            except Exception:
                pass
        writeInTable(prflname, "liked_pages", int(pages_count))  # розрахунок на те що якщо не знайшов то видати помилку
        await page.close()

    async def get_followers_count(prflname, browser):
        fp_link = getFromTable(prflname, "FP link")
        page = await browser.newPage()
        await page.goto(fp_link, timeout=40000)
        try:
            followers_count = await page.waitForSelector('a[href$="followers"]', timeout=10000)
            followers_count = await page.evaluate('(element) => element.textContent', followers_count)
            writeInTable(prflname, "followers", int(followers_count.split(" ")[1]))
        except errors.TimeoutError:
            print('probably old FP')
            await page.goto(fp_link + "/community/?ref=page_internal")
            followers_count = await page.waitForXPath('//span[contains(., "подписчик")]')
            followers_count = await page.evaluate('(element) => element.textContent', followers_count)
            for c in followers_count.split(" "):
                if c.isdigit():
                    followers_count = c
                    break
            writeInTable(prflname, "followers", int(followers_count.split(" ")[-1]))
        await page.close()

    async def get_groups_count(prflname, browser):
        page = await browser.newPage()
        await page.goto('https://www.facebook.com/groups/joins/?nav_source=tab&ordering=viewer_added', timeout=40000)
        try:
            groups_count = await page.waitForXPath('//span[contains(., "Все группы")]', timeout=10000)
            groups_count = await page.evaluate('(element) => element.textContent', groups_count)
            groups_count = int(groups_count.split("(")[-1].split(")")[0])
            writeInTable(prflname, "groups", groups_count)
        except errors.TimeoutError:
            print('get_groups_count(). Cannot get number')
        await page.close()

    # if followers, liked_pages, friends, groups в нормі, то не перевіряти кожну з них
    get_datas_from = [
        get_followers_count(prflname, browser) if getFromTable(prflname, 'followers') is None or int(
            getFromTable(prflname, 'followers')) < 20 else None,
        get_pages_count(prflname, browser) if getFromTable(prflname, 'liked_pages') is None or int(
            getFromTable(prflname, 'liked_pages')) < 35 else None,
        get_friends_count(prflname, browser) if getFromTable(prflname, 'friends') is None or int(
            getFromTable(prflname, 'friends')) < 100 else None,
        get_groups_count(prflname, browser) if getFromTable(prflname, 'groups') is None or int(
            getFromTable(prflname, 'groups')) < 12 else None]
    while None in get_datas_from:
        get_datas_from.remove(None)
    if get_datas_from:
        await asyncio.gather(*get_datas_from)


@atimer
async def add_followers_func(prflname, browser):
    async def follow_page(browser, link):
        page = await browser.newPage()
        await page.goto(link, {"waitUntil": ["domcontentloaded", "networkidle2"]})
        await page.bringToFront()
        follow_btn = await page.waitForSelector('div[aria-label="Нравится"]', timeout=10000)
        await follow_btn.click()
        await asyncio.sleep(2)
        try:
            followers_count = await page.waitForSelector('a[href$="followers"]', timeout=5000)
            followers_count = await page.evaluate('(element) => element.textContent', followers_count)
        except errors.TimeoutError:
            print('probably old FP')
            await page.goto(link + "/about/?ref=page_internal")
            await page.waitForXPath('//span[contains(., "одписан")]', timeout=10000)
            followers_count = await page.Jx('//span[contains(., "одписан")]')
            followers_count = await page.evaluate('(element) => element.textContent', followers_count[-1])
            for flc in followers_count.split(" "):
                if flc.isdigit():
                    followers_count = flc
                    break
            return int(followers_count) + 1
        await page.waitForSelector('div[aria-label="Нравится"]')
        _like = await page.JJ('div[aria-label="Нравится"]')
        for l in _like[1:3]:
            await l.click()
            await asyncio.sleep(random.uniform(0.5, 1.5))
        await page.close()
        return int(followers_count.split(" ")[1]) + 1

    df = pandas.read_csv("data/TableName - main.csv")
    follows = json.loads(open("data/need_followers.json", "r", encoding='utf-8').read())
    added = 0
    for i in range(len(df)):
        if str(df.loc[i, 'followers']) != 'nan':
            if int(float(df.loc[i, 'followers'])) < 20 and int(float(df.loc[i, 'zahid'])) >= 5:
                print(
                    f"Add follower {df.loc[i, 'id']}: F:{int(float(df.loc[i, 'followers']))} L:{df.loc[i, 'FP link']}")
                if df.loc[i, 'FP link'] not in follows:
                    follows.update({df.loc[i, 'FP link']: []})
                if prflname not in follows[df.loc[i, 'FP link']]:
                    try:
                        follower_count = await follow_page(browser, df.loc[i, 'FP link'])
                        follows[df.loc[i, 'FP link']].append(prflname)
                        open("data/need_followers.json", "w", encoding='utf-8').write(json.dumps(follows))
                        df.loc[i, 'followers'] = follower_count
                        df.to_csv("data/TableName - main.csv", index=False)
                        update_gsheets()
                        added += 1
                    except Exception as e:
                        print(e)
        if added >= 8:
            break
    return added


@atimer
async def create_bm(prflname, browser):
    writeInTable(prflname, "BM", "BM not created")
    page = await browser.newPage()
    await page.goto("https://business.facebook.com/overview", {"waitUntil": ['domcontentloaded', 'networkidle2']})
    create_btn = await page.waitForXPath('//a[contains(., "Создать аккаунт")]')
    await create_btn.click()
    input_name = await page.waitForSelector('input[placeholder="Jasper\'s Market"]')
    name = getFromTable(prflname, "name").split()[0] + "\'s Market"
    await input_name.type(name)
    input_email = await page.JJ('input')
    email = getFromTable(prflname, "email:pass").split(":")[0]
    await input_email[-1].type(email)
    await asyncio.sleep(2)
    send_btn = await page.waitForXPath('//span[contains(., "Отправить")]')
    await send_btn.click()
    # try-except for Not created BM
    try:
        done_btn = await page.waitForXPath('//span[contains(., "Готово")]', timeout=60000)
        await done_btn.click()
    except pyppeteer.errors.TimeoutError:
        return 'BM not created'
    await asyncio.sleep(1)
    writeInTable(prflname, "BM", "BM not verified")
    # Підтвердження почти
    mail_url = 'https://' + email.split('@')[-1]
    await page.goto(mail_url, {"waitUntil": ['domcontentloaded', 'networkidle2']})
    await asyncio.sleep(2)
    msg = await page.Jx('//span[contains(., "Confirm your business email")]')
    while msg == []:
        await page.reload()
        await asyncio.sleep(4)
        msg = await page.Jx(
            '//span[contains(., "Confirm your business email") or contains(., "Подтвердите рабочий электронный адрес") or contains(., "Підтвердьте робочу електронну адресу")]')
    await msg[0].click()
    verify_btn = await page.waitForSelector('a[href*="facebook.com/verify/email/checkpoint/"]')
    veify_url = await page.evaluate('(element) => element.href', verify_btn)
    await page.goto(veify_url, {"waitUntil": ['domcontentloaded', 'networkidle2']})
    writeInTable(prflname, "BM", "BM")
    status = await create_rk(prflname, page)
    return status


@atimer
async def create_rk(prflname, page):
    raise Exception('Створіть РК')
    # Створення рекламного аккаунта
    adacc_btn = await page.waitForXPath('//div[text()="Рекламные аккаунты"]')
    await adacc_btn.click()
    await asyncio.sleep(3)
    # try-except for RD
    try:
        add_btn = await page.waitForXPath('//div[text()="Добавить"]', timeout=10000)
        await add_btn.click()
    except pyppeteer.errors.TimeoutError:
        return 'RD'
    await asyncio.sleep(2)
    cr_btn = await page.waitForXPath('//div[text()="Создание рекламного аккаунта"]')
    await cr_btn.click()
    await page.waitForXPath('//span[text()="Название рекламного аккаунта"]')
    await asyncio.sleep(1)
    input_name_rk = await page.JJ('input[type="text"]')
    await input_name_rk[-1].type(str(random.randint(100000, 999999)))

    next_btn = await page.waitForXPath('//div[text()="Далее"]')
    await next_btn.click()
    await asyncio.sleep(2)
    mc_radio = await page.waitForXPath('//span[contains(., "Моя компания")]')
    await mc_radio.click()
    cr2_btn = await page.waitForXPath('//div[text()="Создать"]')
    await cr2_btn.click()
    try:
        my_name_radio = await page.waitForXPath('//div[@aria-checked="false"] [@role="checkbox"]', timeout=20000)
        await asyncio.sleep(1)
        await my_name_radio.click()
        await page.waitForSelector('input[role="switch"]')
        switches = await page.JJ('input[role="switch"]')
        await switches[-1].click()
        await asyncio.sleep(1)
        my_name_radio = await page.waitForXPath('//div[text()="Назначить"]')
        await my_name_radio.click()
        await page.waitForXPath('//div[text()="Аккаунт создан!"]')
        writeInTable(prflname, "BM", "1BM_rk")
        await asyncio.sleep(1)
        await page.close()
    except errors.TimeoutError:
        await page.reload()
        add_people = await page.waitForXPath('//div[text()="Добавить людей"]')
        await add_people.click()
        my_name_radio = await page.waitForXPath('//div[@aria-checked="false"] [@role="checkbox"]', timeout=45000)
        await asyncio.sleep(1)
        await my_name_radio.click()
        await page.waitForSelector('input[role="switch"]')
        switches = await page.JJ('input[role="switch"]')
        await switches[-1].click()
        await asyncio.sleep(1)
        my_name_radio = await page.waitForXPath('//div[text()="Назначить"]')
        await my_name_radio.click()
        await page.waitForXPath('//span[text()="Люди добавлены"]', visible=True)
        writeInTable(prflname, "BM", "1BM_rk")
        await asyncio.sleep(1)
        await page.close()
    return None


@atimer
async def create_bm2(prflname, browser):  # Create BM by developers.facebook.com
    page = await browser.newPage()
    await page.goto("https://developers.facebook.com/async/registration/",
                    {"waitUntil": ['domcontentloaded', 'networkidle2']})
    _b = await page.waitForXPath('//div[text()="Продолжить"]')
    await _b.click()
    # input('Confirm number manually. Press Enter to continue...')
    _b = await page.waitForXPath('//div[text()="Подтвердить электронный адрес"]')
    await _b.click()
    await asyncio.sleep(1)
    _b = await page.waitForXPath('//div[text()="Разработчик"]')
    await _b.click()
    await asyncio.sleep(1)
    _b = await page.waitForXPath('//div[text()="Завершить регистрацию"]')
    await _b.click()
    await page.waitForNavigation()
    _b = await page.waitForXPath('//div[text()="Создать приложение"]')
    await _b.click()
    await asyncio.sleep(1)
    _b = await page.waitForXPath('//div[text()="Другое"]')
    await _b.click()
    await asyncio.sleep(1)
    _b = await page.waitForXPath('//div[text()="Далее"]')
    await _b.click()
    await asyncio.sleep(1)
    await page.waitForXPath('//input[@type="text"]')
    _i = await page.Jx('//input[@type="text"]')
    await _i[-2].type("My app")
    await asyncio.sleep(1)
    await page.waitForXPath('//div[text()="Создание приложения"]')
    _b = await page.Jx('//div[text()="Создание приложения"]')
    await _b[-1].click()
    await asyncio.sleep(1)
    _i = await page.waitForXPath('//input[@type="password"]')
    password = getFromTable(prflname, "fb pass")
    await _i.type(password)
    _b = await page.waitForXPath('//button[text()="Отправить"]')
    await _b.click()
    await page.waitForNavigation()
    await asyncio.sleep(1)
    # Створення бізнес-менеджера
    _b = await page.waitForXPath('//div[text()="Настройки"]')
    await _b.click()
    await asyncio.sleep(1)
    _b = await page.waitForXPath('//div[text()="Основное"]')
    await _b.click()
    await asyncio.sleep(1)
    _b = await page.waitForXPath('//div[text()="Начать подтверждение"]')
    await _b.click()
    await asyncio.sleep(1)
    _b = await page.waitForXPath('//div[text()="Создать аккаунт"]')
    await _b.click()
    await asyncio.sleep(1)
    await page.waitForXPath('//span[text()="Название компании"]')
    _i = await page.Jx('//input[@type="text"]')
    name = getFromTable(prflname, "name")
    await _i[-3].type(name.split()[0] + "\'s Market")
    await asyncio.sleep(1)
    await _i[-2].type(name)
    await asyncio.sleep(1)
    email = getFromTable(prflname, "email:pass").split(":")[0]
    await _i[-1].type(email)
    await asyncio.sleep(1)
    _b = await page.waitForXPath('//div[text()="Создать аккаунт"]')
    await _b.click()
    await page.waitForXPath('//div[text()="Подтвердить позже"]', timeout=60000)
    writeInTable(prflname, "BM", "BM not verified")
    # Підтвердження почти
    mail_url = 'https://' + email.split('@')[-1]
    await page.goto(mail_url, {"waitUntil": ['domcontentloaded', 'networkidle2']})
    await asyncio.sleep(2)
    msg = await page.Jx(
        '//span[contains(., "Confirm your business email") or contains(., "Подтвердите рабочий электронный адрес")]')
    tryies = 0
    while msg == []:
        await page.reload()
        await asyncio.sleep(4)
        msg = await page.Jx(
            '//span[contains(., "Confirm your business email") or contains(., "Подтвердите рабочий электронный адрес")]')
        tryies += 1
        if tryies > 10:
            raise Exception("Can't find message with confirmation link. Please, check it manually.")
    await msg[0].click()
    verify_btn = await page.waitForSelector('a[href^="https://www.facebook.com/verify/email/checkpoint/"]')
    veify_url = await page.evaluate('(element) => element.href', verify_btn)
    await page.goto(veify_url, {"waitUntil": ['domcontentloaded', 'networkidle2']})
    writeInTable(prflname, "BM", "BM")
    # Створення рекламного аккаунта
    await asyncio.sleep(3)
    adacc_btn = await page.waitForXPath('//div[text()="Рекламные аккаунты"]')
    await adacc_btn.click()
    await asyncio.sleep(3)
    add_btn = await page.waitForXPath('//div[text()="Добавить"]')
    await add_btn.click()
    await asyncio.sleep(2)
    cr_btn = await page.waitForXPath('//div[text()="Создание рекламного аккаунта"]')
    await cr_btn.click()
    await page.waitForXPath('//span[text()="Название рекламного аккаунта"]')
    await asyncio.sleep(1)
    input_name_rk = await page.JJ('input[type="text"]')
    await input_name_rk[-1].type(str(random.randint(100000, 999999)))
    next_btn = await page.waitForXPath('//div[text()="Далее"]')
    await next_btn.click()
    await asyncio.sleep(2)
    mc_radio = await page.waitForXPath('//span[contains(., "Моя компания")]')
    await mc_radio.click()
    cr2_btn = await page.waitForXPath('//div[text()="Создать"]')
    await cr2_btn.click()
    try:
        my_name_radio = await page.waitForXPath('//div[@aria-checked="false"] [@role="checkbox"]', timeout=20000)
        await asyncio.sleep(1)
        await my_name_radio.click()
        await page.waitForSelector('input[role="switch"]')
        switches = await page.JJ('input[role="switch"]')
        await switches[-1].click()
        await asyncio.sleep(1)
        my_name_radio = await page.waitForXPath('//div[text()="Назначить"]')
        await my_name_radio.click()
        await page.waitForXPath('//div[text()="Аккаунт создан!"]')
        writeInTable(prflname, "BM", "1BM_rk")
        await asyncio.sleep(1)
        await page.close()
    except errors.TimeoutError:
        await page.reload()
        add_people = await page.waitForXPath('//div[text()="Добавить людей"]')
        await add_people.click()
        my_name_radio = await page.waitForXPath('//div[@aria-checked="false"] [@role="checkbox"]', timeout=45000)
        await asyncio.sleep(1)
        await my_name_radio.click()
        await page.waitForSelector('input[role="switch"]')
        switches = await page.JJ('input[role="switch"]')
        await switches[-1].click()
        await asyncio.sleep(1)
        my_name_radio = await page.waitForXPath('//div[text()="Назначить"]')
        await my_name_radio.click()
        await page.waitForXPath('//span[text()="Люди добавлены"]', visible=True)
        writeInTable(prflname, "BM", "1BM_rk")
        await asyncio.sleep(1)
        await page.close()


@atimer
async def create_bm3(prflname, browser):
    writeInTable(prflname, "BM", "BM not created")
    page = await browser.newPage()
    await page.goto("https://business.facebook.com/latest/home", {"waitUntil": ['domcontentloaded', 'networkidle2']})
    await asyncio.sleep(2)
    for i in range(2):
        await page.keyboard.press('Escape')
    await asyncio.sleep(2)
    menu_btn = await page.waitForSelector('div[data-pagelet="BizKitPresenceSelector"]')
    await menu_btn.click()
    try:
        create_btn = await page.waitForXPath('//div[contains(text(), "Создать бизнес-аккаунт")]')
        await create_btn.click()
    except errors.TimeoutError:
        await page.close()
        return 'Error Создать бизнес-аккаунт'
    await asyncio.sleep(3)
    name, surname = getFromTable(prflname, "name").split()
    email = getFromTable(prflname, "email:pass").split(":")[0]
    inputs = await page.JJ('input')
    await inputs[-1].type(email)
    await inputs[-2].type(surname)
    await inputs[-3].type(name)
    await inputs[-4].type(name + "\'s Market")
    await asyncio.sleep(2)
    send_btn = await page.Jx('//div[contains(text(), "Создать")]')
    await send_btn[-1].click()
    try:  # try-except for Not created BM
        # for i in range(2): # Не завжди потрібно двічі натискати "Пропустить"
        skip_btn = await page.waitForXPath('//div[contains(text(), "Пропустить")]', timeout=50000)
        await skip_btn.click()
        await asyncio.sleep(2)
        # той момент коли потрібно додати 2го адміністратора
        # done_btn = await page.waitForXPath('//div[contains(text(), "Подтвердить")]', timeout=10000)  # можливо не працює
        # await done_btn.click()
        # await asyncio.sleep(2)
    except pyppeteer.errors.TimeoutError:
        print("\"Підтвердити\" помилка!!")
        return 'BM not created'
    await asyncio.sleep(1)
    writeInTable(prflname, "BM", "BM not verified")
    # Підтвердження почти
    mail_url = 'https://' + email.split('@')[-1]
    await page.goto(mail_url, {"waitUntil": ['domcontentloaded', 'networkidle2']})
    await asyncio.sleep(2)
    msg = await page.Jx('//span[contains(., "Confirm your business email")]')
    while msg == []:
        await page.reload()
        await asyncio.sleep(4)
        msg = await page.Jx(
            '//span[contains(., "Confirm your business email") or contains(., "Подтвердите рабочий электронный адрес") or contains(., "Підтвердьте робочу електронну адресу")]')
    await msg[0].click()
    verify_btn = await page.waitForSelector('a[href^="https://www.facebook.com/verify/email/checkpoint/"]')
    veify_url = await page.evaluate('(element) => element.href', verify_btn)
    await page.goto(veify_url, {"waitUntil": ['domcontentloaded', 'networkidle2']})
    writeInTable(prflname, "BM", "BM")
    status = await create_rk(prflname, page)
    return status


def password_generator():
    password = ''
    for i in range(8):
        password += random.choice(string.ascii_letters + string.digits)
    return password


@atimer
async def check_accountquality2(prflname, browser):
    global userbot_choice
    page = await browser.newPage()
    await page.goto('https://business.facebook.com/accountquality/?landing_page=accounts')
    page2 = await browser.newPage()
    await page2.goto('https://mds.gold/')
    await page.bringToFront()
    BM = getFromTable(prflname, 'BM')
    BM_status = getFromTable(prflname, 'BM_status')
    RD = getFromTable(prflname, 'RD')
    prev_record = f"Записано: <{BM}|{BM_status}|{RD}>".replace("_", " ")
    s = await bot.get_session()
    # if pagest is True:
    await bot.send_message(my_id, f'{prflname} trigger rd or create bm?\n{prev_record}', reply_markup=tkb.kb_bm_trigger)
    while True:
        if userbot_choice is not None:
            if userbot_choice == 'trigger':
                await trigger_rd(prflname, browser)
                await page.reload()
            elif userbot_choice == 'create':
                await create_bm4(prflname, browser)
                await page.reload()
            userbot_choice = None
            break
        else:
            await asyncio.sleep(1)
    await bot.send_message(my_id, f'\"{prflname}\" з обмеженнями? \n{prev_record}', reply_markup=tkb.kb_check_rd2)
    while True:
        if userbot_choice is not None:
            download_csv()
            if userbot_choice == 'Skip':
                writeInTable(prflname, "checkRD_day", datetime.now().strftime('%d.%m.%y'))
                userbot_choice = None
                await page.close()
            elif userbot_choice == 'Permanent RD':
                writeInCSV(prflname, "checkRD_day", datetime.now().strftime('%d.%m.%y'))
                writeInCSV(prflname, "date", 'dead')
                writeInTable(prflname, "RD", userbot_choice)
                userbot_choice = None
                await page.close()
            else:
                writeInCSV(prflname, "checkRD_day", datetime.now().strftime('%d.%m.%y'))
                writeInCSV(prflname, "BM", userbot_choice.split(" ")[0])
                writeInCSV(prflname, "BM_status", userbot_choice.split(" ")[1])
                writeInTable(prflname, "RD", userbot_choice.split(" ")[2])
                userbot_choice = None
                await page.close()
            break
        else:
            await asyncio.sleep(1)
    await s.close()


@atimer
async def trigger_rd(prflname, browser):
    email = getFromTable(prflname, "email:pass").split(":")[0]
    first_name, last_name = getFromTable(prflname, "name").split()
    with open("data/create_bm_script.txt", "r", encoding="utf-8") as file:
        scripttxt = file.read()
    scripttxt = scripttxt.replace("MDSFIRST", first_name)
    scripttxt = scripttxt.replace("MDSLAST", last_name)
    scripttxt = scripttxt.replace("MDSGOLD", email)
    print('\n', scripttxt, '\n')
    page2 = await browser.newPage()
    await page2.goto('https://business.facebook.com/accountquality/?landing_page=accounts')
    page3 = await browser.newPage()
    await page3.goto("https://business.facebook.com/overview", {"waitUntil": ['domcontentloaded', 'networkidle2']})
    try:
        rd_label = await page2.waitForXPath('//span[text()="Аккаунт с ограничениями"]', timeout=3000)
    except errors.TimeoutError:
        rd_label = False
    q_requests = 0
    while not rd_label and q_requests < 14:
        await page3.evaluate(scripttxt, force_expr=True)
        q_requests += 1
        print("Console request", q_requests)
        await page2.bringToFront()
        await page2.reload()
        try:
            rd_label = await page2.waitForXPath('//span[text()="Аккаунт с ограничениями"]', timeout=3000)
        except errors.TimeoutError:
            rd_label = False
    await page2.close()
    await page3.close()


@atimer
async def create_bm4(prflname, browser):
    email = getFromTable(prflname, "email:pass").split(":")[0]
    first_name, last_name = getFromTable(prflname, "name").split()
    with open("data/create_bm_script.txt", "r", encoding="utf-8") as file:
        scripttxt = file.read()
    scripttxt = scripttxt.replace("MDSFIRST", first_name)
    scripttxt = scripttxt.replace("MDSLAST", last_name)
    scripttxt = scripttxt.replace("MDSGOLD", email)
    page3 = await browser.newPage()
    await page3.goto("https://business.facebook.com/overview", {"waitUntil": ['domcontentloaded', 'networkidle2']})
    await page3.evaluate(scripttxt, force_expr=True)
    await asyncio.sleep(5)
    await page3.close()
    print("BM створено.")
    await bot.send_message(my_id, f"BM створено.")


@atimer
async def trigger_rd_fbaccio(prflname, browser):
    # prflname заготовка для даних з таблиці для запису імені і почти БМ
    page = await browser.newPage()
    ads_link = "https://www.facebook.com/adsmanager/manage/all?nav_source=comet&nav_entry_point=comet_bookmark"
    await page.goto(ads_link, {"waitUntil": ['domcontentloaded', 'networkidle2']}, timeout=60000)
    # Переходимо до кампаній
    for i in range(3):
        await page.keyboard.press("Escape")
        await asyncio.sleep(0.5)
    try:
        start_btn = await page.waitForXPath('//div[text()="Начать"]', timeout=3000)
        while start_btn:
            await start_btn.click()
            await asyncio.sleep(2)
            try:
                start_btn = await page.waitForXPath('//div[text()="Начать"]', timeout=3000)
            except errors.TimeoutError:
                start_btn = None
        skip_btn = await page.waitForXPath('//div[text()="Пропустить"]', timeout=5000)
        while skip_btn:
            await skip_btn.click()
            await asyncio.sleep(2)
            try:
                skip_btn = await page.waitForXPath('//div[text()="Пропустить"]', timeout=5000)
            except errors.TimeoutError:
                skip_btn = None
        adsman_btn = await page.waitForXPath('//div[text()="Открыть Ads Manager"]', timeout=5000)
        await adsman_btn.click()
        await page.waitForNavigation({"waitUntil": ['domcontentloaded', 'networkidle0']})
    except errors.TimeoutError:
        await page.goto(ads_link, {"waitUntil": ['domcontentloaded', 'networkidle0']}, timeout=60000)
        for i in range(3):
            await page.keyboard.press("Escape")
            await asyncio.sleep(0.5)
    await asyncio.sleep(2)
    script = open("data/fbaccio.txt", "r").read()
    await page.evaluate('''() => { %s }''' % script)
    await page.waitForSelector('a[href$="#tab5"]')
    await page.click('a[href$="#tab5"]')
    await asyncio.sleep(1)
    await page.waitForSelector('button[id="showAddBMbtn"]', timeout=3000)
    await page.click('button[id="showAddBMbtn"]')
    await asyncio.sleep(1)

    print("Ended")


def define_file_category(prflname, requested_type):
    # requsted_type вказуємо якого типу категорію повернути:
    #   "category_name" - повертає назву каталогу
    #   "phrases" - повертає дані із файлу phrases.py
    if re.match("BKN\d", prflname):
        phrases_category = data.second_categories.A.phrases
        category_name = "A"
    elif re.match("BK\d", prflname):
        phrases_category = data.second_categories.B.phrases
        category_name = "B"
    if requested_type == "category_name":
        return category_name
    elif requested_type == "phrases":
        return phrases_category
    else:
        raise Exception(f"Не існує вказаного типу: {requested_type}")


def order_my_prfls(by_col, reverse=False):
    # by_col
        # "idname" - по номеру акку
        # "zahid" - по номеру заходу
        # "step" - по статусу РД
        # "RD" - по крокам
    # download_csv()
    my_prfls = json.loads(open("data/myPrfls.json", 'r', encoding='utf-8').read())
    df = pandas.read_csv("data/TableName - main.csv")
    prfl_value = {}
    if by_col == "idname":
        my_key = lambda x: int(x['name'].replace("BKN", ""))
        my_prfls.sort(key=my_key, reverse=reverse)
    else:
        for prfl in my_prfls:
            value = df.loc[df["id"] == prfl["name"], by_col].values[0]
            prfl_value.update({prfl["name"]: str(value)})
        my_key = lambda x: prfl_value[x["name"]]
        my_prfls.sort(key=my_key, reverse=reverse)
    with open("data/myPrfls.json", 'w', encoding='utf-8') as myPrfls_json:
        json.dump(my_prfls, myPrfls_json, indent=2, ensure_ascii=False)


@atimer
async def go_rd(prflname, ws):
    browser = await pyppeteer.connect({"browserWSEndpoint": ws, "defaultViewport": None})
    await check_accountquality2(prflname, browser)
    try:
        await browser.close()
    except errors.NetworkError as e:
        print("NetworkError:", e)