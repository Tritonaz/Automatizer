import asyncio
import pyppeteer
from pyppeteer import errors
import general_functions as gf
import zahid1
import zahid2
import zahid3
import zahid4
import random
from tqdm import tqdm
from login_sites_origin import multilogin_sites


@gf.atimer
async def delete_some_friends(browser):
    page = await browser.newPage()
    await page.goto("https://www.facebook.com/friends/list", {"waitUntil": ['domcontentloaded', 'networkidle0']})
    await asyncio.sleep(2)
    await page.bringToFront()
    await page.waitForSelector('div[aria-label="Ещё"]')
    more_btns = await page.JJ('div[aria-label="Ещё"]')
    more_btns = random.sample(more_btns, random.randint(3, 5))
    await page.bringToFront()
    pbar = tqdm(total=len(more_btns), desc='Видалення друзів', unit='друг', colour='white')
    for mb in more_btns:
        await mb.click()
        await asyncio.sleep(1)
        del_btns = await page.waitForXPath('//span[contains(., "Удалить")]')
        await del_btns.click()
        await asyncio.sleep(1)
        confirm_btn = await page.waitForSelector('div[aria-label="Подтвердить"]')
        await confirm_btn.click()
        pbar.update(1)
    pbar.close()
    await page.close()


@gf.atimer
async def turn_on_pro(prflname, browser):
    page = await browser.newPage()
    await page.goto(gf.getFromTable(prflname, 'link'), {"waitUntil": ['domcontentloaded', 'networkidle2']},
                    timeout=60000)
    more_btn = await page.waitForSelector('div[aria-label="Открыть настройки"]')
    await more_btn.click()
    try:
        turn_on_pro_btn = await page.waitForXPath('//span[contains(., "Включите профессиональный режим")]',
                                                  timeout=5000)
    except pyppeteer.errors.TimeoutError:
        return 'NoPRO'
    await turn_on_pro_btn.click()
    on_btn = await page.waitForSelector('div[aria-label="Включить"]')
    await on_btn.click()
    done_btn = await page.waitForSelector('div[aria-label="Готово"]')
    await done_btn.click()
    await asyncio.sleep(3)
    await page.close()
    return None


async def z6step2(prflname, browser):
    status_fp = gf.getFromTable(prflname, 'fp_type')
    if status_fp != 'OLD':
        await zahid2.reposts_fp(prflname, browser, 2)
    elif status_fp == 'OLD':
        fp_link = gf.getFromTable(prflname, "FP link")
        page = await browser.newPage()
        await page.goto(fp_link, {"waitUntil": ['domcontentloaded', 'networkidle2']})
        for i in range(2):
            await zahid2.post_oldfp(prflname, page)
        await page.close()


async def z6step4(prflname, browser):
    q = 35 - int(float(gf.getFromTable(prflname, "liked_pages")))
    q = 4 if q <= 0 else q + 4
    print("Розрахована quantity pages to like:", q)
    await asyncio.gather(
        zahid1.like_pages(prflname, browser, q, 2, True),
        zahid1.join_to_groups(prflname, browser, 3))


async def z6step7(prflname, browser):
    q = 100 - int(gf.getFromTable(prflname, "friends"))
    q = 15 if q <= 0 else q + 15
    print("Розрахована quantity friends to add:", q)
    await zahid3.add_recomended_friends(prflname, browser, q)


@gf.atimer
async def zahid6(prflname, ws):
    browser = await pyppeteer.connect({"browserWSEndpoint": ws, "defaultViewport": None})
    steps = [
        zahid4.post_fp4(prflname, browser),             # 1
        z6step2(prflname, browser),                     # 2
        zahid2.invite_friends(prflname, browser),       # 3
        z6step4(prflname, browser),                     # 4
        multilogin_sites(prflname, browser),            # 5
        delete_some_friends(browser),                   # 6
        z6step7(prflname, browser),                     # 7
        gf.gather_data(prflname, browser),              # 8
        zahid3.answer_messages(prflname, browser),      # 9
        zahid3.make_orders(prflname, browser, 2),       # 10
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
    asyncio.run(zahid6())
