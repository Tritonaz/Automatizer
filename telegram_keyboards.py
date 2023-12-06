from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# simple_main_starter.py
# Головне меню
main_buttons = [
    KeyboardButton('▶️ Запуск'),
    KeyboardButton('👁‍🗨 Що там зараз?'),
    KeyboardButton('🔃 Порядок проходження'),
    KeyboardButton('🖍🆔 Прохід РД'),
    KeyboardButton('⏰ Прогноз закінчення'),
    KeyboardButton('🔄 Оновити проксі'),
    KeyboardButton('📊 Статистика'),
    KeyboardButton('📝 Показати останні записи')]
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(*main_buttons)

# Пуск
inwork_kb = InlineKeyboardMarkup(row_width=1)
inwork_kb.add(
    InlineKeyboardButton('⏩ Пропустити крок і продовжити', callback_data='skip'),
    InlineKeyboardButton('⏭ Продовжити з наступного профілю', callback_data='next'))

# zahid7.py Кількість друзів
kb_qfriends = InlineKeyboardMarkup(row_width=4)
kb_qfriends.add(
    InlineKeyboardButton('0', callback_data='qfriends_0'),
    InlineKeyboardButton('10-20', callback_data='qfriends_1'),
    InlineKeyboardButton('20-30', callback_data='qfriends_2'),
    InlineKeyboardButton('30-40', callback_data='qfriends_3'),
    InlineKeyboardButton('40-50', callback_data='qfriends_4'),
    InlineKeyboardButton('50-60', callback_data='qfriends_5'),
    InlineKeyboardButton('60-70', callback_data='qfriends_6'),
    InlineKeyboardButton('70-80', callback_data='qfriends_7'))

# Так або Ні
kb_yesorno = InlineKeyboardMarkup(row_width=2)
kb_yesorno.add(
    InlineKeyboardButton('Так', callback_data='yesorno_0'),
    InlineKeyboardButton('Ні', callback_data='yesorno_1'))

# zahid1.py
# Вибір типу роботи
kb_zahid1 = InlineKeyboardMarkup(row_width=2)
kb_zahid1.add(
    InlineKeyboardButton('Старт', callback_data='zahid1_start'),
    InlineKeyboardButton('Закінчити', callback_data='zahid1_final'),
    InlineKeyboardButton('З fbaccio трігернути РД', callback_data='zahid1_create_bm'),
    InlineKeyboardButton('З консолі трігернути РД', callback_data='zahid1_trigger_rd'))

# check_accountquality2
kb_check_rd2 = InlineKeyboardMarkup(row_width=3)
kb_check_rd2.add(
    InlineKeyboardButton('None None ПЗРД', callback_data='check_rd2_1'),
    InlineKeyboardButton('None None RD', callback_data='check_rd2_2'),
    InlineKeyboardButton('1BM_rk None ПЗРД', callback_data='check_rd2_3'),
    InlineKeyboardButton('1BM_rk ПЗРД ПЗРД', callback_data='check_rd2_4'),
    InlineKeyboardButton('1BM_rk ПЗРД None', callback_data='check_rd2_5'),
    InlineKeyboardButton('1BM_rk None None', callback_data='check_rd2_6'),
    InlineKeyboardButton('BM RD ПЗРД', callback_data='check_rd2_7'),
    InlineKeyboardButton('BM RD RD', callback_data='check_rd2_8'),
    InlineKeyboardButton('BM RD None', callback_data='check_rd2_9'),
    InlineKeyboardButton('Permanent RD', callback_data='check_rd2_10'),
    InlineKeyboardButton('Skip', callback_data='check_rd2_11'))

# options create bm
kb_bm_trigger = InlineKeyboardMarkup(row_width=3)
kb_bm_trigger.add(
    InlineKeyboardButton('trigger', callback_data='bm_trigger_1'),
    InlineKeyboardButton('create', callback_data='bm_trigger_2'),
    InlineKeyboardButton('skip', callback_data='bm_trigger_3'))

# сортування проходження
kb_sortion = InlineKeyboardMarkup(row_width=2)
kb_sortion.add(
    InlineKeyboardButton("За номером 🔽", callback_data='orderby_idname_0'),
    InlineKeyboardButton("За номером 🔼", callback_data='orderby_idname_1'),
    InlineKeyboardButton("За заходом 🔽", callback_data='orderby_zahid_0'),
    InlineKeyboardButton("За заходом 🔼", callback_data='orderby_zahid_1'),
    InlineKeyboardButton("За кроками 🔽", callback_data='orderby_step_0'),
    InlineKeyboardButton("За кроками 🔼", callback_data='orderby_step_1'),
    InlineKeyboardButton("За РД статусом 🔽", callback_data='orderby_RD_0'),
    InlineKeyboardButton("За РД статусом 🔼", callback_data='orderby_RD_1'))

# go_rd
kb_go_rd_chzahid = InlineKeyboardMarkup(row_width=2)
kb_go_rd_chzahid.add(
    InlineKeyboardButton("Всі від 1-го", callback_data='go_rd_chzahid_from1'),
    InlineKeyboardButton("Тільки з 1-м", callback_data='go_rd_chzahid_only1'),
    InlineKeyboardButton("Всі від 2-го", callback_data='go_rd_chzahid_from2'),
    InlineKeyboardButton("Тільки з 2-м", callback_data='go_rd_chzahid_only2'),
    InlineKeyboardButton("Всі від 3-го", callback_data='go_rd_chzahid_from3'),
    InlineKeyboardButton("Тільки з 3-м", callback_data='go_rd_chzahid_only3'),
    InlineKeyboardButton("Всі від 4-го", callback_data='go_rd_chzahid_from4'),
    InlineKeyboardButton("Тільки з 4-м", callback_data='go_rd_chzahid_only4'),
    InlineKeyboardButton("Всі від 5-го", callback_data='go_rd_chzahid_from5'),
    InlineKeyboardButton("Тільки з 5-м", callback_data='go_rd_chzahid_only5'),
    InlineKeyboardButton("Всі від 6-го", callback_data='go_rd_chzahid_from6'),
    InlineKeyboardButton("Тільки з 6-м", callback_data='go_rd_chzahid_only6'),
    InlineKeyboardButton("Тільки з 7-м", callback_data='go_rd_chzahid_only7'))

kb_go_rd_chstatus = InlineKeyboardMarkup(row_width=1)
kb_go_rd_chstatus.add(
    InlineKeyboardButton("ПЗРД без БМ", callback_data='go_rd_chstatus_pzrdnobm'),
    InlineKeyboardButton("Не ПЗРД без БМ", callback_data='go_rd_chstatus_nopzrdnobm'),
    InlineKeyboardButton("Не ПЗРД з БМ", callback_data='go_rd_chstatus_nopzrdbm'))


