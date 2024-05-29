import telebot
import vk_api
import time
import threading
import g4f
import datetime


TELEGRAM_BOT_TOKEN = '' #https://t.me/BotFather тут берете токен от телеграмм бота своего
VK_TOKEN = '' #создаете свое вк приложение, и берет access токен по ссылке https://vkhost.github.io/ и выбераете offline,wall,photos,docs,groups,friends
#или https://oauth.v k.com/authorize?client_id=ТУТ ВЫ ВВОДИТЕ АЙДИ СВОЕГО ПРИЛОЖЕНИЯ В ВК&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=offline,wall,photos,docs,groups,friends&response_type=token&v=5.21

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def get_user_groups(user_id, token):
    vk_session = vk_api.VkApi(token=token)
    try:
        groups_info = vk_session.method('groups.get',
                                        {'user_id': user_id, 'extended': 1, 'fields': 'name,type,date,members_count'})
        if groups_info and 'items' in groups_info:
            return groups_info['items']
        else:
            return []
    except vk_api.exceptions.ApiError as e:
        print(f"Ошибка при получении информации о группах пользователя: {e}")
        return []


def get_user_data(user_id, token):
    vk_session = vk_api.VkApi(token=token)
    try:
        user_info = vk_session.method('users.get', {'user_ids': user_id,
                                                    'fields': 'first_name,last_name,is_closed,bdate,schools,id,city,universities,last_seen,counters'})
        if user_info:
            return user_info[0]
    except vk_api.exceptions.ApiError as e:
        print(f"Ошибка при получении информации о пользователе: {e}")
        return None


def user_get_and_chat_with_gpt(original_message, user_id, sent_message):
    user_data = get_user_data(user_id, VK_TOKEN)

    if not user_data:
        bot.send_message(original_message.chat.id, f"Неверный формат ID профиля. Пожалуйста, введите корректный ID")
        bot.delete_message(sent_message.chat.id, sent_message.message_id)
        return

    groups_data = get_user_groups(user_data['id'], VK_TOKEN)
    if not groups_data:
        if user_data.get('is_closed'):
            bot.send_message(original_message.chat.id, f"Профиль пользователя закрыт")
            bot.delete_message(sent_message.chat.id, sent_message.message_id)
            return
        bot.send_message(original_message.chat.id, "У пользователя нет групп в VK")
        bot.delete_message(sent_message.chat.id, sent_message.message_id)
        return

    categories_list = []
    for group in groups_data:
        group_id = group['id']
        group_category = get_group_categories(group_id, VK_TOKEN)
        categories_list.append(group_category)

    school_sub = []
    for group in groups_data:
        group_name = group['name']
        school_sub.append(str(group_name).lower())
    school_sub_s = []
    for i in school_sub:
        if 'физик' in i:
            school_sub_s.append('физика')
        elif 'математ' in i:
            school_sub_s.append('математика')
        elif 'русский' in i:
            school_sub_s.append('русский')
        elif 'биолог' in i:
            school_sub_s.append('биология')
        elif 'химия' in i:
            school_sub_s.append('химия')
        elif 'информат' in i or 'программ' in i:
            school_sub_s.append('информатика')
    school_sub_s = list(set(school_sub_s))
    ssilki = {'биология': ['https://edu.sirius.online/#/course/1865', 'https://edu.sirius.online/#/course/1889',
                           'https://edu.sirius.online/course/anatomy9',
                           'https://edu.sirius.online/course/biochemistry10',
                           'https://edu.sirius.online/course/biochemistry10'],
              'информатика': ['https://edu.sirius.online/#/course/1805', 'https://edu.sirius.online/#/course/1890',
                              'https://edu.sirius.online/#/course/1891', 'https://edu.sirius.online/#/course/1866',
                              'https://edu.sirius.online/#/course/1880'],
              'математика': [['https://edu.sirius.online/course/algebra7', 'https://edu.sirius.online/#/course/1878'],
                             ['https://edu.sirius.online/#/course/1876', 'https://edu.sirius.online/course/geometry8'],
                             ['https://edu.sirius.online/#/course/1845', 'https://edu.sirius.online/#/course/1877'],
                             'https://edu.sirius.online/#/course/1846', 'https://edu.sirius.online/#/course/1846'],
              'русский': ['https://edu.sirius.online/#/course/1847', 'https://edu.sirius.online/#/course/1862',
                          'https://edu.sirius.online/#/course/1892', 'https://edu.sirius.online/#/course/1847',
                          'https://edu.sirius.online/#/course/1847'],
              'физика': ['https://edu.sirius.online/#/course/1851', 'https://edu.sirius.online/#/course/1863',
                         'https://edu.sirius.online/#/course/1848', 'https://edu.sirius.online/#/course/1799',
                         'https://edu.sirius.online/#/course/1881'],
              'химия': ['https://edu.sirius.online/#/course/1864', 'https://edu.sirius.online/#/course/1864',
                        'https://edu.sirius.online/#/course/1893', 'https://edu.sirius.online/course/chemistry10',
                        'https://edu.sirius.online/course/chemistry11'],
              }
    age = False
    if 'bdate' in user_data:
        bdate = user_data['bdate']
        try:
            birth_year = int(bdate[-4:])
            current_year = datetime.datetime.now().year
            age = current_year - birth_year
        except ValueError:
            age = False

    if categories_list:
        gpt_input_text = f'это список категорий подписок {categories_list}, по нему рассортируй по группам и выдели топ 5 интересов у человека если у него пять или больше подписок, если меньше то выдели столько сколько у него, это может быть какое либо хобби, любимый предмет, любимый вид спорта или вид деятельности, НАПИШИ ПОЖАЛУЙСТА БЕЗ ЛИШНИХ СЛОВ И ЗНАКОВ, просто топ 5 интересов вот пример 1. Образование 2. Программирование и технологии 3. Спорт 4. Музыка 5. Финансы'
        try:
            response = g4f.ChatCompletion.create(
                model=g4f.models.default,
                provider=g4f.Provider.Liaobots,
                messages=[{"role": "user", "content": gpt_input_text}],
                stream=False,
            )

            full_response = ''
            for msg in response:
                full_response += msg

            if age <= 14:
                nugnie_kurs = 0
            elif age == 15:
                nugnie_kurs = 1
            elif age == 16:
                nugnie_kurs = 2
            elif age == 17:
                nugnie_kurs = 3
            else:
                nugnie_kurs = 4
            print(school_sub_s)
            print(age)
            print(school_sub)
            if school_sub_s and age:
                if len(school_sub_s) >= 3:
                    bot.send_message(original_message.chat.id, f'''Привет !

Анализ профиля пользователя {user_data.get('first_name', '')}

Увлечения профиля:

{full_response}

Исходя из интересов и умений, мы предлагаем следующие курсы для дальнейшего развития:

1. Курс по {school_sub_s[0]}: {ssilki[school_sub_s[0]][nugnie_kurs]}
2. Курс по {school_sub_s[1]}: {ssilki[school_sub_s[1]][nugnie_kurs]}
3. Курс по {school_sub_s[2]}: {ssilki[school_sub_s[2]][nugnie_kurs]}''')

                elif len(school_sub_s) == 2:
                    bot.send_message(original_message.chat.id, f'''Привет !

Анализ профиля пользователя {user_data.get('first_name', '')}

Увлечения профиля:

{full_response}

Исходя из интересов и умений, мы предлагаем следующие курсы для дальнейшего развития:

1. Курс по {school_sub_s[0]}: {ssilki[school_sub_s[0]][nugnie_kurs]}
2. Курс по {school_sub_s[1]}: {ssilki[school_sub_s[1]][nugnie_kurs]}''')

                elif len(school_sub_s) == 1:
                    bot.send_message(original_message.chat.id, f'''Привет !

Анализ профиля пользователя {user_data.get('first_name', '')}

Увлечения профиля:

{full_response}

Исходя из интересов и умений, мы предлагаем следующие курсы для дальнейшего развития:

1. Курс по {school_sub_s[0]}: {ssilki[school_sub_s[0]][nugnie_kurs]}''')


                else:
                    bot.send_message(original_message.chat.id, f'''Привет !

Анализ профиля пользователя {user_data.get('first_name', '')}

Увлечения профиля:

{full_response}''')
            else:
                bot.send_message(original_message.chat.id, f'''Привет !

Анализ профиля пользователя {user_data.get('first_name', '')}

Увлечения профиля:

{full_response}''')

        except Exception as e:
            bot.send_message(original_message.chat.id, f"Error: {e}")
    bot.delete_message(sent_message.chat.id, sent_message.message_id)


def get_group_categories(group_id, access_token):
    vk_session = vk_api.VkApi(token=access_token)
    vk = vk_session.get_api()
    try:
        group_info = vk.groups.getById(group_id=group_id, fields='activity')
        time.sleep(0.2)
        if group_info:
            if 'activity' in group_info[0]:
                return group_info[0]['activity']
            else:
                return "Категория группы не найдена"
        else:
            return "Группа с указанным ID не найдена"

    except vk_api.VkApiError as e:
        return f"Произошла ошибка VK API: {e}"


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = telebot.types.KeyboardButton('Информация❓')
    item2 = telebot.types.KeyboardButton('Узнать профиль🔎')
    markup.add(item1, item2)

    bot.send_message(message.chat.id,
                     'Здравствуйте, готовы сделать анализ профиля ВКонтакте? Нажми на кнопку снизу и отправь мне свой VK ID',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == 'Информация❓':
        bot.send_message(message.chat.id, 'Это бот созданный в рамках проекта Сириус-Лето, по вопросам или проблемах в работе бота писать @Satpsi\n\
Мы не несем ответственности за достоверность предоставленных результатов, \
анализ проводится исходя из открытых данных страницы')
    elif message.text == 'Узнать профиль🔎':
        bot.send_message(message.chat.id,
                         'Введите VK ID пользователя в формате:\n@Name (отправь Name)\nИли вот так: id123456789 / 123456789')
        bot.register_next_step_handler(message, process_vk_id_input)
    else:
        bot.send_message(message.chat.id, 'Извините, я не понял ваш запрос. Выберите один из вариантов на клавиатуре.')


def process_vk_id_input(message):
    user_id = message.text
    sent_message = bot.send_message(message.chat.id, "Анализ может занять несколько минут...")
    threading.Thread(target=user_get_and_chat_with_gpt, args=(message, user_id, sent_message)).start()


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)
