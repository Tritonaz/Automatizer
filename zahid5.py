import asyncio
import pyppeteer
import general_functions as gf
import random
import zahid1
import zahid2
import zahid3
import zahid4
from login_sites_origin import multilogin_sites
import shutil
import os
from pyppeteer import errors
from tqdm import tqdm


@gf.atimer
async def create_albom(prflname, browser):
    page = await browser.newPage()
    await page.goto('https://www.facebook.com/media/set/create', {"waitUntil": ['domcontentloaded', 'networkidle2']},
                    timeout=60000)
    album_name = await page.waitForSelector('label[aria-label="Название альбома"]')
    await album_name.focus()
    await page.keyboard.type(random.choice(["Collage", "My Albom", "Me", ]))
    path_dir = os.getcwd() + rf"\used_photos"
    if not os.path.exists(fr"{path_dir}\{prflname}"):
        os.mkdir(os.path.join(path_dir, prflname))
    pathPhoto = os.getcwd() + rf"\photos\{prflname}"
    prflPhotos = os.listdir(pathPhoto)
    for photo in prflPhotos[:4]:
        shutil.move(fr"{pathPhoto}\{photo}", rf"{path_dir}\{prflname}")
    choosenPhotosPath = [rf"{path_dir}\{prflname}\{ch_photo}" for ch_photo in prflPhotos[:4]]
    input_file = await page.J(
        'input[accept="image/*,image/heif,image/heic,video/*,video/mp4,video/x-m4v,video/x-matroska,.mkv"]')
    await input_file.uploadFile(*choosenPhotosPath)
    send_btn = await page.waitForSelector('div[aria-label="Отправить"]')
    while send_btn != None:
        try:
            await send_btn.click()
        except errors.ElementHandleError:
            print('Element not found')
        await asyncio.sleep(4)
        send_btn = await page.J('div[aria-label="Отправить"]')
    await page.close()


@gf.atimer
async def like_newsfeed(browser, quantity):
    page = await browser.newPage()
    await page.goto('https://www.facebook.com/', {"waitUntil": ['domcontentloaded', 'networkidle2']}, timeout=60000)
    await page.bringToFront()
    clicked = 0
    pbar = tqdm(total=quantity, desc='Liking posts(news feed)', unit='post', colour='white')
    while clicked < quantity:
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(2)
        like_btns = await page.Jx('//div[@aria-label="Нравится"]')
        for lkbtn in like_btns:
            if await lkbtn.querySelector('i') == None:
                like_btns.remove(lkbtn)
        ch_btn = random.choice(like_btns)
        like_btns.remove(ch_btn)
        try:
            await ch_btn.hover()
            await ch_btn.click()
            clicked += 1
            pbar.update(1)
        except errors.ElementHandleError:
            print('Element not found')
            pass
    pbar.close()
    await page.close()


@gf.atimer
async def repost_tsn(prflname, browser, quantity):
    themes = gf.define_file_category(prflname, "phrases").tsn_themes
    page = await browser.newPage()
    await page.goto(random.choice(themes), {"waitUntil": ['domcontentloaded', 'networkidle2']}, timeout=60000)
    await page.bringToFront()
    try:
        accept_btn = await page.waitForSelector('button#cookieBtn')
        await accept_btn.click()
    except errors.TimeoutError:
        pass
    await asyncio.sleep(1)
    await page.waitForSelector('a.c-card__link')
    urls = await page.JJ('a.c-card__link')
    if len(urls) > quantity:
        random.shuffle(urls)
        urls = random.sample(urls, quantity)
    links = []
    for url in urls:
        links.append(await page.evaluate('(element) => element.href', url))
    for link in links:
        await page.bringToFront()
        try:
            await page.goto(link, timeout=15000)
        except Exception:
            pass
        share_btn = await page.waitForSelector('button[data-type="facebook"]')
        await share_btn.click()
        # Wait for the new tab to open
        new_page = None
        while not new_page:
            pages = await browser.pages()
            # Find the page with the matching URL
            for p in pages:
                if 'facebook.com/sharer' in p.url:
                    new_page = p
                    break
            # If the page hasn't opened yet, wait a bit and try again
            if not new_page:
                await asyncio.sleep(1)
        # Switch to the new page
        await new_page.bringToFront()
        await new_page.waitForSelector('button[name="__CONFIRM__"]', timeout=10000)
        await asyncio.sleep(3)
        await new_page.click('button[name="__CONFIRM__"]')
        await new_page.waitForNavigation()
    await page.close()


async def z5step4(prflname, browser):
    await asyncio.gather(
        create_albom(prflname, browser),
        zahid3.add_recomended_friends(prflname, browser, random.randint(45, 50)))


async def z5step5(prflname, browser):
    await asyncio.gather(
        zahid1.join_to_groups(prflname, browser, 3),
        zahid1.like_pages(prflname, browser, random.randint(6, 9), 3, True))


async def z5step7(prflname, browser):
    await asyncio.gather(
        repost_tsn(prflname, browser, 2),
        like_newsfeed(browser, random.randint(3, 5)))


@gf.atimer
async def zahid5(prflname, ws):
    browser = await pyppeteer.connect({"browserWSEndpoint": ws, "defaultViewport": None})
    steps = [
        zahid4.post_fp4(prflname, browser),                 # 1
        zahid2.invite_friends(prflname, browser),           # 2
        gf.gather_data(prflname, browser),                  # 3
        z5step4(prflname, browser),                         # 4
        z5step5(prflname, browser),                         # 5
        multilogin_sites(prflname, browser),                # 6
        z5step7(prflname, browser),                         # 7
        zahid3.make_orders(prflname, browser, 2),           # 8
        zahid3.answer_messages(prflname, browser),          # 9
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
    asyncio.run(zahid5())
