import requests  # запросы pip install requests
import urllib.request  # запросы
from urllib.request import urlopen  # запросы
import telebot  # для бота pip install pytelegrambotapi
import re  # для поиска в строках
from telebot import types
from telebot.types import Message  
import os, sys, traceback  # для работы с операционкой
import time  # время
import psutil  # для получения статуса служб
from datetime import datetime  # дата
from multiprocessing import Process  # для создания двух потоков
import shutil  # работа с файлами
import constants as cons  # файл с переменными


bot = telebot.TeleBot(cons.TOKEN, threaded=False)


#------------------------------------------------------------------- Comands ---------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def get_start(message: Message):
    """ Функция отправляет приветствие пользователю """

    bot.send_message(message.from_user.id, text='Здравствуйте, выполните команду /help для ознакомление с моими функциями')
    bot.send_message(cons.admin, text=f'Пользователь {message.from_user.first_name} {message.from_user.last_name},\nid - {message.from_user.id}\nВыполнил команду start')


@bot.message_handler(commands=['help'])
def get_help(message: Message):
    """ Функция отправляет пользователю список доступных команд """

    bot.send_message(message.from_user.id, text=cons.unsver_help)


@bot.message_handler(commands=['start_service'])
def start_service_0(message: Message):
    try:
        if message.from_user.id in cons.users:
            if 1 in cons.backup_status.values():  # Проверка, делается ли сейчас бекап
                raise Exception()
            key = types.ReplyKeyboardMarkup()
            key.row("Да","Нет")
            key.one_time_keyboard = True
            key.resize_keyboard = True
            msg = bot.send_message(message.from_user.id, text='Точно хотите запустить службу?', reply_markup=key)
            bot.register_next_step_handler(msg, start_service)
        else:
            bot.send_message(message.from_user.id, text=cons.get_ansver())
    except Exception as e:
        bot.send_message(message.from_user.id, text=f'Сейчас делается бекапчик, подождите,\n\nError: {e}')


def start_service(message: Message):
    """ Функция для запуска службы """

    if message.from_user.id in cons.users:
        if message.text == 'Да':
            os.system('net start ZvitGrp')
            service = get_service()
            if service[1] == 'Выполняется':
                bot.send_message(message.from_user.id, text=f"Служба {service[0]} - '{service[1]}', все четко", reply_markup=types.ReplyKeyboardRemove())
            else:
                bot.send_message(message.from_user.id, text=f"Служба {service[0]} не запустилась, шо-то не так", reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(cons.admin, text=cons.unsver_only_for_admin(message, start_service.__name__), reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.from_user.id, text=f"Отмена", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.from_user.id, text=cons.get_ansver(), reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['stop_service'])
def stop_service_0(message: Message):
    try:
        if message.from_user.id in cons.users:
            if 1 in cons.backup_status.values():  # Проверка, делается ли сейчас бекап
                raise Exception()
            key = types.ReplyKeyboardMarkup()
            key.row("Да","Нет")
            key.one_time_keyboard = True
            key.resize_keyboard = True
            msg = bot.send_message(message.from_user.id, text='Точно хотите остановить службу?', reply_markup=key)
            bot.register_next_step_handler(msg, stop_service)
        else:
            bot.send_message(message.from_user.id, text=cons.get_ansver())
    except Exception as e:
        bot.send_message(message.from_user.id, text=f'Сейчас делается бекапчик, подождите')


def stop_service(message: Message):
    """ Функция для останоки службы """

    if message.from_user.id in cons.users:
        if message.text == 'Да':
            os.system('net stop ZvitGrp')
            service = get_service()
            if service[1] == 'Остановлена':
                bot.send_message(message.from_user.id, text=f"Служба {service[0]} - '{service[1]}', все четко", reply_markup=types.ReplyKeyboardRemove())
            else:
                bot.send_message(message.from_user.id, text=f"Служба {service[0]} не остановилась, шо-то не так", reply_markup=types.ReplyKeyboardRemove())
                bot.send_message(cons.admin, text=cons.unsver_only_for_admin(message, stop_service.__name__), reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.from_user.id, text=f"Отмена", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.from_user.id, text=cons.get_ansver())


@bot.message_handler(commands=['chek_update'])
def chek_update(message):
    """ Функция для проверки наличия обновленя программы на сайте """

    if message.from_user.id in cons.users:
        spisok = go_poparsim()  # получаем список где spisok[0] - ссылка на скачку обновления, spisok[1] - версия. которая должна быть установлена, spisok[2] - новая версия программы
        version = get_last_link()  # получаем версию (строку) с установленной у нас программой
        if version == spisok[0]:
            bot.send_message(message.from_user.id, text=f"Новой версии пока нет,\n"
                                                        f"сейчас установлена - '{spisok[2]}'")
        else:
            bot.send_message(message.from_user.id, text=f"вот ссыль на обнову - {spisok[0]}\n\n"
                                                        f"Сейчас установлена - '{spisok[1]}'\n"
                                                        f"Новая версия - '{spisok[2]}'")
    else:
        bot.send_message(message.from_user.id, text=cons.get_ansver())


@bot.message_handler(commands=['info'])
def get_info(message: Message):
    """ Функция выводит информацию о службе (Выполняется/Остановлена)
    еще выводит колличество свободного места на диске, где хранятся бекапы"""

    if message.from_user.id in cons.users:
        service = get_service()  # получаем список с состоянием службы где service[0] - имя службы, а service[1] - её состояние (выполняется/Остановлена)
        x = psutil.disk_usage(cons.path_for_chk_space)  # получаем кортеж с состоянием диска где x[2] - свободное место на диске в байтах
        bot.send_message(message.from_user.id, text=(f"... bot активен\n"
                                                     f"... '{service[0]}' - '{service[1]}'\n"
                                                     f"... свободно на диске {round(int(x[2])/ 2**30, 2)} гиг"))
    else:
        bot.send_message(message.from_user.id, text=cons.get_ansver())


@bot.message_handler(commands=['here'])
def write_last_link(message):
    """ Получаем версию установленной программы """

    link = go_poparsim()
    sep = os.sep
    with open(f"***", 'w') as file_handler:
        file_handler.write(link[0])
    bot.send_message(message.from_user.id, text='Ладно, замолкаю')


@bot.message_handler(commands=['zero'])
def get_zero(message: Message):
    cons.backup_status[message.from_user.id] = 0

#------------------------------------------------------- Сделать бекапчик перед обновлением ------------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['backup'])
def get_backup(message):
    """ Функция инициализирует процесс бекапа
     еще проверяет не делает ли сейчас кто-то бекап """

    try:
        if message.from_user.id in cons.users:
            if 1 in cons.backup_status.values():  # Проверка, делается ли сейчас бекап
                raise Exception()
            msg = bot.send_message(message.from_user.id, text='Вы подтверждаете, что хотите сделать backup?')
            bot.register_next_step_handler(msg, get_verification)
        else:
            bot.send_message(message.from_user.id, text=cons.get_ansver())
    except Exception:
        bot.send_message(message.from_user.id, text='Сейчас уже делается бекапчик')


def get_verification(message):
    """ Функция проверяет подтверждение на старт бекапа"""

    try:
        uns = message.text
        if uns in ['Подтверждаю', 'подтверждаю', 'Да', 'да', 'давай уже', 'реще']:
            bot.send_message(message.from_user.id, text='Подтверждено')
            cons.backup_status[message.from_user.id] = 1
            do_backup(message)
        else:
            bot.send_message(message.from_user.id, text='Отмена')
    except Exception as e:
        bot.reply_to(message, f'oooops\n\nError: {e}')

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------------------------------- Сделать бекапчик ------------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['backup_old'])
def get_backup_old(message):
    """ Функция инициализирует процесс бекапа
     еще проверяет не делает ли сейчас кто-то бекап """

    try:
        if message.from_user.id in cons.users:
            if 1 in cons.backup_status.values():  # Проверка, делается ли сейчас бекап
                raise Exception()
            msg = bot.send_message(message.from_user.id, text='Вы подтверждаете, что хотите сделать backup?')
            bot.register_next_step_handler(msg, get_verification_old)
        else:
            bot.send_message(message.from_user.id, text=cons.get_ansver())
    except Exception:
        bot.send_message(message.from_user.id, text='Сейчас уже делается бекапчик')


def get_verification_old(message):
    """ Функция проверяет подтверждение на старт бекапа
     еще проверяет не делает ли сейчас кто-то бекап """

    try:
        uns = message.text
        if uns in ['Подтверждаю', 'подтверждаю', 'Да', 'да', 'давай уже', 'реще']:
            bot.send_message(message.from_user.id, text='Подтверждено')
            cons.backup_status[message.from_user.id] = 1
            do_backup_old(message)
        else:
            bot.send_message(message.from_user.id, text='Отмена')
    except Exception as e:
        bot.reply_to(message, f'oooops\n\nError: {e}')

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------------------------------- Удаление ----------------------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['delete'])
def get_dell(message):
    """ Функция удаляет """

    try:
        if message.from_user.id in cons.users:
            if 1 in cons.backup_status.values():  # Проверка, делается ли сейчас бекап
                raise Exception()
            key = types.ReplyKeyboardMarkup()
            markup = os.listdir(cons.target_dir)
            for i in markup:
                key.row(i)
            key.row('Отмена')
            key.one_time_keyboard = True
            key.resize_keyboard = True
            msg = bot.send_message(message.from_user.id, text='Что из этого нужно удалить?', reply_markup=key)
            bot.register_next_step_handler(msg, get_dell_fin)
        else:
            bot.send_message(message.from_user.id, text=cons.get_ansver())
    except Exception as e:
        bot.send_message(message.from_user.id, text=f'Сейчас делается бекапчик, подождите,\n\nError: {e}')


def get_dell_fin(message):
    """ Функция удаляет """

    try:
        if message.text == 'Отмена':
            bot.send_message(message.chat.id, "Отмена удаления", reply_markup=types.ReplyKeyboardRemove())
        else:
            shutil.rmtree(cons.target_dir+rf'\{message.text}')
            bot.send_message(message.chat.id, "Удалено", reply_markup=types.ReplyKeyboardRemove())

    except Exception as e:
        bot.reply_to(message, f'oooops\n\nError: {e}', reply_markup=types.ReplyKeyboardRemove())

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#------------------------------------------------------------------- Functions ---------------------------------------------------------------------------------------------------------

def do_backup(message):
    """ Функция начинает делать бекап """
    try:
        os.system('net stop ZvitGrp')
    
        today = cons.target_dir+os.sep+time.strftime('%Y.%m.%d')  # Текущая дата служит именем подкаталога в основном каталоге
        ver = go_poparsim()  # получаем версию установленной программы
        dirrr = today+"_"+ver[1]
    
        if not os.path.exists(dirrr):  # Создаём каталог, если его ещё нет
            os.mkdir(dirrr)  # создание каталога
    
            one = dirrr+"\\***"
            os.mkdir(one)  # создание каталога
    
            two = dirrr+"\\***"
            os.mkdir(two)  # создание каталога
    
        bot.send_message(message.from_user.id, text='Начинаем копировать базы, это займет некоторое время. По окончании пришлю сообщение')
        if shutil.copy(cons.iskra_dir, one) == one+r'\ZVIT.FDB':
            bot.send_message(message.from_user.id, text=f"Резервная копия 1 успешно создана.\nПереходим к комбинату питания")
        if shutil.copy(cons.kp_dir, two) == two+r'\ZVIT.FDB':
            bot.send_message(message.from_user.id, text=f"Резервная копия 2 успешно создана.\nОтличная работа 👍, хорошего дня 😊")
        cons.backup_status[message.from_user.id] = 0
        os.system('net start ZvitGrp')
    except Exception as e:
        bot.send_message(cons.admin, text=f'oooops\nПользователь {message.from_user.first_name} {message.from_user.last_name}\n\nError: {e}')


def do_backup_old(message):
    """ Функция начинает делать бекап """
    try:
        os.system('net stop ZvitGrp')
    
        today = cons.target_dir+os.sep+time.strftime('%Y.%m.%d')  # Текущая дата служит именем подкаталога в основном каталоге
        ver = go_poparsim()  # получаем версию установленной программы
        dirrr = today+"_"+ver[2]
    
        if not os.path.exists(dirrr):  # Создаём каталог, если его ещё нет
            os.mkdir(dirrr)  # создание каталога
    
            one = dirrr+"\\***"
            os.mkdir(one)  # создание каталога
    
            two = dirrr+"\\***"
            os.mkdir(two)  # создание каталога
    
        bot.send_message(message.from_user.id, text='Начинаем копировать базы, это займет некоторое время. По окончании пришлю сообщение')
        if shutil.copy(cons.iskra_dir, one) == one+r'\ZVIT.FDB':
            bot.send_message(message.from_user.id, text=f"Резервная копия искры успешно создана.\nПереходим к комбинату питания")
        if shutil.copy(cons.kp_dir, two) == two+r'\ZVIT.FDB':
            bot.send_message(message.from_user.id, text=f"Резервная копия кобината питания успешно создана.\nОтличная работа 👍, хорошего дня 😊")
        cons.backup_status[message.from_user.id] = 0
        os.system('net start ZvitGrp')
    except Exception as e:
        bot.send_message(cons.admin, text=f'oooops\nПользователь {message.from_user.first_name} {message.from_user.last_name}\n\nError: {e}')


def get_last_link():
    """ Получаем версию установленной программы """

    sep = os.sep
    with open(f"***", 'r') as file_handler:
        link = file_handler.read()
    return link


def go_poparsim():
    """ С сайта программы вытаскиваем полследнюю ссылку на обновление """

    website = urlopen('https://medoc.ua/uk/download')
    html = website.read()
    links = re.findall('https://load.medoc.ua/update/ezvit.[0123456789.-]*zip', str(html))
    lust_update_link = links[0]
    x = re.findall('ezvit.([0123456789.-]*).zip', lust_update_link)
    y = x[0].split('-')
    old_ver = y[0]
    new_ver = y[1]    
    return [lust_update_link, old_ver, new_ver]


def get_service():
    """ Функция проверяет статус службы на данный момент (Выполняется/Остановлена) """

    s = psutil.win_service_get('ZvitGrp')  # Получаем инфу о службе, для теста используется Диспетчер печати
    x = s.as_dict()['display_name']  # Вытаскиваем из словаря как служба называется для пользователя
    y = s.as_dict()['status']  # Вытаскиваем из словаря состояние службы
    if y == 'running':
        y = 'Выполняется'
    elif y == 'stopped':
        y = 'Остановлена'
    return [x, y]


def period_check_update():
    """ Функция проверки наличия новой версии, повторяется каждый час """

    while True:
        last_link = get_last_link()  # получаем версию установленной программы
        updete = go_poparsim()
        if last_link != updete[0]:
            bot.send_message(cons.admin, f'WARNING-WARNING-WARNING\n\nПоявилась обнова - {updete[2]}\n\n{updete[0]}\n\nШоб я не пиликал нужно выполнить /here')
        time.sleep(3600)  # 1 час


def start1():
    """ Функция для запуска period_check_update()
    в случае ошибки повторяем перезапускаем функцию через 15 секунд """

    while True:
        try:
            period_check_update()
        except Exception as e:
            bot.send_message(cons.admin, text=f'Поток с функцией period_check_updare чет упал\nError: {e}\nща перезапустим')
            time.sleep(60)


if __name__ == '__main__':
    Process(target=start1).start()

    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            with open(f"***", 'a') as file_errors:
                file_errors.write(e + '\n\n')
            time.sleep(60)
        