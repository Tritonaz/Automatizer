import asyncio
import shutil
import pyppeteer
import general_functions as gf
import os
import random
import zahid1
import zahid2
import zahid3
from zahid3 import make_orders
from tqdm import tqdm
from login_sites_origin import multilogin_sites
from pyppeteer import errors


@gf.atimer
async def post_fp4(prflname, browser):
    link = gf.getFromTable(prflname, "FP link")
    page = await browser.newPage()
    await page.goto(link)
    # Переключаємося на режим роботи з FanPage
    try:
        await page.waitForXPath('//span[text()="Переключить"]', timeout=10000)
    except errors.TimeoutError:
        return await zahid2.post_oldfp(prflname, page)
    switch_btn = await page.Jx('//span[text()="Переключить"]')
    await switch_btn[0].click()
    await page.waitForNavigation()
    # Підтверджуєм кукі, якщо потрібно
    try:
        await page.waitForXPath(
            '//div[@aria-label="Разрешить основные и необязательные cookie" or @aria-label="Разрешить все cookie"]',
            timeout=5000)
        _b = await page.Jx(
            '//div[@aria-label="Разрешить основные и необязательные cookie" or @aria-label="Разрешить все cookie"]')
        await _b[-1].click()
        await asyncio.sleep(1)
    except errors.TimeoutError:
        try:
            await page.waitForXPath('//input[@aria-checked="false"]', timeout=3000)
            _ss = await page.Jx('//input[@aria-checked="false"]')
            for _s in _ss:
                await _s.click()
            await asyncio.sleep(1)
            _b = await page.waitForXPath('//div[@aria-label="I agree" or @aria-label="Принимаю"]', timeout=3000)
            await _b.click()
            await asyncio.sleep(1)
            _b = await page.waitForXPath('//div[@aria-label="Закрыть"]', timeout=5000)
            await _b.click()
            await page.goto(link, {"waitUntil": ['domcontentloaded', 'networkidle2']})
        except errors.TimeoutError:
            pass
    # Публікуємо пост
    post_btn = await page.waitForXPath('//span[text()="Фото/видео"]')
    await asyncio.sleep(1)
    await post_btn.click()
    try:
        await page.waitForXPath('//span[text()="Доступно всем"]', timeout=5000)
        await page.waitForXPath('//span[text()="Готово"]', timeout=5000)
        done_btn = await page.Jx('//span[text()="Готово"]')
        await done_btn[0].click()
    except Exception as exc:
        print("span[text()=\"Доступно всем\".", exc)

    category_name = gf.define_file_category(prflname, "category_name")
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
    textarea = await page.waitForXPath('//div[@aria-label="Что у вас нового?"]')
    await textarea.type(text)
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
    await page.close()


@gf.atimer
async def change_avatar_profile(prflname, browser):
    link = gf.getFromTable(prflname, "link")
    page = await browser.newPage()
    await page.goto(link)
    await asyncio.sleep(2)
    await page.waitForSelector('div[aria-label="Обновить фото профиля"]')
    await page.click('div[aria-label="Обновить фото профиля"]')
    await page.waitForXPath('//span[text()="Загрузить фото"]')

    await page.waitForSelector('input[accept="image/*,image/heif,image/heic"]')
    input_file = await page.JJ('input[accept="image/*,image/heif,image/heic"]')
    await asyncio.sleep(1)

    pathPhoto = os.getcwd() + rf"\photos\{prflname}"
    prflPhotos = os.listdir(pathPhoto)
    srcPhoto1 = fr"{pathPhoto}\{prflPhotos[0]}"
    path_dir = os.getcwd() + rf"\used_photos"
    if not os.path.exists(fr"{path_dir}\{prflname}"):
        os.mkdir(os.path.join(path_dir, prflname))
    pathAUphoto = os.getcwd() + rf"\used_photos\{prflname}"
    shutil.move(srcPhoto1, pathAUphoto)
    srcChoosenPhoto1 = fr"{pathAUphoto}\{prflPhotos[0]}"
    await input_file[-1].uploadFile(srcChoosenPhoto1)
    try:
        await page.waitForXPath('//span[text()="Доступно всем"]', timeout=3000)
        for_all_btn = await page.Jx('//span[text()="Доступно всем"]')
        await for_all_btn[0].click()
    except Exception as exc:
        print("for_all_btn", exc)
    try:
        await page.waitForXPath('//span[text()="Готово"]', timeout=2000)
        done_btn = await page.Jx('//span[text()="Готово"]')
        await done_btn[0].click()
    except Exception as exc:
        print("done_btn", exc)
    await page.waitForXPath('//span[text()="Сохранить"]')
    await asyncio.sleep(2)
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
    await page.close()


@gf.atimer
async def create_stories(prflname, browser):
    page = await browser.newPage()
    await page.goto('https://www.facebook.com/stories/create/', {"waitUntil": ['domcontentloaded', 'networkidle2']},
                    timeout=60000)
    await asyncio.sleep(2)
    pathPhoto = os.getcwd() + rf"\photos\{prflname}"
    prflPhotos = os.listdir(pathPhoto)
    srcPhoto1 = fr"{pathPhoto}\{prflPhotos[0]}"
    path_dir = os.getcwd() + rf"\used_photos"
    if not os.path.exists(fr"{path_dir}\{prflname}"):
        os.mkdir(os.path.join(path_dir, prflname))
    pathAUphoto = os.getcwd() + rf"\used_photos\{prflname}"
    shutil.move(srcPhoto1, pathAUphoto)
    srcChoosenPhoto1 = fr"{pathAUphoto}\{prflPhotos[0]}"
    input_file = await page.waitForSelector('input[accept="image/*,image/heif,image/heic"]')
    await input_file.uploadFile(srcChoosenPhoto1)
    await page.waitForXPath('//span[text()="Поделиться в истории"]')
    await asyncio.sleep(2)
    publication_btn = await page.Jx('//span[text()="Поделиться в истории"]')
    await publication_btn[0].click()
    time_out = 0
    while publication_btn:
        await asyncio.sleep(5)
        try:
            publication_btn = await page.Jx('//span[text()="Поделиться в истории"]')
            await publication_btn[0].click()
        except (IndexError, errors.ElementHandleError):
            print("Очікування публікації закінчилось")
        time_out += 1
        if time_out > 6:
            raise Exception("Публікація не закінчилася за 30 секунд")
    await page.close()


@gf.atimer
async def post_myprofile(prflname, browser):
    category_name = gf.define_file_category(prflname, "category_name")
    link = gf.getFromTable(prflname, "link")
    page = await browser.newPage()
    await page.goto(link, timeout=60000)
    await asyncio.sleep(2)
    # Публікуємо пост
    await page.waitForXPath('//span[text()="Фото/видео"]')
    post_btn = await page.Jx('//span[text()="Фото/видео"]')
    await post_btn[0].click()
    try:
        await page.waitForXPath('//span[text()="Доступно всем"]', timeout=5000)
        await page.waitForXPath('//span[text()="Готово"]', timeout=5000)
        done_btn = await page.Jx('//span[text()="Готово"]')
        await done_btn[0].click()
    except Exception as exc:
        print("span[text()=\"Доступно всем\"", exc)
    quotes = []
    with open(f"data/second_categories/{category_name}/quotes_main.txt", "r", encoding='utf-8') as quotes_txt:
        for line in quotes_txt.read().splitlines():
            if line != '':
                quotes.append(line)
    images_path = rf"data/second_categories/{category_name}/fp_images/background"
    chosen_image_path = rf"{images_path}\{random.choice(os.listdir(images_path))}"
    input_file = await page.waitForSelector(
        'input[accept="image/*,image/heif,image/heic,video/*,video/mp4,video/x-m4v,video/x-matroska,.mkv"]')
    await input_file.uploadFile(chosen_image_path)
    await page.waitForXPath('//span[text()="Что у вас нового?"]')
    textarea = await page.Jx('//span[text()="Что у вас нового?"]')
    await textarea[0].type(random.choice(quotes))
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
        if time_out > 6:
            raise Exception("Публікація не закінчилася за 30 секунд")
    await page.close()


@gf.atimer
async def groups_some_likes(browser):
    page = await browser.newPage()
    await page.goto('https://www.facebook.com/groups/feed/', timeout=60000)
    q = random.randint(3, 5)
    clicked = 0
    pbar = tqdm(total=q, desc="Liking groups feed", unit="post", colour='white')
    while clicked < q:
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(2)
        like_btns = await page.Jx('//div[@aria-label="Нравится"]')
        for lkbtn in like_btns:
            if await lkbtn.querySelector('i') == None:
                like_btns.remove(lkbtn)
        if len(like_btns) != 0:
            ch_btn = random.choice(like_btns)
            like_btns.remove(ch_btn)
            try:
                await page.evaluate('window.scrollBy(0, -300)')
                await ch_btn.click()
                clicked += 1
                pbar.update(1)
            except errors.ElementHandleError:
                pass
    pbar.close()
    await page.close()


async def z4step4(prflname, browser):
    await asyncio.gather(
        create_stories(prflname, browser),
        post_myprofile(prflname, browser))


async def z4step6(prflname, browser):
    await asyncio.gather(
        zahid1.join_to_groups(prflname, browser, 3),
        groups_some_likes(browser),
        zahid1.like_pages(prflname, browser, random.randint(9, 12), 2, True))


@gf.atimer
async def zahid4(prflname, ws):
    browser = await pyppeteer.connect({"browserWSEndpoint": ws, "defaultViewport": None})
    steps = [
        post_fp4(prflname, browser),                                                # 1
        zahid2.invite_friends(prflname, browser),                                   # 2
        change_avatar_profile(prflname, browser),                                   # 3
        z4step4(prflname, browser),                                                 # 4
        zahid3.add_recomended_friends(prflname, browser, random.randint(43, 50)),   # 5
        z4step6(prflname, browser),                                                 # 6
        multilogin_sites(prflname, browser),                                        # 7
        make_orders(prflname, browser, 2),                                          # 8
        zahid3.answer_messages(prflname, browser),                                  # 9
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
    asyncio.run(zahid4())
