import random
from pyppeteer import errors
import general_functions as gf
import zahid2
import zahid3
import zahid4
import pyppeteer
import asyncio
import pandas as pd
from aiogram import Bot
from data import access_data
import telegram_keyboards as tkb

API_TOKEN = access_data.API_TOKEN
bot = Bot(token=API_TOKEN)
my_id = access_data.my_id  # тільки адмін може використовувати бота
WORKSHEET_ID = access_data.WORKSHEET_ID


@gf.atimer
async def beginning_zahid(browser):
    links = ["https://www.facebook.com/settings/?tab=your_facebook_information",
             "https://chrome.google.com/webstore/detail/cookiebro/lpmockibcakojclnfmhchibmdpmollgn?hl=uk",
             "https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg?hl=uk",
             "https://chrome.google.com/webstore/detail/access-token-extractor-by/jdiljjjlnmciheackloanmdcnkoknpji",
             "https://www.facebook.com/accountquality",
             "https://www.facebook.com/adsmanager/manage/all?nav_source=comet&nav_entry_point=comet_bookmark", ]

    async def open_link(link):
        page = await browser.newPage()
        await page.goto(link, timeout=90000)

    await asyncio.gather(*[open_link(link) for link in links])


async def fill_vydacha(prflname):
    global WORKSHEET_ID
    data = gf.get_my_sheet(WORKSHEET_ID)
    df = pd.DataFrame(data[1:], columns=data[0])
    reg = gf.getFromTable(prflname, 'reg')
    fb_pass = gf.getFromTable(prflname, 'fb pass')
    birth = gf.getFromTable(prflname, 'birth')
    email_pass = gf.getFromTable(prflname, 'email:pass')
    fa2 = gf.getFromTable(prflname, '2fa')
    name = gf.getFromTable(prflname, 'name')
    link = gf.getFromTable(prflname, 'link')
    fullname_prfl = prflname
    bm = gf.getFromTable(prflname, 'BM')
    if 'ПЗРД' in gf.getFromTable(prflname, 'BM_status') and 'ПЗРД' not in gf.getFromTable(prflname, 'RD'):
        fullname_prfl += f' dzrd {bm.split("_")[0]} PZRD'
    else:
        fullname_prfl += f' {bm}' if 'BM_rk' in bm else ''
        fullname_prfl += ' ПЗРД' if 'ПЗРД' in gf.getFromTable(prflname, 'RD') else ''
    df.loc[len(df)] = [reg, fullname_prfl, fb_pass, birth, email_pass, fa2, 'user_agent', 'token', 'multitoken',
                       name, link, 'quality_pic', 'document', 'cookie']
    data = [df.columns.values.tolist()] + df.values.tolist()
    gf.update_my_sheet(WORKSHEET_ID, data)


@gf.atimer
async def like_myfeed(prflname, browser):
    page = await browser.newPage()
    my_url = gf.getFromTable(prflname, 'link')
    await page.goto(my_url, {"waitUntil": ["domcontentloaded", "networkidle2"]})
    await page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
    await asyncio.sleep(2)
    await page.waitForSelector('div[aria-label="Нравится"]')
    like_btns = await page.JJ('div[aria-label="Нравится"]')
    for btn in like_btns:
        await btn.click()
        await asyncio.sleep(1)
    articles = await page.JJ('div[role="article"]')
    unic_articles = []
    comment_inputs = []
    for article in articles:
        attribute_name = 'aria-posinset'  # атрибут для номеру посту. Пости мають унікальний номер кожний
        attribute_value = await page.evaluate('(element, attr) => element.getAttribute(attr)', article, attribute_name)
        if attribute_value not in unic_articles and attribute_value is not None:
            unic_articles.append(attribute_value)
            comment_input = await article.J('div[aria-label^="Напишите комментарий"]')
            comment_inputs.append(comment_input)
    print(unic_articles)  # коли більше 10 вибирається однаковий пост?
    if len(comment_inputs) > 3:
        comment_inputs = random.sample(comment_inputs, 3)
    comments = gf.define_file_category(prflname, "phrases").comments
    for inpt in comment_inputs:
        await inpt.type(f"{random.choice(comments)}\n")
        await asyncio.sleep(1)


@gf.atimer
async def reposts_mypage(prflname, browser, quantity):
    post_category = gf.define_file_category(prflname, "phrases").categories
    page = await browser.newPage()
    await page.goto(f'https://www.facebook.com/search/posts/?q={random.choice(post_category)}',
                    {"waitUntil": ['domcontentloaded', 'networkidle2']}, timeout=60000)
    await page.bringToFront()
    for i in range(random.randint(1, 5)):
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(2)
    await asyncio.sleep(5)
    # видалити пости з рекламою та залишити тільки пости з кнопкою "Поділитися"
    repost_btns = await filter_posts(page, quantity)
    await page.bringToFront()
    while quantity > 0:
        try:
            ch_repost = random.choice(repost_btns)
            await ch_repost.click()
            repost_btns.remove(ch_repost)
            await page.waitForXPath('//span[contains(text(), "Поделиться сейчас")]')
            repost_now = await page.Jx('//span[contains(text(), "Поделиться сейчас")]')
            await repost_now[0].click()
            quantity -= 1
            await asyncio.sleep(2)
        except pyppeteer.errors.ElementHandleError:
            print("ElementHandleError")
            await page.evaluate('window.scrollBy(0, -500)')
            await asyncio.sleep(1)
            repost_btns = await filter_posts(page, quantity)
        except IndexError:
            print("IndexError")
            await page.goto(f'https://www.facebook.com/search/posts/?q={random.choice(post_category)}',
                            {"waitUntil": ['domcontentloaded', 'networkidle2']}, timeout=60000)
            repost_btns = await filter_posts(page, quantity)
        except pyppeteer.errors.TimeoutError:
            print("TimeoutError")
            repost_btns = await filter_posts(page, quantity)
        await asyncio.sleep(3)
    await page.close()


async def filter_posts(page, quantity):
    posts = await page.JJ('div[role="article"]')
    repost_btns = []
    selectors = ['a[aria-label="Рекламодатель"]', 'a[aria-label="В магазин"]', 'a[aria-label="Подробнее"]',
                 'a[aria-label="Заказать"]', 'a[aria-label="Посмотреть товар"]', 'a[aria-label="Забронировать"]',
                 'a[aria-label="Узнать стоимость"]', 'a[aria-label="Подать заявку"]']
    for post in posts:
        for selector in selectors:
            with_ad = await post.J(selector)
            with_repost_btn = await post.J('div[aria-label="Отправьте это друзьям или опубликуйте в своей Хронике."]')
            if with_ad is None and with_repost_btn is not None:
                repost_btns.append(with_repost_btn)
    if len(repost_btns) > quantity:
        repost_btns = random.sample(repost_btns, quantity)
    return repost_btns


async def first_step(prflname, browser):
    await gf.gather_data(prflname, browser)
    print('НЕ ЗАБУДЬТЕ ПРОПИСАТИ ID ЛИСТА GOOGLE ТАБЛИЦІ!')
    # Додавання друзів
    num_followers = gf.getFromTable(prflname, "followers")
    num_liked_pages = gf.getFromTable(prflname, "liked_pages")
    num_friends = gf.getFromTable(prflname, "friends")
    num_groups = gf.getFromTable(prflname, "groups")
    s = await bot.get_session()
    await bot.send_message(
        my_id,
        (f"_К-ть підписників_: {num_followers}\n" if num_followers is None or num_followers < 20 else '') +
        (f"_К-ть вподобаних сторінок_: {num_liked_pages}\n" if num_liked_pages is None or num_liked_pages < 35 else '') +
        (f"_К-ть груп_: {num_groups}\n" if num_groups is None or num_groups < 12 else '') +
        f"_К-ть друзів_: {num_friends}\n" +
        f"*Скільки друзів додати?*", reply_markup=tkb.kb_qfriends, parse_mode='Markdown')
    while True:
        if gf.userbot_choice is not None:
            if int(gf.userbot_choice) != 0:
                await zahid3.add_recomended_friends(prflname, browser, int(gf.userbot_choice))
            gf.userbot_choice = None
            break
        else:
            await asyncio.sleep(1)
    # Запитуємо чи завершити роботу з профілем
    await bot.send_message(my_id, f'Продовжити 7й захід?', reply_markup=tkb.kb_yesorno)
    while True:
        if gf.userbot_choice is not None:
            if gf.userbot_choice == 'n':
                gf.userbot_choice = None
                return 'close'
            gf.userbot_choice = None
            break
        else:
            await asyncio.sleep(1)
    await s.close()


async def last_step(prflname, browser):
    # Запитуємо чи завершити роботу з профілем
    s = await bot.get_session()
    await bot.send_message(my_id, f'Закінчити 7й захід?'
                                  f'_\nНатисніть \"Ні\", щоб просто закрити {prflname}._',
                           reply_markup=tkb.kb_yesorno, parse_mode='Markdown')
    while True:
        if gf.userbot_choice is not None:
            if gf.userbot_choice == 'n':
                gf.userbot_choice = None
                return 'close'
            gf.userbot_choice = None
            break
        else:
            await asyncio.sleep(1)
    await s.close()


@gf.atimer
async def zahid7(prflname, ws):
    browser = await pyppeteer.connect({"browserWSEndpoint": ws, "defaultViewport": None})
    print('НЕ ЗАБУДЬТЕ ПРОПИСАТИ ID ЛИСТА GOOGLE ТАБЛИЦІ!')
    steps = [
             first_step(prflname, browser),             # 1
             zahid4.post_fp4(prflname, browser),        # 2
             zahid2.invite_friends(prflname, browser),  # 3
             reposts_mypage(prflname, browser, 1),      # 4
             fill_vydacha(prflname),                    # 5
             like_myfeed(prflname, browser),            # 6
             beginning_zahid(browser),                  # 7
             last_step(prflname, browser)               # 8
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


if __name__ == "__main__":
    asyncio.run(zahid7())
