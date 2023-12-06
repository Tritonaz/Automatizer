import random
import os
import pyppeteer
import general_functions as gf
import asyncio
import zahid1
from login_sites_origin import multilogin_sites
from pyppeteer import errors
from tqdm import tqdm


@gf.atimer
async def add_friends(prflname, browser, quantity):
    category_name = gf.define_file_category(prflname, "category_name")
    if quantity > 60:
        quantity = 60
    human_names = open(f"data/second_categories/{category_name}/human_names.txt", "r").read().split(" ")
    page = await browser.newPage()
    link = f"https://www.facebook.com/search/people/?q={random.choice(human_names)}"
    await page.goto(link, {"waitUntil": ['domcontentloaded', 'networkidle2']})
    await page.bringToFront()
    scsfl_added = 0
    failure_added = 0
    pbar = tqdm(total=quantity, desc="Adding friends", unit="friend", ncols=100, colour='white')
    while scsfl_added <= quantity:
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(4)
        try:
            await page.waitForSelector('div[aria-label="Добавить в друзья"]', timeout=5000)
        except TimeoutError:
            print("Not find \"Добавить в друзья\"")
        add_friends_btns = await page.JJ('div[aria-label="Добавить в друзья"]')
        rr = random.randint(3, 4)
        if len(add_friends_btns) > rr:
            random.shuffle(add_friends_btns)
            add_friends_btns = random.sample(add_friends_btns, rr)
        for btn in add_friends_btns:
            try:
                await btn.click()
                try:
                    await page.waitForXPath('//span[text()="Невозможно отправить запрос"]',
                                            timeout=random.randrange(1800, 2101, 100))
                    await page.keyboard.press('Escape')
                    failure_added += 1
                except errors.TimeoutError:
                    scsfl_added += 1
                    pass
            except Exception as exc:
                print("btn.click()", exc)
                break
        if failure_added > 25:
            break
        await page.waitForSelector('input[aria-label="Поиск на Facebook"]', timeout=10000)
        search_input = await page.J('input[aria-label="Поиск на Facebook"]')
        await search_input.focus()
        await page.keyboard.type(f'{random.choice(human_names)}\n')
        pbar.update(n=scsfl_added - pbar.n)
    pbar.close()
    await page.close()


@gf.atimer
async def fbacc(prflname, browser):
    page = await browser.newPage()
    ads_link = "https://www.facebook.com/adsmanager/manage/all?nav_source=comet&nav_entry_point=comet_bookmark"
    await page.goto(ads_link, {"waitUntil": ['domcontentloaded', 'networkidle2']}, timeout=60000)
    # Приймаємо умови
    try:
        accept_btn = await page.waitForXPath('//div[text()="Принимаю"]', timeout=5000)
    except errors.TimeoutError:
        accept_btn = None
    max_clicks = 3
    while accept_btn is not None:
        await accept_btn.click()
        max_clicks -= 1
        if max_clicks == 0:
            await page.keyboard.press("Escape")
        try:
            accept_btn = await page.waitForXPath('//div[text()="Принимаю"]', timeout=3000)
        except errors.TimeoutError:
            print("No \"Принимаю\" button.")
            accept_btn = None
    try:
        start_btn = await page.waitForXPath('//div[text()="Начать"]', timeout=3000)
        while start_btn:
            await start_btn.click()
            try:
                start_btn = await page.waitForXPath('//div[text()="Начать"]', timeout=2000)
            except errors.TimeoutError:
                start_btn = None
        skip_btn = await page.waitForXPath('//div[text()="Пропустить"]', timeout=3000)
        while skip_btn:
            await skip_btn.click()
            try:
                skip_btn = await page.waitForXPath('//div[text()="Пропустить"]', timeout=5000)
            except errors.TimeoutError:
                skip_btn = None
        adsman_btn = await page.waitForXPath('//div[text()="Открыть Ads Manager"]', timeout=5000)
        await adsman_btn.click()
        await page.waitForNavigation({"waitUntil": ['domcontentloaded', 'networkidle0']})
    except errors.TimeoutError:
        await page.goto(ads_link, {"waitUntil": ['domcontentloaded', 'networkidle0']}, timeout=60000)

    script = open("data/fbaccio.txt", "r").read()
    await page.evaluate('''() => { %s }''' % script)
    await page.waitForSelector('a[href$="#tab4"]')
    await page.click('a[href$="#tab4"]')
    await asyncio.sleep(1)
    await page.waitForSelector('button[id="showAddFPbtn"]', timeout=3000)
    await page.click('button[id="showAddFPbtn"]')
    await page.waitForSelector('input[id="Tab4AddFPname"]')

    category_name = gf.define_file_category(prflname, "category_name")
    adj = random.choice(list(open(f'data/second_categories/{category_name}/adjectives.txt', 'r').read().splitlines()))
    noun = random.choice(list(open(f'data/second_categories/{category_name}/nouns.txt', 'r').read().splitlines()))
    await page.type('input[id="Tab4AddFPname"]', f'{adj} {noun}')
    await page.click('button[id="Tab4AddFPForm"]')
    try:
        await page.waitForXPath('//a[text()="Open"]', timeout=60000)
        open_btn = await page.Jx('//a[text()="Open"]')
        url_fp = await (await open_btn[0].getProperty('href')).jsonValue()
        if url_fp == 'https://www.facebook.com/0':
            raise errors.TimeoutError
        gf.writeInTable(prflname, "FP link", url_fp)
        await page.close()
    except errors.TimeoutError:
        print("Error create Page :( ")
        await page.goto(ads_link, {"waitUntil": ['domcontentloaded', 'networkidle2']})
        await asyncio.sleep(5)
        script = open("data/fbaccio.txt", "r").read()
        await page.evaluate('''() => { %s }''' % script)
        await page.waitForSelector('a[href$="#tab4"]')
        await page.click('a[href$="#tab4"]')
        await asyncio.sleep(1)
        await page.waitForSelector('button[id="showAddFPbtn"]')
        await page.click('button[id="showAddFPbtn"]')
        await page.waitForSelector('input[id="Tab4AddFPname"]')
        category_name = gf.define_file_category(prflname, "category_name")
        adj = random.choice(list(open(f'data/second_categories/{category_name}/adjectives.txt', 'r').read().splitlines()))
        noun = random.choice(list(open(f'data/second_categories/{category_name}/nouns.txt', 'r').read().splitlines()))
        await page.type('input[id="Tab4AddFPname"]', f'{adj} {noun}')
        await page.waitForSelector('select[id="Tab4AddFPstyle"]')
        await page.focus('select[id="Tab4AddFPstyle"]')
        await page.keyboard.press('o')
        await page.click('button[id="Tab4AddFPForm"]')
        await page.waitForXPath('//a[text()="Open"]')
        open_btn = await page.Jx('//a[text()="Open"]')
        url_fp = await (await open_btn[0].getProperty('href')).jsonValue()
        gf.writeInTable(prflname, "FP link", url_fp)
        await page.close()


@gf.atimer
async def fill_oldfp(prflname, page):
    category_name = gf.define_file_category(prflname, "category_name")
    try:
        await page.waitForXPath('//span[text()="Подключите Страницу Facebook к WhatsApp"]')
        await page.keyboard.press("Escape")
        exit_btn = await page.waitForXPath('//div[@aria-label="Выйти"]')
        await exit_btn.click()
        await asyncio.sleep(3)
    except errors.TimeoutError:
        print("Not found \"Подключите Страницу Facebook к WhatsApp\"")
    # Оновлюємо аватарку
    _b = await page.waitForXPath('//div[@aria-label="Обновить фото профиля"]')
    await _b.click()
    await asyncio.sleep(1)
    _b = await page.waitForXPath('//span[text()="Редактировать фото профиля"]')
    await _b.click()
    await page.waitForSelector('div[aria-label="Загрузить фото"]')
    path = rf"data\second_categories\{category_name}\fp_images\avatars"
    avatars = os.listdir(path)
    ch_avatar = f"{path}\\{random.choice(avatars)}"
    input_file = await page.Jx('//input[@accept="image/*,image/heif,image/heic"]')
    await input_file[-1].uploadFile(ch_avatar)
    await page.waitForSelector('div[aria-label="Сохранить"]')
    await page.click('div[aria-label="Сохранить"]')
    window = await page.J('div[aria-label="Сохранить"]')
    while window is not None:
        await asyncio.sleep(1)
        window = await page.J('div[aria-label="Сохранить"]')
    # Оновлюємо обложку
    path = rf"data\second_categories\{category_name}\fp_images\background"
    oblozhka = os.listdir(path)
    ch_oblozhka = f"{path}\\{random.choice(oblozhka)}"
    input_file = await page.waitForXPath('//input[@accept="image/*,image/heif,image/heic"]')
    await input_file.uploadFile(ch_oblozhka)
    await page.evaluate('window.scrollBy(0, -1000)')
    save_btn = await page.waitForXPath('//div[@aria-label="Сохранить изменения"]', timeout=60000)
    cancel_btn = await page.waitForXPath('//div[@aria-label="Отмена"]')
    await cancel_btn.focus()
    await save_btn.press('Tab')
    await asyncio.sleep(2)
    await page.keyboard.press('Enter')
    # Додаємо кнопку "Підписатися"
    _b = await page.waitForXPath('//div[@aria-label="Добавить кнопку" or @aria-label="Добавить кнопку действия"]')
    await _b.click()
    _b = await page.waitForXPath('//span[text()="Подписаться"]')
    await _b.click()
    # Додаємо біографію
    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
    _b = await page.waitForXPath('//div[text()="Редактировать описание"]')
    await _b.click()
    await page.waitForXPath('//span[text()="Редактирование информации о Странице"]')
    await asyncio.sleep(1)
    textarea = await page.waitForXPath('//label[@aria-label="Описание"]')
    citati_list = []
    with open(f"data/second_categories/{category_name}/quotes_fp.txt", "r", encoding='utf-8') as citati_txt:
        for line in citati_txt.read().splitlines():
            if line != '':
                citati_list.append(line)
    await textarea.type(random.choice(citati_list))
    await asyncio.sleep(1)
    close_btn = await page.waitForXPath('//div[@aria-label="Закрыть"]')
    while close_btn:
        await close_btn.click()
        await asyncio.sleep(2)
        close_btn = await page.J('div[aria-label="Закрыть"]')
    await asyncio.sleep(2)
    # Робимо пости на сторінці
    for i in range(2):
        await post_oldfp(prflname, page)
    await page.close()
    return 'OldFP'


@gf.atimer
async def post_oldfp(prflname, page):
    category_name = gf.define_file_category(prflname, "category_name")
    await page.evaluate('window.scrollTo(0, 0)')
    await asyncio.sleep(2)
    _b = await page.waitForXPath('//span[contains(., "Фото/видео")]')
    await _b.click()
    input_file = await page.waitForXPath(
        '//input[@accept="image/*,image/heif,image/heic,video/*,video/mp4,video/x-m4v,video/x-matroska,.mkv"]')
    articles = os.listdir(rf"data/second_categories/{category_name}/articles/texts")
    ch_article = random.choice(articles)
    animal_name = ch_article.split(" ")[0]
    photos = os.listdir(rf"data/second_categories/{category_name}/articles/images")
    photos2 = []
    for p in photos:
        if animal_name == p.split(" ")[0]:
            photos2.append(p)
    photo_path = os.getcwd() + rf"\data\second_categories\{category_name}\articles\images\{random.choice(photos2)}"
    with open(rf"data/second_categories/{category_name}/articles/texts/{ch_article}", "r") as article_file:
        text = article_file.read()
    await input_file.uploadFile(photo_path)
    textarea = await page.waitForSelector('div[aria-label^="Напишите что-нибудь"]')
    await textarea.type(text)
    await asyncio.sleep(8)
    await page.waitForXPath('//span[text()="Опубликовать"]')
    publication_btn = await page.Jx('//span[text()="Опубликовать"]')
    await publication_btn[-1].click()
    time_out = 0
    while publication_btn:
        await asyncio.sleep(5)
        try:
            publication_btn = await page.Jx('//span[text()="Опубликовать"]')
            await publication_btn[-1].click()
        except (IndexError, errors.ElementHandleError):
            print("Очікування публікації закінчилось")
        time_out += 1
        if time_out > 6:
            raise Exception("Публікація не закінчилася за 30 секунд")
    return 'OldFP'


@gf.atimer
async def fill_fp(prflname, browser):
    category_name = gf.define_file_category(prflname, "category_name")
    page = await browser.newPage()
    fp_url = gf.getFromTable(prflname, "FP link")
    await page.goto(fp_url, {"waitUntil": ['domcontentloaded', 'networkidle2']})
    # Переключаємося на режим роботи з FanPage
    try:
        await page.waitForXPath('//span[text()="Переключить"]')
        switch_btn = await page.Jx('//span[text()="Переключить"]')
        await switch_btn[0].click()
        await page.waitForNavigation({"waitUntil": ['domcontentloaded', 'networkidle0']})
        gf.writeInTable(prflname, "FP link", page.url)  # Записуємо актуальну адресу FanPage
    except errors.TimeoutError:
        print("It's probably OldPage")
        gf.writeInTable(prflname, 'fp_type', 'OLD')
        return await fill_oldfp(prflname, page)
    try:
        _b = await page.waitForXPath('//span[contains(., "Не сейчас")]', timeout=5000)
        await _b.click()
        await asyncio.sleep(2)
    except errors.TimeoutError:
        pass
    # Оновлюємо аватарку
    await page.waitForSelector('div[aria-label="Обновить фото профиля"]')
    await page.click('div[aria-label="Обновить фото профиля"]')
    await page.waitForSelector('div[aria-label="Загрузить фото"]')
    await asyncio.sleep(1)
    path = rf"data\second_categories\{category_name}\fp_images\avatars"
    avatars = os.listdir(path)
    ch_avatar = f"{path}\\{random.choice(avatars)}"
    input_file = await page.Jx('//input[@accept="image/*,image/heif,image/heic"]')
    await input_file[1].uploadFile(ch_avatar)
    await page.waitForSelector('div[aria-label="Сохранить"]')
    await page.click('div[aria-label="Сохранить"]')
    window = await page.J('div[aria-label="Сохранить"]')
    while window is not None:
        await asyncio.sleep(1)
        window = await page.J('div[aria-label="Сохранить"]')
    # Оновлюємо обложку
    await page.waitForSelector('div[aria-label="Добавить фото обложки"]')
    await asyncio.sleep(1)
    path = rf"data\second_categories\{category_name}\fp_images\background"
    oblozhka = os.listdir(path)
    ch_oblozhka = f"{path}\\{random.choice(oblozhka)}"
    input_file = await page.waitForXPath('//input[@accept="image/*,image/heif,image/heic"]')
    await input_file.uploadFile(ch_oblozhka)
    await page.waitForXPath('//div[@aria-label="Сохранить изменения"]', timeout=60000)
    save_btn = await page.Jx('//div[@aria-label="Сохранить изменения"]')
    await save_btn[0].press('Tab')
    await asyncio.sleep(2)
    await page.keyboard.press('Enter')
    # Додаємо біографію
    citati_list = []
    with open(f"data/second_categories/{category_name}/quotes_fp.txt", "r", encoding='utf-8') as citati_txt:
        for line in citati_txt.read().splitlines():
            if line != '':
                citati_list.append(line)
    await page.waitForSelector('div[aria-label="Добавить биографию"]')
    await page.click('div[aria-label="Добавить биографию"]')
    await page.waitForSelector('textarea[aria-label="Введите текст биографии"]')
    await page.type('textarea[aria-label="Введите текст биографии"]', random.choice(citati_list))
    await page.waitForSelector('div[aria-label="Сохранить"]')
    await page.click('div[aria-label="Сохранить"]')
    await asyncio.sleep(5)
    # Створюємо пост
    await page.evaluate('window.scrollTo(0, 0)')
    await post_fp(prflname, page)
    await page.close()


@gf.atimer
async def reposts_fp(prflname, browser, quantity):
    pages = gf.define_file_category(prflname, "phrases").pages_repost_fp
    page = await browser.newPage()
    await page.goto(random.choice(pages), {"waitUntil": ['domcontentloaded', 'networkidle2']}, timeout=60000)
    while quantity > 0:
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(4)
        await page.waitForXPath('//div[@aria-label="Отправьте это друзьям или опубликуйте в своей Хронике."]')
        reposts_btns = await page.Jx('//div[@aria-label="Отправьте это друзьям или опубликуйте в своей Хронике."]')
        try:
            ch_repost = random.choice(reposts_btns)
            await page.evaluate('''(element) => element.scrollIntoView()''', ch_repost)
            await page.evaluate('window.scrollBy(0, -300)')
            await asyncio.sleep(2)
            await ch_repost.click()
            reposts_btns.remove(ch_repost)
            repost_now = await page.waitForXPath('//span[contains(., "Поделиться сейчас")]', timeout=3000)
            await asyncio.sleep(1)
            await repost_now.click()
            quantity -= 1
            await asyncio.sleep(2)
        except Exception as err:
            print('Exception:', err)
    await page.close()


@gf.atimer
async def post_fp(prflname, page):
    category_name = gf.define_file_category(prflname, "category_name")
    await page.waitForXPath('//span[text()="Фото/видео"]')
    post_btn = await page.Jx('//span[text()="Фото/видео"]')
    await post_btn[0].click()
    try:
        await page.waitForXPath('//span[text()="Доступно всем"]', timeout=10000)
    except Exception as exc:
        print('for_all_btn', exc)
    try:
        await page.waitForXPath('//span[text()="Готово"]', timeout=10000)
        done_btn = await page.Jx('//span[text()="Готово"]')
        await done_btn[0].click()
    except Exception as exc:
        print("done_btn", exc)
    articles = os.listdir(rf"data/second_categories/{category_name}/articles/texts")
    ch_article = random.choice(articles)
    animal_name = ch_article.split(" ")[0]
    photos = os.listdir(rf"data/second_categories/{category_name}/articles/images")
    photos2 = []
    for p in photos:
        if animal_name == p.split(" ")[0]:
            photos2.append(p)
    photo_path = os.getcwd() + rf"\data\second_categories\{category_name}\articles\images\{random.choice(photos2)}"
    with open(rf"data/second_categories/{category_name}/articles/texts/{ch_article}", "r") as article_file:
        text = article_file.read()
    input_file = await page.waitForSelector(
        'input[accept="image/*,image/heif,image/heic,video/*,video/mp4,video/x-m4v,video/x-matroska,.mkv"]')
    await input_file.uploadFile(photo_path)
    await page.waitForXPath('//span[text()="Что у вас нового?"]')
    textarea = await page.Jx('//span[text()="Что у вас нового?"]')
    await textarea[0].type(text)
    await asyncio.sleep(1)
    await page.waitForXPath('//span[text()="Опубликовать"]')
    publication_btn = await page.Jx('//span[text()="Опубликовать"]')
    await publication_btn[0].click()
    time_out = 0
    while publication_btn:
        await asyncio.sleep(5)
        try:
            publication_btn = await page.Jx('//span[text()="Опубликовать"]')
            await publication_btn[0].click()
        except (IndexError, errors.ElementHandleError):
            print("Очікування публікації закінчилось")
        time_out += 1
        if time_out > 8:
            raise Exception("Публікація не закінчилася за 40 секунд")


@gf.atimer
async def fill_info_oldfp(prflname, browser):
    districts = gf.define_file_category(prflname, "phrases").district_names
    page = await browser.newPage()
    fp_url = gf.getFromTable(prflname, "FP link")
    await page.goto(fp_url + "/about/?ref=page_internal", {"waitUntil": ['domcontentloaded', 'networkidle2']})
    await asyncio.sleep(2)
    await page.bringToFront()
    _b = await page.waitForXPath('//div[text()="Укажите местоположение"]')
    await _b.click()
    await page.waitForSelector('label[aria-label="Адрес"]')
    await asyncio.sleep(1)
    await page.type('label[aria-label="Адрес"]', f"{random.choice(districts)} {random.randint(1, 200)}")
    await page.type('label[aria-label="Город"]', "Киев\n")
    await page.type('label[aria-label="Индекс"]', f"{random.randint(500000, 999999)}")
    _f = await page.waitForSelector(
        'div.leaflet-container.leaflet-touch.leaflet-fade-anim.leaflet-grab.leaflet-touch-drag.leaflet-touch-zoom')
    await _f.click()
    save_btn = await page.waitForXPath('//div[@aria-label="Закрыть"]')
    await save_btn.click()

    await asyncio.sleep(3)
    await page.bringToFront()
    index_btn = await page.Jx('//div[text()="Введите электронный адрес"]')
    await index_btn[0].click()
    await page.waitForSelector('label[aria-label="Электронный адрес"]')
    await asyncio.sleep(1)
    email = gf.getFromTable(prflname, "email:pass")
    email = email.split(":")[0] if ":" in email else email.split(" ")[0]
    await page.type('label[aria-label="Электронный адрес"]', email)
    save_btn = await page.waitForXPath('//div[@aria-label="Закрыть"]')
    await save_btn.click()

    await asyncio.sleep(3)
    await page.bringToFront()
    index_btn = await page.Jx('//div[text()="Введите адрес сайта"]')
    await index_btn[0].click()
    await page.waitForSelector('label[aria-label="Веб-сайт"]')
    await asyncio.sleep(1)
    fp_link = gf.getFromTable(prflname, "FP link")
    await page.type('label[aria-label="Веб-сайт"]', fp_link)
    save_btn = await page.waitForXPath('//div[@aria-label="Закрыть"]')
    await save_btn.click()

    await asyncio.sleep(3)
    await page.bringToFront()
    index_btn = await page.Jx('//div[text()="Редактировать часы работы"]')
    await index_btn[0].click()
    await asyncio.sleep(2)
    index_btn = await page.Jx('//span[text()="Всегда открыто"]')
    await index_btn[0].click()
    save_btn = await page.waitForXPath('//div[@aria-label="Закрыть"]')
    await save_btn.click()

    await asyncio.sleep(3)
    await page.bringToFront()
    index_btn = await page.Jx('//div[text()="Редактировать диапазон цен"]')
    await index_btn[0].click()
    await asyncio.sleep(2)
    await page.waitForXPath('//span[text()="Не применимо"]')
    index_btn = await page.Jx('//span[text()="Не применимо"]')
    await index_btn[0].click()
    save_btn = await page.waitForXPath('//div[@aria-label="Закрыть"]')
    await save_btn.click()
    await asyncio.sleep(3)
    await page.close()


@gf.atimer
async def fill_info_fp(prflname, browser):
    districts = gf.define_file_category(prflname, "phrases").district_names
    page = await browser.newPage()
    fp_url = gf.getFromTable(prflname, "FP link")
    await page.goto(fp_url + "&sk=about", {"waitUntil": ['domcontentloaded', 'networkidle2']}, timeout=60000)
    await page.keyboard.press('Escape')
    await page.bringToFront()
    try:
        await page.waitForXPath('//span[text()="Использовать Страницу"]', timeout=5000)
        for_all_btn = await page.Jx('//span[text()="Использовать Страницу"]')
        await for_all_btn[0].click()
    except Exception as err:
        print(err)
    await asyncio.sleep(2)
    # Основна частина функції
    await page.bringToFront()
    await page.waitForXPath('//span[text()="Добавьте адрес"]')
    addadress_btn = await page.Jx('//span[text()="Добавьте адрес"]')
    await addadress_btn[0].click()
    await page.waitForSelector('label[aria-label="Адрес"]')
    await asyncio.sleep(1)
    await page.type('label[aria-label="Адрес"]', f"{random.choice(districts)} {random.randint(1, 200)}")
    await page.type('label[aria-label="Город"]', "Киев\n")
    await page.type('label[aria-label="Индекс"]', f"{random.randint(500000, 999999)}")
    await page.waitForXPath('//span[text()="Сохранить"]')
    save_btn = await page.Jx('//span[text()="Сохранить"]')
    while save_btn:
        await save_btn[0].click()
        await asyncio.sleep(3)
        save_btn = await page.Jx('//span[text()="Сохранить"]')
    await asyncio.sleep(2)
    await page.evaluate('window.scrollTo(0, 0)')
    await page.bringToFront()
    index_btn = await page.Jx('//span[text()="Добавить электронный адрес"]')
    await index_btn[0].click()
    await page.waitForSelector('label[aria-label="Электронный адрес"]')
    await asyncio.sleep(1)
    email = gf.getFromTable(prflname, "email:pass")
    email = email.split(":")[0] if ":" in email else email.split(" ")[0]
    await page.type('label[aria-label="Электронный адрес"]', email)
    save_btn = await page.Jx('//span[text()="Сохранить"]')
    while save_btn:
        await save_btn[0].click()
        await asyncio.sleep(3)
        save_btn = await page.Jx('//span[text()="Сохранить"]')
    await asyncio.sleep(2)
    await page.bringToFront()
    index_btn = await page.Jx('//span[text()="Добавьте веб-сайт"]')
    await index_btn[0].click()
    await page.waitForSelector('label[aria-label="Адрес веб-сайта"]')
    await asyncio.sleep(1)
    fp_link = gf.getFromTable(prflname, "FP link")
    await page.type('label[aria-label="Адрес веб-сайта"]', fp_link)
    save_btn = await page.Jx('//span[text()="Сохранить"]')
    while save_btn:
        await save_btn[0].click()
        await asyncio.sleep(3)
        save_btn = await page.Jx('//span[text()="Сохранить"]')
    await asyncio.sleep(2)
    await page.bringToFront()
    index_btn = await page.Jx('//span[text()="Добавить часы работы"]')
    await index_btn[0].click()
    await asyncio.sleep(2)
    index_btn = await page.Jx('//span[text()="Всегда открыто"]')
    await index_btn[0].click()
    save_btn = await page.Jx('//span[text()="Сохранить"]')
    while save_btn:
        await save_btn[0].click()
        await asyncio.sleep(3)
        save_btn = await page.Jx('//span[text()="Сохранить"]')
    await asyncio.sleep(2)
    await page.bringToFront()
    index_btn = await page.Jx('//span[text()="Добавить диапазон цен"]')
    await index_btn[0].click()
    await asyncio.sleep(2)
    await page.waitForXPath('//span[text()="Не применимо"]')
    index_btn = await page.Jx('//span[text()="Не применимо"]')
    await index_btn[0].click()
    save_btn = await page.Jx('//span[text()="Сохранить"]')
    while save_btn:
        await save_btn[0].click()
        await asyncio.sleep(3)
        save_btn = await page.Jx('//span[text()="Сохранить"]')
    await asyncio.sleep(2)
    await page.close()


@gf.atimer
async def invite_friends(prflname, browser):
    page = await browser.newPage()
    fp_url = gf.getFromTable(prflname, "FP link")
    await page.goto(fp_url)
    _b = await page.waitForXPath('//div[@aria-label="Открыть настройки" or @aria-label="Другие действия"]')
    await asyncio.sleep(1)  # без паузи іноді провтикується нажаття
    await _b.click()
    await page.waitForXPath('//span[text()="Пригласить друзей"]')
    invite_btn = await page.Jx('//span[text()="Пригласить друзей"]')
    await invite_btn[0].click()
    await asyncio.sleep(2)
    selectors = ['//span[text()="Switch"]', '//span[text()="Перейти сейчас"]', '//span[text()="Переключиться"]']
    finded_switch = []
    for selector in selectors:
        finded_switch += [*await page.Jx(selector)]
    if finded_switch:
        await finded_switch[0].click()
    else:
        print("No switch button")
        for i in range(3):
            await page.keyboard.press('Tab')
        await page.keyboard.press('Enter')
    try:
        await page.waitForNavigation()
    except errors.TimeoutError:
        pass
    try:
        await page.waitForSelector('div[aria-checked="false"]', timeout=10000)
        check_boxes = await page.JJ('div[aria-checked="false"]')
        checks = 0
        while check_boxes != [] and checks < 49:
            await asyncio.sleep(1)
            check_boxes = await page.JJ('div[aria-checked="false"]')
            for box in check_boxes:
                await box.click()
                checks += 1
                await asyncio.sleep(0.3)
                if checks >= 49:
                    break
        send_invites = await page.Jx("//span[contains(text(), 'Отправить приглашения')]")
        await send_invites[0].click()
        await asyncio.sleep(1)
    except Exception as err:
        print('There is no one to invite.', err)


async def fp_filler(prflname, browser, fp_status):
    if fp_status != 'OldFP':
        await asyncio.gather(
            fill_info_fp(prflname, browser),
            reposts_fp(prflname, browser, 1))
    elif fp_status == 'OldFP':
        await fill_info_oldfp(prflname, browser)


async def z2step4(prflname, browser):
    await asyncio.gather(
        zahid1.like_pages(prflname, browser, random.randint(7, 9)),
        zahid1.join_to_groups(prflname, browser, 2))


async def z2step7(prflname, browser):
    status_fp = gf.getFromTable(prflname, 'fp_type')
    if status_fp == 'OLD':
        await fill_info_oldfp(prflname, browser)
    else:
        await asyncio.gather(
            fill_info_fp(prflname, browser),
            reposts_fp(prflname, browser, 1))


@gf.atimer
async def zahid2(prflname, ws):
    browser = await pyppeteer.connect({"browserWSEndpoint": ws, "defaultViewport": None})
    steps = [
        zahid1.add_prfl_photos(prflname, browser),                # 1
        add_friends(prflname, browser, random.randint(30, 38)),   # 2
        z2step4(prflname, browser),                               # 3
        fbacc(prflname, browser),                                 # 4
        fill_fp(prflname, browser),                               # 5
        z2step7(prflname, browser),                               # 6
        invite_friends(prflname, browser),                        # 7
        multilogin_sites(prflname, browser),                      # 8
    ]
    for index, step in enumerate(steps):
        if int(gf.getFromTable(prflname, "step")) == index + 1:
            returns = await step
            if returns == 'close':
                break
            if index != (len(steps) - 1):
                gf.increase_step(prflname)
        if index == (len(steps) - 1):
            gf.writeInTable(prflname, "step", 0)
    try:
        await browser.close()
    except errors.NetworkError as e:
        print("NetworkError:", e)


if __name__ == '__main__':
    asyncio.run(zahid2())
