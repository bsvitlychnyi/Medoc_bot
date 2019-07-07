import random


def get_ansver():
	return random.choice(unsver_acsces_denied) 


def unsver_only_for_admin(message, func):
	unsver = f'Пользователь {message.from_user.first_name} {message.from_user.last_name}, с id - {message.from_user.id}, получил ошибку в функции {func}'
	return unsver


TOKEN = '***'  # Токен бота

admin = ***  # id админа
users = (admin, )  # id пользователей, которые имеют доступ

backup_status = {}.fromkeys([admin, ], 0)  # Словарь, для хранения статуса бекапа

path_for_chk_space = r'E:\\'  # Диск у которого проверять свободное место

target_dir = r'***'  # Путь, куда будут сохраняться бекапы.

iskra_dir = r'***'  # Путь, к базе искры
kp_dir = r'***'  # Путь, к базе комбината питания


unsver_help = ('/backup : запускает процесс бекапа, необходимо следовать подсказкам;\n'
               '/info : информация о боте, работе службы, версии программы\n'
               '/version : установка актуальной версии программы\n'
               '/zero : сброс одного важного параметра, при необходимости выполнения появится подсказка\n'
               '/startService : запускает службу ZvitGrp\n'
               '/stopService : останавливает службу ZvitGrp')


unsver_acsces_denied = ["Извините, но вы не входите узкий круг людей, которым позволено это делать",
						 "Шо ты хочешь дядя, иди прогуляйся",
						 'Извините, у вас нет доступа к этой фунции']
