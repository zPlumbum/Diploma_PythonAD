import vk_api
from random import randrange
from vk_bot import VkBot
from vk_DB import DbWorker, DB_path
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

# Токен Вк-группы, от лица которой будет писать бот.
group_token = input('Group token: ')
# Токен любого пользователя Вк, он нужен для поиска людей, так как по токену группы этого сделать нельзя.
bot_token = input('Bot token: ')

vk_session = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk_session)
vk_bot = VkBot(bot_token)
db_worker = DbWorker(DB_path)


def write_message(user_id, message, attachment=None, keyboard=None):
    vk_session.method(
        'messages.send',
        {
            'user_id': user_id,
            'message': message,
            'random_id': randrange(10 ** 7),
            'attachment': attachment,
            'keyboard': keyboard
        }
    )


def create_keyboard(request, one_time):
    keyboard = VkKeyboard(one_time=one_time)

    if request == '/команды' or request == 'в начало' or request == 'завершить' or request == 'начать':
        keyboard.add_button('Найти пару', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Показать понравившихся людей', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Показать черный список', color=VkKeyboardColor.NEGATIVE)

    elif request == 'неверные данные':
        keyboard.add_button('Завершить', color=VkKeyboardColor.PRIMARY)

    elif request == 'найти пару':
        keyboard.add_button('Довериться боту', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Указать параметры поиска', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('В начало', color=VkKeyboardColor.PRIMARY)

    elif request == 'понравился':
        keyboard.add_button('Да, мне кто-то понравился', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Неа, никто не понравился', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Добавить человека в черный список', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('В начало', color=VkKeyboardColor.PRIMARY)

    elif request == 'еще понравился':
        keyboard.add_button('Добавить еще одного человека', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Завершить', color=VkKeyboardColor.PRIMARY)

    elif request == 'еще добавить в чс':
        keyboard.add_button('Добавить человека в понравившихся', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Добавить человека в черный список', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('Завершить', color=VkKeyboardColor.PRIMARY)

    elif request == 'еще удалить из чс':
        keyboard.add_button('Удалить человека из черного списка', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('В начало', color=VkKeyboardColor.PRIMARY)

    elif request == 'показать черный список':
        keyboard.add_button('Удалить человека из черного списка', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('В начало', color=VkKeyboardColor.PRIMARY)

    else:
        keyboard.add_button('/команды', color=VkKeyboardColor.POSITIVE)

    keyboard = keyboard.get_keyboard()
    return keyboard


def start_vk_longpoll():
    dialog_exists = False
    find_pair_bool = False
    is_liked = False
    add_to_blacklist = False
    delete_from_blacklist = False
    parameters_exist = False

    found_people = []

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                try:
                    print('Текст сообщения:', event.text)
                    print(f'Отправитель: {event.user_id}\n')
                    request = event.text.lower()

                    if request == 'начать':
                        write_message(
                            event.user_id,
                            '''Привет! Я бот, который помогает людям найти свою вторую половинку.
                            Вот список команд, которые я могу выполнить:
                            1) Найти тебе пару 💘
                            2) Показать понравившихся людей 😍
                            3) Показать людей из черного списка 🚫''',
                            keyboard=create_keyboard('/команды', True)
                        )

                    elif request == 'пока':
                        write_message(event.user_id, 'Пока-пока! Если что, обращайся!')

                        dialog_exists = False
                        find_pair_bool = False
                        is_liked = False
                        add_to_blacklist = False
                        delete_from_blacklist = False
                        parameters_exist = False
                        found_people = []

                    elif request == 'в начало' and dialog_exists:
                        write_message(event.user_id, 'Понял, давай попробуем еще раз.', keyboard=create_keyboard('в начало', True))

                        dialog_exists = False
                        find_pair_bool = False
                        is_liked = False
                        add_to_blacklist = False
                        delete_from_blacklist = False
                        parameters_exist = False
                        found_people = []

                    elif request == 'завершить':
                        write_message(
                            event.user_id,
                            '''Не забудь написать понравившимся людям. Надеюсь, у вас все получится!😉
                            А для того, чтобы вспомнить, кто тебе понравился, ты можешь нажать кнопку "Показать понравившихся людей"''',
                            keyboard=create_keyboard('завершить', True)
                        )

                        dialog_exists = False
                        find_pair_bool = False
                        is_liked = False
                        add_to_blacklist = False
                        delete_from_blacklist = False
                        parameters_exist = False
                        found_people = []

                    elif request == '/команды' or request == 'начать':
                        write_message(
                            event.user_id,
                            '''Вот список команд, которые я могу выполнить:
                            1) Найти тебе пару 💘
                            2) Показать понравившихся людей 😍
                            3) Показать людей из черного списка 🚫''',
                            keyboard=create_keyboard('/команды', True)
                        )

                    elif request == 'найти пару':
                        write_message(
                            event.user_id,
                            '''Здорово! Сейчас мы тебе быстро найдем вторую половинку!
                            Ты можешь указать параметры поиска или довериться мне. Поверь, я тебя не подведу!😉''',
                            keyboard=create_keyboard('найти пару', True)
                        )
                        dialog_exists = True
                        find_pair_bool = True

                    elif request == 'указать параметры поиска' and find_pair_bool:
                        write_message(
                            event.user_id,
                            '''Пожалуйста, введи через запятую следующие параметры:
                            1) Свой возраст
                            2) От какого возраста искать
                            3) До какого возраста искать
                            4) Id своего города (Москва - 1; Санкт-Петербург - 2)
        
                            Пример: 20, 18, 22, 1
                            '''
                        )
                        parameters_exist = True

                    elif find_pair_bool and parameters_exist:
                        result = request.split(',')
                        result = [item.strip() for item in result]

                        write_message(event.user_id, 'Немного подожди, я ищу твою вторую половинку')
                        age = result[0]
                        user_info = vk_bot.get_user_info(event.user_id)
                        sex = user_info['sex']
                        city = result[3]

                        db_worker.add_user_to_db(user_info, age)

                        if sex == 1:
                            partner_sex = 2
                        else:
                            partner_sex = 1

                        blacklist = db_worker.show_blacklist(event.user_id)
                        blacklist_ids = [person['user_id'] for person in blacklist]

                        user_pairs = vk_bot.find_pairs(result[1], result[2], partner_sex, city)
                        found_people = user_pairs

                        write_message(event.user_id, 'Я нашел для тебя следующих людей:')
                        for person in user_pairs:
                            if person['user_id'] not in blacklist_ids:
                                person_photos = [item[0] for item in person['profile_photos']]
                                attachment = ','.join(person_photos)

                                write_message(
                                    event.user_id,
                                    f'''Id: {person['user_id']}
                                                    Имя: {person['first_name']}
                                                    Фамилия: {person['last_name']}
                                                    Страница вк: {person['url']}''',
                                    attachment=attachment
                                )

                        write_message(
                            event.user_id,
                            '''Если тебе кто-то приглянулся, дай мне знать!
                            Я сразу же добавлю этого человека в список понравившихся, чтобы он точно не потерялся😊''',
                            keyboard=create_keyboard('понравился', True)
                        )
                        find_pair_bool = False

                    elif request == 'довериться боту' and find_pair_bool:
                        write_message(
                            event.user_id,
                            '''Спасибо за доверие, я просто тронут! Только мне нужно кое-что знать.
                            Сколько тебе лет?'''
                        )

                    elif request.isdigit() and int(request) > 0 and find_pair_bool:
                        write_message(event.user_id, 'Немного подожди, я ищу твою вторую половинку')
                        age = int(request)
                        user_info = vk_bot.get_user_info(event.user_id)
                        sex = user_info['sex']
                        city = user_info['city_id']

                        db_worker.add_user_to_db(user_info, age)

                        if sex == 1:
                            partner_sex = 2
                        else:
                            partner_sex = 1

                        blacklist = db_worker.show_blacklist(event.user_id)
                        blacklist_ids = [person['user_id'] for person in blacklist]

                        user_pairs = vk_bot.find_pairs(age-2, age+2, partner_sex, city)
                        found_people = user_pairs

                        write_message(event.user_id, 'Я нашел для тебя следующих людей:')
                        for person in user_pairs:
                            if person['user_id'] not in blacklist_ids:
                                person_photos = [item[0] for item in person['profile_photos']]
                                attachment = ','.join(person_photos)

                                write_message(
                                    event.user_id,
                                    f'''Id: {person['user_id']}
                                    Имя: {person['first_name']}
                                    Фамилия: {person['last_name']}
                                    Страница вк: {person['url']}''',
                                    attachment=attachment
                                )

                        write_message(
                            event.user_id,
                            '''Если тебе кто-то приглянулся, дай мне знать!
                            Я сразу же добавлю этого человека в список понравившихся, чтобы он точно не потерялся😊''',
                            keyboard=create_keyboard('понравился', True)
                        )
                        find_pair_bool = False

                    elif request == 'да, мне кто-то понравился' or request == 'добавить еще одного человека' or request == 'добавить человека в понравившихся':
                        write_message(
                            event.user_id,
                            '''Пожалуйста, введите "id" понравившегося человека:'''
                        )
                        add_to_blacklist = False
                        is_liked = True

                    elif request == 'неа, никто не понравился' and dialog_exists:
                        dialog_exists = False
                        find_pair_bool = False
                        is_liked = False
                        add_to_blacklist = False
                        delete_from_blacklist = False
                        parameters_exist = False
                        found_people = []

                        write_message(
                            event.user_id,
                            'Эх, жалко... Ну, ничего, попробуй еще раз! Я уверен, тебе обязательно кто-то приглянется!😊',
                            keyboard=create_keyboard('в начало', True)
                        )

                    elif request.isdigit() and is_liked:
                        for person in found_people:
                            if int(request) == person['user_id']:
                                print('Добавляю пользователя')
                                db_worker.add_liked_to_db(event.user_id, person)

                        write_message(
                            event.user_id,
                            'Пользователь добавлен в список понравившихся✅',
                            keyboard=create_keyboard('еще понравился', True)
                        )

                    elif not request.isdigit() and is_liked:
                        write_message(
                            event.user_id,
                            '''Извини, но в id пользователя допущена ошибка🙁
                            Попробуй еще раз!)''',
                            keyboard=create_keyboard('неверные данные', True)
                        )

                    elif request == 'показать понравившихся людей':
                        liked_people = db_worker.show_liked_people(event.user_id)

                        if not liked_people:
                            write_message(
                                event.user_id,
                                'Эх, список пуст. Это значит, тебе пока никто не понравился. Но все впереди!😉',
                                keyboard=create_keyboard('завершить', True)
                            )
                        else:
                            write_message(
                                event.user_id,
                                f'Всего понравившихся людей: {len(liked_people)}',
                                keyboard=create_keyboard('завершить', True)
                            )

                            for person in liked_people:
                                write_message(
                                    event.user_id,
                                    f'''Id: {person['user_id']}
                                    Имя: {person['first_name']}
                                    Фамилия: {person['last_name']}
                                    Профиль вк: {person['profile_url']}'''
                                )

                    elif request == 'добавить человека в черный список':
                        write_message(
                            event.user_id,
                            'Пожалуйста, введи "id" человека, которого хочешь добавить в черный список:'
                        )
                        add_to_blacklist = True

                    elif request.isdigit() and add_to_blacklist:
                        for person in found_people:
                            if int(request) == person['user_id']:
                                print('Добавляю пользователя')
                                db_worker.add_to_blacklist(event.user_id, person)

                        write_message(
                            event.user_id,
                            'Пользователь добавлен в черный список🚫',
                            keyboard=create_keyboard('еще добавить в чс', True)
                        )

                    elif not request.isdigit() and add_to_blacklist:
                        write_message(
                            event.user_id,
                            '''Извини, но в id пользователя допущена ошибка🙁
                            Попробуй еще раз!)''',
                            keyboard=create_keyboard('неверные данные', True)
                        )

                    elif request == 'удалить человека из черного списка':
                        write_message(
                            event.user_id,
                            'Пожалуйста, введи "id" человека, которого хочешь удалить из черного списка:'
                        )
                        delete_from_blacklist = True

                    elif request.isdigit() and delete_from_blacklist:
                        result = db_worker.delete_from_blacklist(event.user_id, request)
                        delete_from_blacklist = False

                        if result:
                            write_message(
                                event.user_id,
                                f'Пользователь удален из черного списка✅',
                                keyboard=create_keyboard('еще удалить из чс', True)
                            )
                        else:
                            write_message(
                                event.user_id,
                                f'Пользователя c таким id нет в черном списке👣',
                                keyboard=create_keyboard('еще удалить из чс', True)
                            )

                    elif not request.isdigit() and delete_from_blacklist:
                        write_message(
                            event.user_id,
                            '''Извини, но в id пользователя допущена ошибка🙁
                            Попробуй еще раз!)''',
                            keyboard=create_keyboard('неверные данные', True)
                        )

                    elif request == 'показать черный список':
                        blacklist_people = db_worker.show_blacklist(event.user_id)
                        dialog_exists = True

                        if not blacklist_people:
                            write_message(
                                event.user_id,
                                'В черном списке пока никого нет.',
                                keyboard=create_keyboard('показать черный список', True)
                            )
                        else:
                            write_message(
                                event.user_id,
                                f'Всего людей в черном списке: {len(blacklist_people)}',
                                keyboard=create_keyboard('показать черный список', True)
                            )

                            for person in blacklist_people:
                                write_message(
                                    event.user_id,
                                    f'''Id: {person['user_id']}
                                    Имя: {person['first_name']}
                                    Фамилия: {person['last_name']}
                                    Профиль вк: {person['profile_url']}'''
                                )

                    else:
                        write_message(
                            event.user_id,
                            '''К сожалению, я тебя не понимаю...😔
                            Введи "/команды" для просмотра доступных команд.''',
                            keyboard=create_keyboard('', True)
                        )
                        dialog_exists = False
                        find_pair_bool = False
                        is_liked = False
                        add_to_blacklist = False
                        delete_from_blacklist = False
                        parameters_exist = False
                        found_people = []

                except Exception:
                    print('Возникла ошибка')
                    dialog_exists = False
                    find_pair_bool = False
                    is_liked = False
                    add_to_blacklist = False
                    delete_from_blacklist = False
                    parameters_exist = False
                    found_people = []

                    write_message(
                        event.user_id,
                        'Упс... Что-то пошло не так!',
                        keyboard=create_keyboard('/команды', True)
                    )


if __name__ == '__main__':
    start_vk_longpoll()
