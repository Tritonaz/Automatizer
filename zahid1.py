import random
import os
import shutil
import asyncio
import pyppeteer
import after_reg
import general_functions as gf
from pyppeteer import errors
from tqdm import tqdm
from data import access_data
import telegram_keyboards as tkb
from aiogram import Bot


API_TOKEN = access_data.API_TOKEN
bot = Bot(token=API_TOKEN)
my_id = access_data.my_id  # тільки адмін може використовувати бота


@gf.atimer
async def add_bio(prflname, browser):
    category_name = gf.define_file_category(prflname, "category_name")
    prfl_link = gf.getFromTable(prflname, "link")
    quotes = []
    with open(f"data/second_categories/{category_name}/quotes_main.txt", "r", encoding='utf-8') as quotes_txt:
        for line in quotes_txt.read().splitlines():
            if line != '':
                quotes.append(line)
    random.shuffle(quotes)
    page = await browser.newPage()
    await page.goto(prfl_link, {"waitUntil": ['domcontentloaded', 'networkidle2']})
    try:
        await page.waitForXPath('//span[text()="Добавить биографию"]', timeout=15000)
    except errors.TimeoutError:
        await page.goto('https://www.facebook.com/settings/?tab=your_facebook_information')
        iframe = await page.waitForSelector('iframe[src^="https://www.facebook.com/settings/?tab=your_facebook_information"]')
        iframe_content = await iframe.contentFrame()
        btn = await iframe_content.J('a[title="Russian"]')
        await page.keyboard.press('Escape')
        await btn.click()
        await asyncio.sleep(2)
        await page.goto(prfl_link, {"waitUntil": ['domcontentloaded', 'networkidle2']})
        await page.waitForXPath('//span[text()="Добавить биографию"]')
    add_bio_btn = await page.Jx('//span[text()="Добавить биографию"]')
    await add_bio_btn[0].click()
    await page.waitForSelector('textarea[aria-label="Введите текст биографии"]')
    await page.type('textarea[aria-label="Введите текст биографии"]', random.choice(quotes))
    await asyncio.sleep(1)
    save_btn = await page.Jx('//span[text()="Сохранить"]')
    await save_btn[0].click()
    time_out = 0
    while save_btn:
        await asyncio.sleep(5)
        try:
            save_btn = await page.Jx('//span[text()="Сохранить"]')
            await save_btn[0].click()
        except (IndexError, errors.ElementHandleError):
            print("Очікування публікації закінчилось")
        time_out += 1
        if time_out > 6:
            raise Exception("Публікація не закінчилася за 30 секунд")

    @gf.atimer
    async def add_hobi():
        red_btn = await page.waitForXPath('//div[@aria-label="Редактировать хобби"]', timeout=5000)
        await red_btn.click()
        inpt = await page.waitForXPath('//input[@placeholder="Как вы развлекаетесь?"]')
        await asyncio.sleep(2)
        added_labels = await page.Jx('//li[@aria-selected="true"]')
        while len(added_labels) <= 7:
            await inpt.focus()
            await page.keyboard.press('Backspace')
            await inpt.type(random.choice(list(gf.alphabet)))
            await asyncio.sleep(2)
            labels = await page.Jx('//li[@aria-selected="false"]')
            i = 8 - len(added_labels)
            if i > 0:
                if len(labels) > i:
                    random.shuffle(labels)
                    labels = random.sample(labels, i)
                for label in labels:
                    try:
                        await label.click()
                    except errors.ElementHandleError:
                        pass
                    await asyncio.sleep(1)
            added_labels = await page.Jx('//li[@aria-selected="true"]')
        await asyncio.sleep(1)
        await page.waitForXPath('//span[contains(., "Сохранить")]')
        save_btn = await page.Jx('//span[contains(., "Сохранить")]')
        await save_btn[-1].click()
    try:
        await add_hobi()
    except errors.TimeoutError as er:
        await bot.send_message(my_id, er)


@gf.atimer
async def add_prfl_photos(prflname, browser):
    prfl_link = gf.getFromTable(prflname, "link")
    page = await browser.newPage()
    await page.goto(prfl_link + "&sk=photos", {"waitUntil": ['domcontentloaded', 'networkidle2']})
    pathPhoto = os.getcwd() + rf"\photos\{prflname}"
    prflPhotos = os.listdir(pathPhoto)
    srcPhoto1 = fr"{pathPhoto}\{prflPhotos[0]}"
    srcPhoto2 = fr"{pathPhoto}\{prflPhotos[1]}"
    path_dir = os.getcwd() + rf"\used_photos"
    if not os.path.exists(fr"{path_dir}\{prflname}"):
        os.mkdir(os.path.join(path_dir, prflname))
    pathAUphoto = os.getcwd() + rf"\used_photos\{prflname}"
    shutil.move(srcPhoto1, pathAUphoto)
    shutil.move(srcPhoto2, pathAUphoto)
    srcChoosenPhoto1 = fr"{pathAUphoto}\{prflPhotos[0]}"
    srcChoosenPhoto2 = fr"{pathAUphoto}\{prflPhotos[1]}"
    choosenPhotosPath = [srcChoosenPhoto1, srcChoosenPhoto2]
    await page.bringToFront()
    input_file = await page.waitForSelector(
        'input[accept="image/*,image/heif,image/heic,video/*,video/mp4,video/x-m4v,video/x-matroska,.mkv"]')
    await input_file.uploadFile(*choosenPhotosPath)
    try:
        await asyncio.sleep(2)
        await page.waitForXPath('//span[text()="Доступно всем"]', timeout=5000)
        for_all_btn = await page.Jx('//span[text()="Доступно всем"]')
        await for_all_btn[0].click()
    except Exception as exc:
        print("for_all_btn", exc)
    try:
        await asyncio.sleep(2)
        await page.waitForXPath('//span[text()="Готово"]', timeout=2000)
        done_btn = await page.Jx('//span[text()="Готово"]')
        await done_btn[0].click()
    except Exception as exc:
        print("done_btn", exc)
    await page.waitForXPath('//span[text()="Опубликовать"]')
    await asyncio.sleep(2)
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
        if time_out > 6:
            raise Exception("Публікація не закінчилася за 30 секунд")
    await page.close()


@gf.atimer
async def join_to_groups(prflname, browser, quantity):
    themes = gf.define_file_category(prflname, "phrases").categories
    link = f'https://www.facebook.com/search/groups?q={random.choice(themes)}'
    page = await browser.newPage()
    await page.goto(link, {"waitUntil": ['domcontentloaded', 'networkidle2']}, timeout=60000)
    await page.bringToFront()
    await page.waitForSelector('div[aria-label^="Вступить в группу"]')
    join_btns = await page.JJ('div[aria-label^="Вступить в группу"]')
    if len(join_btns) > quantity:
        random.shuffle(join_btns)
        join_btns = random.sample(join_btns, quantity)
    await page.bringToFront()
    for btn in join_btns:
        await btn.click()
        await asyncio.sleep(1)
    await page.close()


@gf.atimer
async def like_pages(prflname, browser, q_pages, q_reposts=2, add_followers=False):
    if add_followers is True:
        q_added_pages = await gf.add_followers_func(prflname, browser)
        q_pages = q_pages - q_added_pages
        q_pages = q_pages if q_pages > 0 else 2
    themes = gf.define_file_category(prflname, "phrases").categories
    page = await browser.newPage()
    link = f'https://www.facebook.com/search/pages?q={random.choice(themes)}'
    await page.goto(link, {"waitUntil": ['domcontentloaded', 'networkidle2']}, timeout=60000)
    await asyncio.sleep(3)
    like_btns = await page.JJ('div[aria-label*="равится"]')
    pbar = tqdm(total=q_pages, desc="Like pages", unit="page", colour='white')
    while q_pages > 0:
        try:
            ch_btn = like_btns.pop(random.randint(0, len(like_btns)))
            await ch_btn.click()
            q_pages -= 1
            pbar.update(1)
            await asyncio.sleep(2)
        except IndexError:
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(3)
            like_btns = await page.JJ('div[aria-label*="равится"]')
            like_btns += await page.JJ('div[aria-label="Подписаться"]')
    pbar.close()
    liked_pages_btns = await page.JJ('a[aria-label*="равится"]')
    liked_pages_btns += await page.JJ('a[aria-label="Вы подписаны"]')
    liked_pages_links = []
    for btn in liked_pages_btns:
        liked_pages_links.append(await (await btn.getProperty('href')).jsonValue())
    reposts_made = 0  # зроблених репостів
    # Паралельний лайкинг сторінок
    if len(liked_pages_links) > 3:
        random.shuffle(liked_pages_links)
        liked_pages_links = random.sample(liked_pages_links, 3)

    async def liking(browser, link):
        new_page = await browser.newPage()
        await new_page.bringToFront()
        await new_page.goto(link, timeout=120000)  # , {"waitUntil": ['domcontentloaded', 'networkidle2']}
        await new_page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await new_page.bringToFront()
        await asyncio.sleep(3)
        page_like_btns = await get_like_btns(new_page)
        q_liked = 0
        empty_page_like_btns = 0
        nonlocal reposts_made
        numlikes = random.randint(2, 5)
        link_name = link[:-1].split('/')[-1]
        pbar = tqdm(total=numlikes, desc=f"Liking {link_name} page feed", unit="post", colour='white')
        while q_liked < numlikes:
            try:
                ch_like = random.choice(page_like_btns)
                page_like_btns.remove(ch_like)
                await new_page.evaluate('window.scrollBy(0, -300)')
                await ch_like.click()
                q_liked += 1
                pbar.update(1)
                await asyncio.sleep(random.randint(3, 5))
            except Exception as err:
                print(err)
                empty_page_like_btns += 1
                if empty_page_like_btns >= 5:
                    break
                await new_page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await new_page.bringToFront()
                await asyncio.sleep(3)
                page_like_btns = await get_like_btns(new_page)
            if reposts_made < int(q_reposts):
                try:
                    await new_page.bringToFront()
                    repost_btn = await new_page.JJ(
                        'div[aria-label="Отправьте это друзьям или опубликуйте в своей Хронике."]')
                    repost_btn = random.choice(repost_btn)
                    await new_page.evaluate('window.scrollBy(0, -300)')
                    await repost_btn.click()
                    await asyncio.sleep(3)
                    await new_page.bringToFront()
                    repost_now = await new_page.waitForXPath('//span[contains(., "Поделиться сейчас")]', timeout=2000)
                    await repost_now.click()
                    reposts_made += 1
                    await asyncio.sleep(2)
                except Exception as err:
                    print(type(err), err)
        pbar.close()
        await new_page.close()

    async def get_like_btns(new_page):
        page_like_btns = await new_page.JJ('div[aria-label="Нравится"]')
        for lkbtn in page_like_btns:
            if await lkbtn.querySelector('i') is None:
                page_like_btns.remove(lkbtn)
        return page_like_btns

    await page.close()
    await asyncio.gather(*[liking(browser, link) for link in liked_pages_links])


@gf.atimer
async def off_notifications(browser):
    page = await browser.newPage()
    await page.goto('chrome://settings/content/siteDetails?site=https%3A%2F%2Fwww.facebook.com%2F')
    _s = await page.evaluateHandle(
        'document.querySelector("body > settings-ui").shadowRoot.querySelector("#main").shadowRoot.querySelector("settings-basic-page").shadowRoot.querySelector("#basicPage > settings-section.expanded > settings-privacy-page").shadowRoot.querySelector("#pages > settings-subpage > site-details").shadowRoot.querySelector("div.list-frame > site-details-permission:nth-child(5)").shadowRoot.querySelector("#permission")')
    await _s.click()
    await asyncio.sleep(1)
    await page.keyboard.press('ArrowDown')
    await page.keyboard.press('ArrowDown')
    await page.keyboard.press('Enter')
    await asyncio.sleep(1)
    await page.close()


async def z1step5(prflname, browser):
    await asyncio.gather(join_to_groups(prflname, browser, 1), like_pages(prflname, browser, 1))


@gf.atimer
async def zahid1(prflname, ws):
    browser = await pyppeteer.connect({"browserWSEndpoint": ws, "defaultViewport": None})
    email_status = 'Без пошти.' if str(gf.getFromTable(prflname, "name")).endswith('(без пошти)') else ''
    msg = await bot.send_message(my_id, f"{prflname} 1й захід. {email_status}", reply_markup=tkb.kb_zahid1)
    gf.userbot_choice = 'start'  # starts without getting answer
    while True:
        if gf.userbot_choice == 'start':
            steps = [
                after_reg.loginEmail(prflname, browser),  # 1
                off_notifications(browser),               # 2
                add_bio(prflname, browser),               # 3
                add_prfl_photos(prflname, browser),       # 4
                z1step5(prflname, browser)                # 5
            ]
            for index, step in enumerate(steps):
                if int(gf.getFromTable(prflname, "step")) == index + 1:
                    returns = await step
                    if returns == 'close':
                        break
                    if index != (len(steps) - 1):
                        gf.increase_step(prflname)
            gf.userbot_choice = None
            await bot.send_message(my_id, f"Перевірте основну сторінку і оберіть наступну дію 👆 {email_status}")
        if gf.userbot_choice == 'create_bm':
            gf.userbot_choice = None
            await gf.trigger_rd_fbaccio(prflname, browser)  # Створення БМ ака виклик РД
            await bot.send_message(my_id, f"Закінчіть виклик")
        elif gf.userbot_choice == 'trigger_rd':
            gf.userbot_choice = None
            await gf.trigger_rd(prflname, browser)  # Створення БМ ака виклик РД
            await bot.send_message(my_id, f"Trigger finished")
        if gf.userbot_choice == 'final':
            gf.userbot_choice = None
            await msg.delete()
            gf.writeInTable(prflname, "step", 0)
            try:
                await browser.close()
            except Exception as err:
                print(err)
            break
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(zahid1())
