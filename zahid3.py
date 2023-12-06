import asyncio
import pyppeteer
import general_functions as gf
import zahid1
import zahid2
import os
import random
from login_sites_origin import multilogin_sites
from pyppeteer import errors
from tqdm import tqdm


@gf.atimer
async def add_recomended_friends(prflname, browser, quantity):
    async def filter_friends(elements):
        nonlocal page
        # Фільтруємо друзів по буквами в алфавіті
        elements2 = []
        for el in elements:
            parent = el
            for i in range(2):
                parent = await parent.getProperty('parentNode')
            friend_name = await parent.J('a[href^="/friends/suggestions/"][tabindex="0"]')
            friend_name = await page.evaluate('(element) => element.textContent', friend_name)
            if friend_name[0].lower() in gf.alphabet:
                elements2.append(el)
        return elements2

    page = await browser.newPage()
    await page.goto('https://www.facebook.com/friends', {"waitUntil": ['domcontentloaded', 'networkidle2']},
                    timeout=60000)
    await page.bringToFront()
    await page.waitForSelector('div[role="main"]')
    await asyncio.sleep(5)
    main_div = await page.J('div[role="main"]')
    elements = await main_div.JJ('div[aria-label="Добавить в друзья"]')
    scrolls = 0
    length = None
    while len(elements) < int(quantity + (quantity * 0.5)):
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(2)
        main_div = await page.J('div[role="main"]')
        elements = await main_div.JJ('div[aria-label="Добавить в друзья"]')
        # Якщо не змінилась кількість елементів на сторінці, то зупиняємо скролл
        scrolls += 1
        if scrolls > 3 and elements == []:
            await page.close()
            return await zahid2.add_friends(prflname, browser, quantity)
        elif length == len(elements):
            print("len(elements) not changed for 3 scrolls. break. end function. restart with less quantity")
            elements = await filter_friends(elements)
            break
        if scrolls % 3 == 0:
            length = len(elements)
        elements = await filter_friends(elements)
    quantity2 = min(len(elements), quantity)
    added = 0
    i = 0
    pbar = tqdm(total=quantity, desc="Adding friends", unit="friend", ncols=100, colour='white')
    while added < quantity2:
        action = random.choice(['add', 'skip'])
        if action == 'add':
            await elements[i].click()
            added += 1
            elements.remove(elements[i])
            await asyncio.sleep(random.uniform(1, 2.5))
        i += 1
        if added >= quantity2:
            break
        elif i >= len(elements) - 1:
            i = 0
        pbar.update(n=added - pbar.n)
    pbar.close()
    await page.close()
    difference = quantity - added
    if difference > 0:
        print(f'Не додалось {difference} друзів. Повторюємо')
        await add_recomended_friends(prflname, browser, difference)


@gf.atimer
async def change_avatar_fp(prflname, browser):
    category_name = gf.define_file_category(prflname, "category_name")
    link = gf.getFromTable(prflname, "FP link")
    page = await browser.newPage()
    await page.goto(link, {"waitUntil": ['domcontentloaded', 'networkidle2']})
    # Переключаємося на режим роботи з FanPage
    try:
        await page.waitForXPath('//span[text()="Переключить"]')
        switch_btn = await page.Jx('//span[text()="Переключить"]')
        await switch_btn[0].click()
        oldfp = None
        await page.waitForNavigation({"waitUntil": ['domcontentloaded', 'networkidle2']})
    except errors.TimeoutError:
        print('Probably Old FP')
        oldfp = 'OldFP'
    # Оновлюємо аватарку
    await asyncio.sleep(3)
    await page.waitForSelector('div[aria-label="Обновить фото профиля"]')
    await page.click('div[aria-label="Обновить фото профиля"]')
    if oldfp == 'OldFP':
        red_btn = await page.waitForXPath('//span[text()="Редактировать фото профиля"]')
        await red_btn.click()
    await page.waitForSelector('div[aria-label="Загрузить фото"]')
    await asyncio.sleep(1)
    await page.waitForSelector('input[accept="image/*,image/heif,image/heic"]')
    input_file = await page.JJ('input[accept="image/*,image/heif,image/heic"]')
    path = rf"data\second_categories\{category_name}\fp_images\avatars"
    avatars = os.listdir(path)
    ch_avatar = f"{path}\\{random.choice(avatars)}"
    await input_file[1].uploadFile(ch_avatar)
    save_btn = await page.waitForSelector('div[aria-label="Сохранить"]')
    await save_btn.click()
    time_out = 0
    while save_btn:
        await asyncio.sleep(5)
        try:
            save_btn = await page.J('div[aria-label="Сохранить"]')
            await save_btn.click()
        except (AttributeError, errors.ElementHandleError):
            print("Очікування публікації закінчилось")
        time_out += 1
        if time_out > 6:
            raise Exception("Публікація не закінчилася за 30 секунд")
    await page.close()
    return oldfp


@gf.atimer
async def answer_messages(prflname, browser):
    messages = gf.define_file_category(prflname, "phrases").messages
    messages2 = gf.define_file_category(prflname, "phrases").messages2
    page = await browser.newPage()
    await page.goto('https://www.facebook.com/messages/t/', {"waitUntil": ['domcontentloaded', 'networkidle2']})
    await asyncio.sleep(2)
    try:
        await page.waitForXPath('//div[@aria-label="Отметить как прочитанное"]', timeout=10000)
    except errors.TimeoutError as exc:
        print(exc)
        await page.close()
        return
    notreaded = await page.Jx('//div[@aria-label="Отметить как прочитанное"]')
    print("Непрочитаних:", len(notreaded))
    if len(notreaded) > 2:
        random.shuffle(notreaded)
        notreaded = random.sample(notreaded, 2)
    dialogs = []
    for msg in notreaded:
        for i in range(6):
            msg = await msg.getProperty('parentNode')
        dialogs.append(await page.evaluate('(element) => element.href', msg))
    await page.close()

    async def answer(dialog):
        new_page = await browser.newPage()
        await new_page.goto(dialog, {"waitUntil": ['domcontentloaded', 'networkidle2']})
        try:
            msg_input = await new_page.waitForXPath('//div[@aria-label="Сообщение"]', timeout=10000)
            await msg_input.type(random.choice(messages) + '\n')
            await msg_input.type(random.choice(messages2) + '\n')
            await asyncio.sleep(3)
        except errors.TimeoutError:
            print("Не вдалося відповісти на повідомлення")
            try:
                await new_page.waitForXPath('//div[@aria-label="Отметить как прочитанное"]', timeout=3000)
            except errors.TimeoutError as exc:
                print(exc)
                await new_page.close()
                return
            notreaded = await new_page.Jx('//div[@aria-label="Отметить как прочитанное"]')
            notreaded_msg = random.choice(notreaded)
            for i in range(6):
                notreaded_msg = await notreaded_msg.getProperty('parentNode')
            dialog = await new_page.evaluate('(element) => element.href', notreaded_msg)
            await answer(dialog)
        await new_page.close()

    for dialog in dialogs:
        print(dialog)
        await answer(dialog)


@gf.atimer
async def make_orders(prflname, browser, quantity):
    page = await browser.newPage()
    await page.goto("https://www.facebook.com/", {"waitUntil": ['domcontentloaded', 'networkidle2']})
    ads_finded = []
    ads = {}
    scrolls = 0
    selectors = ['a[aria-label="Рекламодатель"]', 'a[aria-label="В магазин"]', 'a[aria-label="Подробнее"]',
                 'a[aria-label="Заказать"]', 'a[aria-label="Забронировать"]', 'a[aria-label="Узнать стоимость"]',
                 'a[aria-label="Подать заявку"]']
    while len(ads) < quantity:
        for selector in selectors:
            ads_finded += [*await page.JJ(selector)]
        for ad in ads_finded:
            # якщо 9й батько - li, то skip. Тому що клік по такому елементу не здійснює перехід
            parent = ad
            for i in range(9):
                parent = await parent.getProperty('parentNode')
                name = await (await parent.getProperty('tagName')).jsonValue()
            if name != "LI":
                ad_href = await page.evaluate('(element) => element.href', ad)
                if ad_href not in ads:
                    ads.update({ad_href: ad})
        if scrolls > 10:
            print("Not enough ads!")
            break
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(2)
        scrolls += 1
        await asyncio.sleep(1)
    print(f"Found {len(ads)} ads")
    ads = list(ads.values())
    clicked_ads = 0
    handle_errors = 0
    if len(ads) > 0:
        while clicked_ads < quantity:
            await page.bringToFront()
            try:
                rnd_choice = random.choice(ads)
                await rnd_choice.click()
                await asyncio.sleep(random.randint(8, 10))
                ads.remove(rnd_choice)
                clicked_ads += 1
            except pyppeteer.errors.ElementHandleError:
                print("ElementHandleError")
                await page.evaluate('window.scrollBy(0, -600)')
                await asyncio.sleep(1)
                handle_errors += 1
                if handle_errors > 30:
                    break
        ad_clicks_table = int(gf.getFromTable(prflname, 'ad_clicks'))
        gf.writeInTable(prflname, 'ad_clicks', clicked_ads + ad_clicks_table)
    await page.close()


async def z3step2(prflname, browser):
    status_fp = gf.getFromTable(prflname, 'fp_type')
    if status_fp != 'OLD':
        fp_link = gf.getFromTable(prflname, "FP link")
        page = await browser.newPage()
        await page.goto(fp_link, {"waitUntil": ['domcontentloaded', 'networkidle2']}, timeout=60000)
        await asyncio.gather(
            zahid2.post_fp(prflname, page),
            zahid2.reposts_fp(prflname, browser, 2))
        await page.close()
    elif status_fp == 'OLD':
        fp_link = gf.getFromTable(prflname, "FP link")
        page = await browser.newPage()
        await page.goto(fp_link, {"waitUntil": ['domcontentloaded', 'networkidle2']}, timeout=60000)
        for i in range(3):
            await zahid2.post_oldfp(prflname, page)
        await page.close()


async def z3step5(prflname, browser):
    await asyncio.gather(
        zahid1.join_to_groups(prflname, browser, 3),
        zahid1.like_pages(prflname, browser, random.randint(9, 12), 2, True))


@gf.atimer
async def zahid3(prflname, ws):
    browser = await pyppeteer.connect({"browserWSEndpoint": ws, "defaultViewport": None})
    steps = [
        change_avatar_fp(prflname, browser),                                # 1
        z3step2(prflname, browser),                                         # 2
        zahid2.invite_friends(prflname, browser),                           # 3
        add_recomended_friends(prflname, browser, random.randint(45, 50)),  # 4
        z3step5(prflname, browser),                                         # 5
        multilogin_sites(prflname, browser),                                # 6
        make_orders(prflname, browser, 2),                                  # 7
        answer_messages(prflname, browser),                                 # 8
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
    asyncio.run(zahid3())
