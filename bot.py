from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle
from SQLighter import SQLighter
import time
import os
import statfuncs
import random
import utils
import config
import cat

class SetCategory(StatesGroup):
    available_categories = ['все','рок','поп','современные','старые']
    waiting_for_category_name = State()
    waiting_for_name = State()



bot = Bot(config.token)
dp = Dispatcher(bot , storage=MemoryStorage())

@dp.message_handler(commands=['victorina'])
async def getvic(message: types.Message):
  argument = message.get_args()
  if argument.lower() not in SetCategory.available_categories:
      await bot.send_message(message.chat.id , "Пожалуйста, выберите категорию из списка 🎼")
      return
  if not argument:
      row = statfuncs.getrandomsong('music.db')
  if argument.lower() == 'все':
      row = statfuncs.getrandomsong('music.db')
  if argument.lower() == 'рок':
      row = statfuncs.getrandomsong('rock.db')
  if argument.lower() == 'поп':
      row = statfuncs.getrandomsong('pop.db')
  if argument.lower() == 'современные':
      row = statfuncs.getrandomsong('new.db')
  if argument.lower() == 'старые':
      row = statfuncs.getrandomsong('old.db')
  correctanswer = row[2]
  options = statfuncs.optionsforvic(row[2] , row[3])
  for i , opt in enumerate(options):
   if opt == correctanswer:
       id = i
  await bot.send_voice(message.chat.id , row[1])
  await bot.send_poll(chat_id=message.chat.id, question='Что это за песня 🎶?',
                              is_anonymous=False, options=options, type="quiz",
                              correct_option_id=id , open_period = 20)


@dp.inline_handler() # Обработчик любых инлайн-запросов
async def inlinesender(inline_query: types.InlineQuery):
    input_content = InputTextMessageContent(f'Всем привет🤗! Это бот🤖 угадай-мелодию🎶! \nЧтобы играть в группе нужно обязательно добавить➕ в неё этого бота🤖. \nЕсли бот🤖 уже в группе, введите:\n/victorina - Чтобы получить случайную песню🎶!\n/victorina категория (через пробел, на русском языке) - Чтобы получить случайную песню🎶,в желаемой категории,список доступных категорий ниже⬇:\n Доступные категории : Рок🤘,Поп👯,Старые👴🏻,Современные👩‍🎤,Все(без категории)\n/ifact - Чтобы получить интересный факт о песнях🎙 и музыкантах👨‍🎤! \nВнимание! Во время игры в группах индивидуальная статистика📈 не учитывается :(\nЕсли хотите играть с учетом статистики📈, добро пожаловать👉 в личные сообщения к боту🤖 :)' )
    item = InlineQueryResultArticle(
        id = 1,
        title='У бота есть возможность игры в группе, нажми для подробностей',
        input_message_content=input_content,

    )
    await bot.answer_inline_query(inline_query.id, results=[item],cache_time = 600)

@dp.message_handler(commands = ['setcategory'],state='*')
async def setcategory_1(message: types.Message):
    morkup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    btn1 = types.KeyboardButton('Все')
    btn2 = types.KeyboardButton('Рок 🤘')
    btn3 = types.KeyboardButton('Поп 👯')
    btn4 = types.KeyboardButton('Современные 👩‍🎤')
    btn5 = types.KeyboardButton('Старые 👴🏻')
    morkup.add(btn1, btn2 ,btn3 ,btn4 ,btn5)
    await bot.send_message(message.from_user.id, 'Выберите категорию',reply_markup=morkup)
    await SetCategory.waiting_for_category_name.set()

@dp.message_handler(state=SetCategory.waiting_for_category_name, content_types=types.ContentTypes.TEXT)
async def setcategory_2(message: types.Message , state: FSMContext):
    if message.text.lower() not in SetCategory.available_categories:
        await bot.send_message(message.from_user.id ,"Пожалуйста, выберите категорию, используя клавиатуру ниже ⬇.")
        return
    if message.text.lower() == 'все':
        statfuncs.savecategory('music.db', message.from_user.id)
    if message.text.lower() == 'рок 🤘':
        statfuncs.savecategory('rock.db', message.from_user.id)
    if message.text.lower() == 'поп 👯':
        statfuncs.savecategory('pop.db', message.from_user.id)
    if message.text.lower() == 'современные 👩‍🎤':
        statfuncs.savecategory('new.db', message.from_user.id)
    if message.text.lower() == 'старые 👴🏻':
        statfuncs.savecategory('old.db', message.from_user.id)
    morkup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    btn1 = types.KeyboardButton('Играть еще 😄')
    btn2 = types.KeyboardButton('Стоп 🛑')
    morkup.add(btn1, btn2)
    await bot.send_message(message.from_user.id ,"Категория успешно сохранена 👌" ,reply_markup=morkup)
    await state.finish()


@dp.message_handler(commands=['start'])
async def game(message: types.Message):
    # Подключаемся к БД
    if (statfuncs.currentansreturner(message.from_user.id)[0]) != 3 and (statfuncs.currentansreturner(message.from_user.id)[0]) != 8:
     db_worker = SQLighter(cat.catreturner(message.from_user.id))
    # Получаем случайную строку из БД
     row = db_worker.select_single(random.randint(1, db_worker.count_rows()))
    # Формируем разметку
     markup = utils.generate_markup(row[2], row[3])
    # Отправляем аудиофайл с вариантами ответа
     await bot.send_voice(message.from_user.id, row[1], reply_markup=markup)
    # Включаем "игровой режим"
     utils.set_user_game(message.from_user.id, row[2])
    # Отсоединяемся от БД
     db_worker.close()
    else:
        await singerchoose(message)

@dp.message_handler(commands=['singer'])
async def singerchoose(message: types.Message):
    # Подключаемся к БД
    db_worker = SQLighter(config.database_name4)
    # Получаем случайную строку из БД
    row = db_worker.select_single(random.randint(1, db_worker.count_rows()))
    # Формируем разметку
    markup = utils.generate_markup(row[2], row[3])
    # Отправляем фото с вариантами ответа
    await bot.send_message(message.from_user.id, 'Угадай исполнителя!')
    await bot.send_photo(message.from_user.id, row[1], reply_markup=markup)
    # Включаем "игровой режим"
    utils.set_user_game(message.from_user.id, row[2])
    # Отсоединяемся от БД
    db_worker.close()


@dp.message_handler(commands=['reset'])
async def reset(message: types.Message):
 statfuncs.resetstats(message.from_user.id)

@dp.message_handler(commands=['top'])
async def printtop(message: types.Message):
    tplst = statfuncs.statsreturner(message.from_user.id)
    await bot.send_message(message.from_user.id, f'{tplst[0][0]} (Вы) - {tplst[0][1]} очков.')
    for n,i in enumerate(tplst[1:]):
        await bot.send_message(message.from_user.id , f'{n+1}. {list(i)[0]} - {list(i)[1]} очков.')

@dp.message_handler(commands=['dailytop'])
async def printtop(message: types.Message):
    tplst = statfuncs.dailystatsreturner(message.from_user.id)
    await bot.send_message(message.from_user.id, f'{tplst[0][0]} (Вы) - {tplst[0][1]} очков.')
    for n,i in enumerate(tplst[1:]):
        await bot.send_message(message.from_user.id , f'{n+1}. {list(i)[0]} - {list(i)[1]} очков.')

'''
@dp.message_handler(commands=['test'])
async def find_file_ids(message):
    path = 'newmusic/'
    files = sorted(os.listdir(path), key=lambda x: os.path.getctime(os.path.join(path, x)))
    for file in files:
            print(file)
            f = open('newmusic/'+file, 'rb')
            msg = await bot.send_voice(message.from_user.id, f, None)
            await bot.send_message(message.from_user.id, msg.voice.file_id, reply_to_message_id=msg.message_id) #Для фото msg.photo[-1].file_id, для песен msg.voice.file_id
    time.sleep(3)
'''

@dp.message_handler(commands=['ifact'])
async def ifacts(message: types.Message):
 rsp = list(random.choice(statfuncs.getinfacts()))
 media = types.MediaGroup()
 media.attach_photo(rsp[0] , rsp[1])
 await bot.send_message(message.chat.id, 'Интересный факт: ⬇')
 await bot.send_media_group(message.chat.id, media=media)


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await bot.send_message(message.chat.id, 'Доступные команды бота 🤖:\nВведите /start чтобы начать играть!\nВведите /setcategory чтобы изменить категорию песен 🎶!\nВведите /reset чтобы сбросить статистику 📈!\nВведите /top чтобы увидеть список лидеров 👑 за всё время!\nВведите /dailytop чтобы увидеть ежедневный список лидеров 👸!\nВведите /ifact чтобы увидеть интересные факты 📖!\nВведите /setname чтобы изменить ваш никнейм 📝\nТакже есть возможность игры в группах 👥!\nДля этого обязательно добавление бота 🤖 в группу.\nДля получения полной информации 💁 напишите:\n"@SuddensBot любой текст" (Инлаин-режим)')

@dp.message_handler(commands=['setname'] , state='*')
async def nickchange(message: types.Message):
    await bot.send_message(message.from_user.id, 'Введите новое имя ✍')
    await SetCategory.waiting_for_name.set()

@dp.message_handler(state=SetCategory.waiting_for_name, content_types=types.ContentTypes.TEXT)
async def changenick(message : types.Message , state: FSMContext):
    statfuncs.nickchanger(message.from_user.id, message.text)
    await bot.send_message(message.from_user.id, "Имя успешно сохранено 📝")
    await state.finish()

@dp.message_handler()
async def check_answer(message: types.Message):
    # Если функция возвращает None -> Человек не в игре
    answer = utils.get_answer_for_user(message.from_user.id)
    if message.text == 'Играть еще 😄':
      return await game(message)
    # Как Вы помните, answer может быть либо текст, либо None
    # Если None:
    if not answer:
        await bot.send_message(message.from_user.id, 'Чтобы начать игру, введите команду /start')
    else:
        morkup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        btn1 = types.KeyboardButton('Играть еще 😄')
        btn2 = types.KeyboardButton('Стоп 🛑')
        morkup.add(btn1, btn2)
        # Если ответ правильный/неправильный
        if message.text == answer:
           await bot.send_message(message.from_user.id, 'Верно 🎉!', reply_markup=morkup)
           sp = statfuncs.scoreupdater(message.from_user.id, message.from_user.username,True)
           if sp[4] > 2:
            await bot.send_message(message.from_user.id , f'🎊 Вы отгадали уже {sp[4]} песен подряд ! Вы получаете больше очков! 🎊')
           await bot.send_message(message.from_user.id, f'Ваша статистика 📈:\nСчет: {sp[1]}\nОтгадано✅: {sp[2]}\nНе отгадано❎: {sp[3]}')

        else:
           await bot.send_message(message.from_user.id, 'Увы, Вы не угадали. Попробуйте ещё раз!', reply_markup=morkup)
           sp = statfuncs.scoreupdater(message.from_user.id,message.from_user.username,False)
           await bot.send_message(message.from_user.id, f'Ваша статистика 📈:\nСчет: {sp[1]}\nОтгадано✅: {sp[2]}\nНе отгадано❎: {sp[3]}')
        # Удаляем юзера из хранилища (игра закончена)
        if sp[6] == 10:
            await ifacts(message)
        utils.finish_user_game(message.from_user.id)



if __name__ == '__main__':
        random.seed()
        executor.start_polling(dp)