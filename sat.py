import telebot
import vk_api
import g4f
import time

TELEGRAM_BOT_TOKEN = ''
VK_TOKEN = ''
text = f'пиши на русском и пожалуйста без лишних слов я тебе скину группы категории и ключевые слова которые тебе помогут ЧТОБЫ ОБЯЗАТЕЛЬНО В СУММЕ ВСЕ КАТЕГОРИИ ДАВАЛИ РОВНО 100% , а ты попробуй определить их категории и распределить по процентам, напиши только по шаблону, ничего остального не надо писать, ЧТОБЫ ОБЯЗАТЕЛЬНО В СУММЕ ВСЕ КАТЕГОРИИ ДАВАЛИ РОВНО 100%\
Госорганизация-Администрация,Больницы,Детский сад,Дом престарелых,Объявления,Пенсионный фонд,Поиск работы \
Здоровье-Витамины,Медицина,Похудение,Правильное питание,Фитнес,Тренажерный зал \
Интернет и технологии-Интернет и технологии,Программирование,Программное обеспечение,Социальные сети \
Искусство и культура творческие направления-Балет,Искусство,Книги,Лингвистика,Музей,Творчество,Философия,Культура,Мода \
Еда и кулинария-Домохозяйки,Продукты,Рецепты\
Магазины и услуги-Маркетплейсы,Барахолка,Товары,Купоны,Скидки,Визажист,Компьютерная помощь,Доставка,Реклама,Кафе\
Музыка-Артист,Концерт,Виды музыки,Музыканты,аккорды,Певец - сколько % \
Образование-Олимпиады,Курсы,Онлайн-школы,Репетиторы,Обучение,Школьные предметы,Саморазвитие,Учитель,Преподавание,Наука\
Объединения, группы людей-Автовладельцы,Религия,Благотворительность,Группа одноклассников,Соседи\
Политика-Выборы,Президент,Депутаты,Военное дело,Страна\
Путешествия и туризм-Туризм,Онлайн-тур,Путешествия,Отдых\
Развлекательные-Блогеры,Компьютерные игры,Кино,Фильмы,Дикие и домашние животные,Мемы,Стримеры,Ютуберы,Настольные игры,Юмор,Шоу\
СМИ и новости-Новости,Медиа,Подслушано,Городские группы,Анонс\
Семья и отношения-Беременность,Детское питание,игрушки,Материнство,Родители,Знакомства\
Спорт-Спортивная организация,Киберспорт,Шахматы,виды спорта\
Увлечения и хобби-Анимация,Дизайн и графика,Питомники,Хобби,Фотография,Автомобили,Рыбалка\
Экономика и финансы-Банки и (ЦБ),Бизнес,Инвестиции,Криптовалюта,Продажи,Финансы\
Запрещенные-Вейп,Даркнет,Оружие,Порнография,Эротика,Наркотики,Казино,Ставки,Сливы\
Другое-Строительство,Армия,Эстетика,красота,Картинки и фото,Интерьер,Ремонт и тд\
вот так пиши ответ Госорганизация - % Здоровье - % Интернет и технологии - % Искусство и культура творческие направления - % Еда и кулинария - % Магазины и услуги - % Музыка - % Образование - %Объединения, группы людей - % Политика - % Путешествия и туризм - % Развлекательные - % Семья и отношения - % СМИ и новости - % Спорт - % Увлечения и хобби - % Экономика и финансы - % Запрещенные - % Другое - %{{}}'
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


def user_get_and_chat_with_gpt(message, user_id):
    user_data = get_user_data(user_id, VK_TOKEN)

    if not user_data:
        bot.send_message(message.chat.id, f"Пользователь с ID {user_id} не найден.")
        return

    groups_data = get_user_groups(user_data['id'], VK_TOKEN)
    if groups_data:
        groups_list = [group['name'] for group in groups_data]
        gpt_input_text = f'{text} VK Groups: {", ".join(groups_list)}'

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
            bot.send_message(message.chat.id, full_response)
        except Exception as e:
            bot.send_message(message.chat.id, f"Error: {e}")

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    item1 = telebot.types.KeyboardButton('Информация❓')
    item2 = telebot.types.KeyboardButton('Узнать профиль🔎')
    markup.add(item1, item2)

    bot.send_message(message.chat.id, 'Привет, я бот в telegram. Отправь мне VK ID пользователя, например @User_name отправть User_name без лишних знаков', reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    if message.text == 'Информация❓':
        bot.send_message(message.chat.id, 'Это бот для проекта Сириус-Лето, по вопросам писать @Satpsi')
    elif message.text == 'Узнать профиль🔎':
        bot.send_message(message.chat.id, 'Введите VK ID пользователя:')
        bot.register_next_step_handler(message, process_vk_id_input)
    else:
        bot.send_message(message.chat.id, 'Извините, я не понял ваш запрос. Выберите один из вариантов на клавиатуре.')

def process_vk_id_input(message):
    user_id = message.text
    user_get_and_chat_with_gpt(message, user_id)

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(1)
bot.pollind(none_stop=True)