import vk_api
from random import randrange
from vk_bot import VkBot
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType

# Токен Вк-группы, от лица которой будет писать бот.
group_token = input('Group token: ')
# Токен любого пользователя Вк, он нужен для поиска людей, так как по токену группы это делать нельзя.
bot_token = input('Bot token: ')

vk_session = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk_session)
vk_bot = VkBot(bot_token)


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

    if request == '/команды' or request == 'в начало':
        keyboard.add_button('Найти пару', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()

        keyboard.add_button('Показать понравившихся людей', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()

        keyboard.add_button('Показать черный список', color=VkKeyboardColor.NEGATIVE)

    elif request == 'найти пару':
        keyboard.add_button('Довериться боту', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Указать параметры поиска', color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('В начало', color=VkKeyboardColor.NEGATIVE)

    else:
        keyboard.add_button('/команды', color=VkKeyboardColor.POSITIVE)

    keyboard = keyboard.get_keyboard()
    return keyboard


dialog_exists = False
find_pair_bool = False
show_liked_people_bool = False
show_black_bool = False

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            print('Текст сообщения:', event.text)
            print(f'Отправитель: {event.user_id}\n')
            request = event.text.lower()
            keyboard = create_keyboard(request, True)

            if request == "привет":
                write_message(event.user_id, f"Хай, {event.user_id}")

            elif request == '/команды':
                write_message(
                    event.user_id,
                    '''Вот список команд, которые я могу выполнить:
                    1) Найти тебе пару 💘
                    2) Показать понравившихся людей 😍
                    3) Показать людей из черного списка 🚫''',
                    keyboard=keyboard
                )

            elif request == 'найти пару':
                write_message(
                    event.user_id,
                    '''Здорово! Сейчас мы тебе быстро найдем вторую половинку!
                    Ты можешь указать параметры поиска или довериться мне. Поверь, я тебя не подведу!😉''',
                    keyboard=keyboard
                )
                dialog_exists = True
                find_pair_bool = True

            elif request == 'довериться боту' and find_pair_bool:
                write_message(
                    event.user_id,
                    'Спасибо за доверие, я просто тронут! Только мне нужно кое-что знать: сколько тебе лет?'
                )

            elif request.isdigit() and int(request) and int(request) > 0 and find_pair_bool:
                age = int(request)
                user_info = vk_bot.get_user_info(event.user_id)
                sex = user_info['sex']
                city = user_info['city_id']

                if sex == 1:
                    partner_sex = 2
                else:
                    partner_sex = 1

                user_pairs = vk_bot.find_pairs(age-2, age+2, partner_sex, city)
                write_message(event.user_id, 'Я нашел вам следующих людей:')

                for person in user_pairs:
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

            elif request == 'пока':
                write_message(event.user_id, 'Пока-пока! Если что, обращайся!')

                dialog_exists = False
                find_pair_bool = False
                show_liked_people_bool = False
                show_black_bool = False

            elif request == 'в начало' and dialog_exists:
                write_message(event.user_id, 'Понял, давай попробуем еще раз.', keyboard=keyboard)

                dialog_exists = False
                find_pair_bool = False
                show_liked_people_bool = False
                show_black_bool = False

            else:
                write_message(
                    event.user_id,
                    '''К сожалению, я Вас не понимаю...😔
                    Введите "/команды" для просмотра доступных команд.''',
                    keyboard=keyboard
                )
                dialog_exists = False
                find_pair_bool = False
                show_liked_people_bool = False
                show_black_bool = False
