import traceback
import general_functions as gf
import asyncio
import json
import time
import requests
from datetime import datetime
from zahid1 import zahid1
from zahid2 import zahid2
from zahid3 import zahid3
from zahid4 import zahid4
from zahid5 import zahid5
from zahid6 import zahid6
from zahid7 import zahid7
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton
import logging
from PIL import ImageGrab
from Helper import analize_average_time, calculate_output, prediction
from data import access_data
import re
import random
import telegram_keyboards as tkb

API_TOKEN = access_data.API_TOKEN
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
my_id = access_data.my_id  # тільки адмін може використовувати бота
port = gf.port


@gf.atimer
async def startProfile(profile_id):
    check_active = f'http://127.0.0.1:{port}/api/v1/profile/active?profileId={profile_id}'
    response1 = requests.get(check_active)
    response1 = json.loads(response1.text)
    if response1['value'] != False:
        print(f"Profile {profile_id} is active. Response: {response1}")
        return None

    url_start = f'http://127.0.0.1:{port}/api/v1/profile/start?automation=true&puppeteer=true&loadTabs=true&profileId={profile_id}'
    await asyncio.sleep(4)
    await gf.refresh_proxy()
    await asyncio.sleep(4)
    response = {"status": None}
    while response["status"] != "OK":
        response = requests.get(url_start)
        response = json.loads(response.text)
        print(response)
        if response["status"] == "ERROR":
            time.sleep(20)
    ws = response['value']
    return ws


@gf.atimer
async def stop_profile(prflname):
    my_prfls = json.loads(open("data/myPrfls.json", 'r', encoding='utf-8').read())
    profile_id = [prfl['uuid'] for prfl in my_prfls if prfl['name'] == prflname][0]
    url_stop = f'http://127.0.0.1:{port}/api/v1/profile/stop?profileId={profile_id}'
    response = requests.get(url_stop)
    response = json.loads(response.text)
    print(response)


@gf.atimer
async def main():
    gf.download_csv()
    my_prfls = json.loads(open("data/myPrfls.json", 'r', encoding='utf-8').read())
    zahods = {1: zahid1, 2: zahid2, 3: zahid3, 4: zahid4, 5: zahid5, 6: zahid6, 7: zahid7}
    for prfl in my_prfls:
        today = datetime.now().strftime('%d.%m')
        last_day = str(gf.getFromTable(prfl['name'], 'date'))# + "0"  # + 0 через помилку у гуглшітс на жовтень
        d1 = datetime.strptime(today, "%d.%m")
        try:
            d2 = datetime.strptime(last_day, "%d.%m")
        except ValueError:
            # print(f'Format of date {prfl["name"]} is not correct. Skip.')
            continue
        difference = (d1 - d2).days
        if difference < 2:
            # print(f'{prfl["name"]} already done. Skip.')
            continue

        print(prfl["name"])
        print(datetime.now().strftime('%H.%M'), prfl["name"], file=open("data/log_v0.txt", 'a', encoding='utf-8'))
        ws = await startProfile(prfl["uuid"])
        if ws is None:
            ws = prfl['ws']
        else:
            prfl.update({'ws': ws})
            with open("data/myPrfls.json", 'w', encoding='utf-8') as myPrfls_json:
                json.dump(my_prfls, myPrfls_json, indent=2, ensure_ascii=False)
            if int(gf.getFromTable(prfl['name'], 'step')) == 0:
                gf.writeInTable(prfl['name'], 'zahid', int(float(gf.getFromTable(prfl['name'], 'zahid')) + 1))
                gf.increase_step(prfl['name'])
            gf.writeInTable(prfl['name'], 'elapsed_time', time.time())
        print('-' * 100)
        zahid = int(gf.getFromTable(prfl['name'], 'zahid'))
        await asyncio.sleep(1)
        try:
            await zahods[zahid](prfl['name'], ws)
        except Exception as e:
            traceback.print_exc()
            print(e, e.args)
            time.sleep(2)
            ss_img = ImageGrab.grab(bbox=None)
            ss_img.save(r"screenshots/Error.jpg")
            return [prfl['name'], 'Error: ' + str(e)]
        t1 = time.time()
        t0 = float(gf.getFromTable(prfl['name'], 'elapsed_time'))
        elapsed_time = time.strftime("%H:%M:%S", time.gmtime(t1 - t0))
        date = datetime.now().strftime('%d.%m')
        gf.writeInCSV(prfl['name'], 'date', str(date))
        gf.writeInTable(prfl['name'], 'elapsed_time', elapsed_time)
        print('-' * 100)
    return 'Sucessfully done!'


@gf.atimer
async def go_rd_starter():
    gf.download_csv()
    my_prfls = json.loads(open("data/myPrfls.json", 'r', encoding='utf-8').read())
    go_rd_choices = json.loads(open("data/go_rd_choice.json", 'r', encoding='utf-8').read())
    print(go_rd_choices)
    chzahid = go_rd_choices["chzahid"]
    chstatus = go_rd_choices["chstatus"]
    today = datetime.now().strftime('%d.%m.%y')
    today = datetime.strptime(today, "%d.%m.%y")
    for prfl in my_prfls:
        last_day = str(gf.getFromTable(prfl['name'], 'checkRD_day'))
        try:
            last_day = datetime.strptime(last_day, "%d.%m.%y")
        except ValueError:
            pass
        if today == last_day or 'dead' in str(gf.getFromTable(prfl["name"], 'date')):
            continue
        if chzahid.startswith("from"):
            if int(chzahid[-1]) > int(gf.getFromTable(prfl["name"], "zahid")):
                continue
        elif chzahid.startswith("only"):
            if int(chzahid[-1]) != int(gf.getFromTable(prfl["name"], "zahid")):
                continue
        if chstatus == "pzrdnobm":
            if "BM_rk" in str(gf.getFromTable(prfl["name"], "BM")) \
                    or "ПЗРД" not in str(gf.getFromTable(prfl["name"], "RD")):
                continue
        elif chstatus == "nopzrdnobm":
            if "BM_rk" in str(gf.getFromTable(prfl["name"], "BM")) \
                    or "ПЗРД" in str(gf.getFromTable(prfl["name"], "RD")):
                continue
        elif chstatus == "nopzrdbm":
            if "BM_rk" not in str(gf.getFromTable(prfl["name"], "BM")) \
                    or "ПЗРД" in str(gf.getFromTable(prfl["name"], "RD")):
                continue
        print(prfl["name"])
        print(datetime.now().strftime('%H.%M'), f'GoRD {prfl["name"]}',
              file=open("data/log_v0.txt", 'a', encoding='utf-8'))
        ws = await startProfile(prfl["uuid"])
        if ws is None:
            ws = prfl['ws']
        else:
            prfl.update({'ws': ws})
            with open("data/myPrfls.json", 'w', encoding='utf-8') as myPrfls_json:
                json.dump(my_prfls, myPrfls_json, indent=2, ensure_ascii=False)
        await gf.go_rd(prfl['name'], ws)
        print('-' * 100)
    await bot.send_message(my_id, "Прохід по РД завершено ✅")

# Telegram bot
last_profile = None
last_message = None
prechoice = ""


@dp.message_handler(commands='start')
async def start_cmd_handler(message: types.Message):
    if message.from_user.id == my_id:
        await message.answer("Вітаю!", reply_markup=tkb.main_kb)
        await bot.set_my_commands(
            [types.BotCommand('stop', 'Зупинити main_task'), types.BotCommand('start', 'Оновити меню')])


@dp.message_handler(commands='stop')
async def stop_cmd_handler(message: types.Message):
    if message.from_user.id == my_id:
        success = False
        for task in asyncio.all_tasks():
            if task.get_name() == 'main_task':
                task.cancel()
                success = True
                await message.answer("Робота зупинена!", reply_markup=tkb.main_kb)
                print('Task \"main_task\" canceled!')
                break
        if not success:
            await message.answer("Немає процесу з ім\'ям \"main_task\"", reply_markup=tkb.main_kb)
            print('No task with name \"main_task\"')


@dp.message_handler(text='🔄 Оновити проксі')
async def handle_refresh_proxy(message: types.Message):
    if message.from_user.id == my_id:
        msg_delete = await message.answer('Оновлюю...')
        resp_text = await gf.refresh_proxy()
        await message.answer(f'Status refresh_proxy: {resp_text}')
        await msg_delete.delete()


@dp.message_handler(text='⏰ Прогноз закінчення')
async def handle_prediction(message: types.Message):
    if message.from_user.id == my_id:
        msg_delete = await message.answer('Обчислюю...')
        text = prediction()
        await message.answer(text, parse_mode='Markdown')
        await msg_delete.delete()


@dp.message_handler(text='🔃 Порядок проходження')
async def handle_sortion(message: types.Message):
    if message.from_user.id == my_id:
        await message.answer(message.text, reply_markup=tkb.kb_sortion)


@dp.message_handler(text='📊 Статистика')
async def statistics(message: types.Message):
    if message.from_user.id == my_id:
        msg_delete = await message.answer('Обчислюю...')
        text1 = analize_average_time()
        text2 = calculate_output()
        await message.answer(text1, parse_mode=types.ParseMode.MARKDOWN_V2)
        await message.answer(text2, parse_mode='Markdown')
        await msg_delete.delete()


@dp.message_handler(text='👁‍🗨 Що там зараз?')
async def what_now(message: types.Message):
    if message.from_user.id == my_id:
        ss_img = ImageGrab.grab(bbox=None)
        ss_img.save(r"screenshots/what_now.jpg")
        photo = open(r"screenshots/what_now.jpg", 'rb')
        await message.answer_photo(photo)
        photo.close()


@dp.message_handler(text='📝 Показати останні записи')
async def last_logs(message: types.Message):
    if message.from_user.id == my_id:
        with open("data/log_v0.txt", 'r', encoding='utf-8') as f:
            text = f.read()
        text2 = ''
        for i in text.split('\n')[-20:]:
            text2 += i + '\n'
        await message.answer(text2)


@dp.message_handler(text='🖍🆔 Прохід РД')
async def choose_go_rd(message: types.Message):
    if message.from_user.id == my_id:
        await bot.send_message(my_id, "Профілі з яким заходом обрати? (включно)", reply_markup=tkb.kb_go_rd_chzahid)


async def start_work(message):
    global last_profile
    global last_message
    task = asyncio.create_task(main(), name='main_task')
    returns = await task
    if returns == 'Sucessfully done!':
        await message.answer("Роботу успішно завершено! 👏", reply_markup=tkb.main_kb)
    elif returns[1].startswith('Error:'):
        last_profile = returns[0]
        photo = open(r"screenshots/Error.jpg", 'rb')
        caption = f"{returns[0]} {returns[1]}"
        # 1024 - максимальна довжина caption, 50 - довжина останнього рядка, який не включено в caption
        if len(caption) > 1024 - 50:
            caption = caption[:1024 - 50].encode('utf-8')
        last_message = await message.answer_photo(photo,
                                                  caption=caption + f"\n\n_Для ПЕРЕЗАПУСКУ натисніть \"▶️ Запуск\"_",
                                                  reply_markup=tkb.inwork_kb, parse_mode='Markdown')
        photo.close()


@dp.message_handler(text='▶️ Запуск')
async def begin_work(message: types.Message):
    global last_message
    if message.from_user.id == my_id:
        if last_message is not None:
            await last_message.edit_caption(caption=last_message.caption, reply_markup=None)
            last_message = None
        await message.answer('Робота пішла ...', reply_markup=tkb.main_kb)
        await start_work(message)


@dp.callback_query_handler(lambda c: c.data == 'next')
async def process_btn_next(callback_query: types.CallbackQuery):
    if callback_query.from_user.id == my_id:
        await callback_query.message.edit_caption(caption=f'{callback_query.message.caption}\n*(Закриваємо профіль)*',
                                                  reply_markup=None, parse_mode='Markdown')
        msgwait = await callback_query.message.answer('Зачекайте ...')
        kb1 = InlineKeyboardMarkup(row_width=1)
        kb1.add(InlineKeyboardButton('Підтвердити закриття профілю', callback_data='confirm_closed_profile'))
        await stop_profile(last_profile)
        await asyncio.sleep(2)
        ss_img = ImageGrab.grab(bbox=None)
        ss_img.save(r"screenshots/Closed.jpg")
        photo = open(r"screenshots/Closed.jpg", 'rb')
        await callback_query.message.answer_photo(photo, caption=f"Робота з профілем {last_profile} успішно зупинена!",
                                                  reply_markup=kb1)
        photo.close()
        await msgwait.delete()


@dp.callback_query_handler(lambda c: c.data == 'confirm_closed_profile')
async def process_btn_confirm_closed_profile(callback_query: types.CallbackQuery):
    global last_profile
    if callback_query.from_user.id == my_id:
        gf.download_csv()
        gf.writeDate(last_profile)
        last_profile = None
        await callback_query.message.answer('Робота пішла ...', reply_markup=tkb.main_kb)
        await callback_query.message.edit_caption(caption=f'{callback_query.message.caption}\n*(Профіль пропущено)*',
                                                  parse_mode='Markdown', reply_markup=None)
        await start_work(callback_query.message)


@dp.callback_query_handler(lambda c: c.data == 'skip')
async def process_btn_skip(callback_query: types.CallbackQuery):
    global last_profile
    if callback_query.from_user.id == my_id:
        gf.download_csv()
        gf.increase_step(last_profile)
        last_profile = None
        await callback_query.message.edit_caption(caption=f'{callback_query.message.caption}\n*(Пропущено крок)*',
                                                  parse_mode='Markdown')
        await start_work(callback_query.message)


@dp.callback_query_handler(lambda c: re.match(r'^yesorno', c.data))
async def process_callback_yesorno(callback_query: types.CallbackQuery):
    if callback_query.from_user.id == my_id:
        variations = {'yesorno_0': ['y', 'Так'], 'yesorno_1': ['n', 'Ні']}
        gf.userbot_choice = variations[callback_query.data][0]
        my_answer = variations[callback_query.data][1]
        await callback_query.message.edit_text(f'{callback_query.message.text}\n*Ваша відповідь: {my_answer}.*',
                                               parse_mode='Markdown')


@dp.callback_query_handler(lambda c: re.match(r'^qfriends', c.data))
async def process_callback_qfriends(callback_query: types.CallbackQuery):
    if callback_query.from_user.id == my_id:
        variations = {'qfriends_0': 0,
                      'qfriends_1': random.randint(10, 20),
                      'qfriends_2': random.randint(20, 30),
                      'qfriends_3': random.randint(30, 40),
                      'qfriends_4': random.randint(40, 50),
                      'qfriends_5': random.randint(50, 60),
                      'qfriends_6': random.randint(60, 70),
                      'qfriends_7': random.randint(70, 80)}
        gf.userbot_choice = variations[callback_query.data]
        await callback_query.message.edit_text(
            f"{callback_query.message.text}\n*Обрано додати {gf.userbot_choice} друзів.*", parse_mode='Markdown')


@dp.callback_query_handler(lambda c: re.match(r'^zahid1', c.data))
async def process_callback_zahid1(callback_query: types.CallbackQuery):
    if callback_query.from_user.id == my_id:
        variations = {'zahid1_start': 'start', 'zahid1_create_bm': 'create_bm',
                      'zahid1_trigger_rd': 'trigger_rd', 'zahid1_final': 'final'}
        gf.userbot_choice = variations[callback_query.data]


@dp.callback_query_handler(lambda c: re.match(r'^check_rd2', c.data))
async def process_callback_check_rd(callback_query: types.CallbackQuery):
    if callback_query.from_user.id == my_id:
        variations = {'check_rd2_1': 'None None ПЗРД', 'check_rd2_2': 'None None RD', 'check_rd2_3': '1BM_rk None ПЗРД',
                      'check_rd2_4': '1BM_rk ПЗРД ПЗРД', 'check_rd2_5': '1BM_rk ПЗРД None',
                      'check_rd2_6': '1BM_rk None None', 'check_rd2_7': 'BM RD ПЗРД', 'check_rd2_8': 'BM RD RD',
                      'check_rd2_9': 'BM RD None', 'check_rd2_10': 'Permanent RD', 'check_rd2_11': 'Skip'}
        gf.userbot_choice = variations[callback_query.data]
        await callback_query.message.edit_text(
            f"{callback_query.message.text}\n*Ваша відповідь: {gf.userbot_choice}.*", parse_mode='Markdown')


@dp.callback_query_handler(lambda c: re.match(r'^bm_trigger', c.data))
async def process_callback_bm_trigger(callback_query: types.CallbackQuery):
    if callback_query.from_user.id == my_id:
        variations = {'bm_trigger_1': 'trigger', 'bm_trigger_2': 'create', 'bm_trigger_3': 'skip'}
        gf.userbot_choice = variations[callback_query.data]
        await callback_query.message.edit_text(
            f"{callback_query.message.text}\n*Ваша відповідь: {gf.userbot_choice}.*", parse_mode='Markdown')


@dp.callback_query_handler(lambda c: re.match(r'^orderby', c.data))
async def process_callback_sortion(callback_query: types.CallbackQuery):
    if callback_query.from_user.id == my_id:
        order_by = callback_query.data.split("_")[1]
        reverse = True if callback_query.data.split("_")[2] == '0' else False
        icon = "🔽" if reverse is True else "🔼"
        gf.order_my_prfls(order_by, reverse=reverse)
        await callback_query.message.edit_text(f"{callback_query.message.text}\n*Відсортовано за {order_by} {icon}*",
                                               parse_mode='Markdown')


@dp.callback_query_handler(lambda c: re.match(r'^go_rd', c.data))
async def process_callback_sortion(callback_query: types.CallbackQuery):
    if callback_query.from_user.id == my_id:
        choice = callback_query.data.split("_")[-1]
        with open("data/go_rd_choice.json", "r") as go_rd_json:
            go_rd_choices = json.loads(go_rd_json.read())
        go_rd_choices[callback_query.data.split("_")[2]] = choice
        with open("data/go_rd_choice.json", "w") as go_rd_json:
            json.dump(go_rd_choices, go_rd_json, indent=2, ensure_ascii=False)
        if callback_query.data.startswith('go_rd_chzahid'):
            await callback_query.message.edit_text("По якому статусу пройдемо?", reply_markup=tkb.kb_go_rd_chstatus)
        elif callback_query.data.startswith('go_rd_chstatus'):
            await callback_query.message.edit_text("Погнали!")
            await go_rd_starter()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
