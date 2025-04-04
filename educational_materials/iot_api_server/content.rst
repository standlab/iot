Сервер для регистрации устройств
================================

Мотивация
---------

Мы уже наладили коммуникацию между устройствами, используя MQTT. Но внимательный читатель, мог
заметить, что нам пришлось вручную прописывать MQTT-темы на каждом из устройств и заново загружать 
программу на каждое из них. Когда все устройства лежат у нас на столе это не проблема, но 
представьте себе эту ситуацию со стороны пользователя, которые может купить датчик в понедельник, 
а актуатор в воскресенье (или купит актуатор через год на замену сломанному) - естественно мы не 
можем полагаться на то, что они по случайному совпадению будут знать какие данные слушать. 
Нам нужен **способ доставить настройки в устройство** не меня его основной код. Способов может быть
несколько мы можем поставлять с нашим устройством клиентское приложение, которое свяжеться с 
устройством по USB или WiFi и поможет настроить его. Другим способом (который может работать в 
связке с клиентским приложением) может быть сервер к которому подключаться устройства и получат 
всю нужную информацию с него. Именно это мы и будем сегодня делать, так как это основа, на которой
можно построить разные сценарии. 

Выбор инструментов
------------------

Существует несколько инструментов создать REST-API сервер, мы будем использовать FastAPI так как он
очень хорошо документирован и имеет руководство пользователей (https://fastapi.tiangolo.com/tutorial/)
от авторов. Это важно, так как мы не  сможем покрыть все аспекты в этом уроке, но Вы всегда сможете 
обратить к документации и руководству для дальнейше разработки.

Определяем требования
---------------------

Всегда важно определиться, чего мы хотим от нашей разработки, поэтому сформируем требования (не 
путать с техническим заданием). Требования является первым шагом к тому чтобы объяснить коллегам
по команде или генеративным моделям, что Вы от них хотите.

* Устройства IoT взаимодействуют через MQTT и используют FastAPI в качестве точки входа
* Должна быть запросы для: 
    * регистрации устройств IoT
    * извлечения тем MQTT на основе идентификатора устройства
    * извлечения конфигурации
    * задание конфигурации
    * Должна быть конечная точка для удаления и изменения устройства.
* Регистрация должна быть выполнена с идентификатором устройства IoT 
    * ID устройства вычисляется основе хэша MAC-адреса
    * местоположением устройства (широта, долгота, местоположение - название города)
    * владельцем устройства (просто название компании)
    * типом измерений устройства (температура, давление)
    * моделью датчика устройства. 
* Конфигурация включает
    * интервал отправки данных
    * качество сервиса QoS
    * время последнего изменения конфигурации
* Темы должны однозначно данные, напримерм соответствовать шаблону владелец/местоположение/тип_измерений_устройства/идентификатор_устройства. 
* После регистрации устройство должно иметь возможность получать темы на основе своего идентификатора.
* Конфигурации может быть изменена системным администратором.
* Устройство принимает новую конфигурацию после перезагрузки

Установим зависимости:

.. code-block:: bash

    pip install fastapi==0.115.8
    pip install pydantic==2.10.6
    pip install uvicorn[standard]==0.34.0



Код сервера расположен в папке `./src/iot_regestration_server.`

Код клиента расположен в папке `./src/esp_client.`


Разворачиваем на удаленном сервере
----------------------------------

Для того, чтобы сервер был доступен снаружи, мы можем разместить его на виртуальном сервере. 
Вам нужно знать пароль и IP адрес сервера:

Подключаемся:

.. code-block:: bash

    artem@pc:~$ ssh admin@62.109.28.99
        admin@62.109.28.99's password: YOUR_PASSWORD_HERE

        Welcome to Ubuntu 22.04 LTS (GNU/Linux 5.15.0-126-generic x86_64)

        * Documentation:  https://help.ubuntu.com
        * Management:     https://landscape.canonical.com
        * Support:        https://ubuntu.com/advantage
        New release '24.04.2 LTS' available.
        Run 'do-release-upgrade' to upgrade to it.

        Last login: Thu Mar 20 08:00:05 2025 from 188.162.250.239

Устанавливаем нужные программы:

.. code-block:: bash

        admin@iot-reg:~# sudo apt update
        admin@iot-reg:~# sudo install git
            ... installed
        admin@iot-reg:~# sudo apt install python3-pip
            ... installed
        admin@iot-reg:~# sudo apt install python3-venv
            ... installed

Клонируем проект с кодом:

.. code-block:: bash

        admin@iot-reg:~# git clone https://github.com/standlab/iot
            Cloning into 'iot'...
            remote: Enumerating objects: 243, done.
            remote: Counting objects: 100% (243/243), done.
            remote: Compressing objects: 100% (178/178), done.
            remote: Total 243 (delta 81), reused 209 (delta 47), pack-reused 0 (from 0)
            Receiving objects: 100% (243/243), 8.61 MiB | 2.45 MiB/s, done.
            Resolving deltas: 100% (81/81), done

Создаем и активируем виртуальное окружение для проекта:

.. code-block:: bash

        admin@iot-reg:~# python3 -m venv ~/iot-regestration-server
        admin@iot-reg:~# source ~/iot-regestration-server/bin/activate    
    
Переходим в папку с кодом сервера, устанавливаем зависимости и запускаем:

.. code-block:: bash

        (iot-regestration-server) admin@iot-reg:~# cd educational_materials/iot_api_server/src/iot_regestration_server/
        (iot-regestration-server) admin@iot-reg:~# pip install -r requirements.txt
        (iot-regestration-server) admin@iot-reg:~# uvicorn main:app --host 0.0.0.0 --port 8000
            INFO:     Started server process [111597]
            INFO:     Waiting for application startup.
            INFO:     Application startup complete.
            INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)


Уведомления с помощью телеграмм бота
------------------------------------

На текущий момент у нас есть

1. Регистрация устройств с помощью приложения (сервера) на FastAPI
2. Общение устройств с помощью MQTT

Т.е. устройства могут регистрироваться и оптравлять сообщения друг дургу. Инженер, который 
настраивает систему может так же пользоваться API для того, чтобы получать информацию об
устройствах, мы делали это через ``swagger`` когда заходили на страницу с функциями сервиса 
``http://localhost:8080/docs``. Однако такой способ коммуникации не удобен для обычного
пользователя и ему нужно предоставить привычный способ общения: через графический интерфейс или
приложение которым он и так пользуется. 

Мы воспользуемя вторым сопособ и сделаем телеграм бота, которые будет уведомлять пользователя, 
когда в системе происходят какие-либо события, например регистрируется устройство. События на
которые будет реагировать бот вы, как разработчики, всегда можете прописать в коде. Для python
есть хорошая библиотека для создания своего бота https://github.com/eternnoir/pyTelegramBotAPI.

Добавим ее к нашим зависимостям в ``requirements.txt``:

.. code-block:: bash

    pyTelegramBotAPI==4.26.0

И установим: 

.. code-block:: bash

    pip install -r requirements.txt

Далее напишем код, который будет заниматься отправкой сообщения пользователям. 
В самой простой реализации сделаем оптправку сообщений всем кого бот "знает".

.. code-block:: python

    # notifier.py
    import telebot
    import os

    # Load environment variables
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    if TELEGRAM_CHAT_ID:
        chat_ids = [TELEGRAM_CHAT_ID]
    else:
        chat_ids = []

    # Validate environment variables
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables.")

    bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

    def send_telegram_notification(message: str):
        """Send a notification message to the configured Telegram chat."""
        for chat_id in chat_ids:
            try:
                bot.send_message(chat_id, message)
            except Exception as e:
                print(f"Error sending Telegram notification: {e}")

    if __name__ == "__main__":
        send_telegram_notification("Hello there?")
        bot.infinity_polling()


Если мы сейчас попробуем выполнить этот код:

.. code-block:: bash

    python notifier.py
  

То получим ошибку, которая говорит, что не установлен токен по которому телеграм поймет какой именно
бот сейчас задействован. Таким образом токен это ключ, по которому сервер телеграм, поймет с каким
ботом мы хотим работать и что у нас есть доступ к нему. Можно сказать, что это логин и пароль 
одновременно.  

.. code-block:: bash

    Traceback (most recent call last):
    File "..../src/iot_regestration_server/notifier.py", line 10, in <module>
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables.")
    ValueError: TELEGRAM_BOT_TOKEN is not set in environment variables.

Где взять эти данные? Для регистрации нового бота в телеграм есть ... другой бот. Можно набрать в 
поиске **bot father** и найти его. Процесс регистрации очень прост и делается в одну команду.

**ВАЖНО: никому не отдавайте токен, иначе вы потеряете конроль над ботом**

.. image:: ../../graphics/telegram_bot_father_help_newbot.png
  :width: 800
  :alt: Регистрация чат-бота (получение токена для использования API Telegram)

Теперь мы готовы прописать переменные окружения, так чтобы приложение могло получить доступ 
к этой информации, но при этом в само коде мы не указывали явно эти данные. 

**ВАЖНО: не указываете пароли, токены и другую чувствительную информацию прямо в коде. 
Так как ее может уведеть, то кому она не предназначалась**

Ниже приведен код для того чтобы установить эти переменные. Замените ``your_telegram_bot_token``
на токен который пришел от bot father (на скриншоте выше он закрашен оранжевым).

.. code-block:: bash

    export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"

To make them persistent (for Linux/macOS), add them to your ~/.bashrc or ~/.bash_profile:

.. code-block:: bash

    echo 'export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"' >> ~/.bashrc
    source ~/.bashrc

Для командной строки Windows :

.. code-block:: bash

    set TELEGRAM_BOT_TOKEN=your_telegram_bot_token

Для Windows (PowerShell):

.. code-block:: bash

    $env:TELEGRAM_BOT_TOKEN="your_telegram_bot_token"


Код ``notifier.py`` подразумевает, что мы знаем не только token чата, но и пользователя, которому 
мы хотим адресовать сообщение. В "базовой комплектации", т.е. когда бот только запустился за 
это отвечает вторая переменная ``TELEGRAM_CHAT_ID``, в дальнейшем бот будет сам сохранять CHAT_ID. 
Если вы знаете этот ID, то можете его задать как показано выше, но если мы делаем это в первый раз, то 
этой информации у нас нет, поэтому напишем фукнцию, которая вернет нам этот номер. Мы будем 
использовать декоратор ``@bot.message_handler(commands=['chatid'])`` это нужно для того, чтобы 
привязать команду пользователя к вызову нашей функции. Работа этой функции очень простая: из
сообщения пользователя извлекаем ``chat.id`` и передаем его обратно пользователю. Эта функция
нужна нам для проверки и мы можем ей не пользоваться когда запустим бота в постоянную работу. 


.. code-block:: python

    @bot.message_handler(commands=['chatid'])
    def handle_chatid(message: telebot.types.Message) -> None:
        bot.reply_to(message, f"Your chat id is {message.chat.id}")


Так же принято делать команду ``/start``:

.. code-block:: python

    @bot.message_handler(commands=['start'])
    def handle_start(message: telebot.types.Message):
        bot.reply_to(message, "This bot will notify you if some IoT device registered")


Запустим бота:

.. code-block:: bash

    python notifier.py

Зайдем в приложение телеграмм и найдем нашего бота по имени. Назмем ``start`` и увидим 
приветственное сообщение: *This bot will notify you if some IoT device registered*
Если мы делаем запуск бота в первый раз и еще не установили переменную TELEGRAM_CHAT_ID,
сообщения *Hello there?* мы не увидим, и это правильно так как бот еще не знает кому отправить
сообщение - ``chat_ids`` пока пустой. 

.. image:: ../../graphics/telegram_bot_start_chatid.png
  :width: 400
  :alt: Получение своего чат-ID

Теперь если утсановить переменную TELEGRAM_CHAT_ID:

.. code-block:: bash

    export TELEGRAM_CHAT_ID="your_telegram_chat_id"

То в следующий раз мы получим сообщение сразу.

.. image:: ../../graphics/telegram_bot_memorize_you.png
  :width: 400
  :alt: Бот теперь знает на ID и сразу присылает сообщение


Теперь мы дали нашему боту всю необходимую информацию для того, чтобы он мог работать и 
присылать сообщение тому пользователю, которого мы указали через переменную ``TELEGRAM_CHAT_ID``.
Следующий шаг это подключить нашего бота к серверу.


Интегрируем чат-бота
--------------------

Проверим, что бот действительно работает и сможет уведомлять нас о регистрации новых устройств.
Для этого нужно использовать ``send_telegram_notification``, написанную нами ранее. Сущесвтует 
несколько способов использования в зависимости от требований и желаемой связанности системы:


1. (Самый простой) Прямой вызов из FastAPI

   * Когда регистрируется новое устройство, приложение FastAPI отправляет HTTP-запрос напрямую в API Telegram Bot.
   * Бот немедленно пересылает уведомление настроенному пользователю или группе.

    **Плюсы**: простота, не требуется дополнительная инфраструктура.

    **Минусы**: если Telegram API работает медленно или не работает, это может задержать ответ FastAPI.

2. (Рабочий вариант) Использование фоновой задачи в FastAPI

    * FastAPI поддерживает фоновые задачи с помощью BackgroundTasks.
    * запрос регистрации устройства ставит в очередь фоновую задачу для отправки уведомления.
     
    **Плюсы**: пользователь сразу видит регистрацию устройства, а уведомление выполняется **асинхронно**.

    **Минусы**: если приложение FastAPI выходит из строя или перезапускается, ожидающие уведомления могут быть потеряны.

3. (Микросервисный) Использование очереди или брокера сообщений (например, Redis, RabbitMQ, Kafka)
   
   * FastAPI публикует сообщение в очереди при регистрации нового устройства.
   * Отдельный рабочий процесс (бот Telegram) прослушивает сообщения и отправляет уведомления.

    **Плюсы**: масштабируемость и устойчивость к сбоям; приложение FastAPI отделено от системы уведомлений.

    **Минусы**: требуется дополнительная инфраструктура (например, Redis, RabbitMQ).

Мы выберем компромисный второй вариант, пользоваться первым не рекомендуется, а третий дан 
для полноты картины, примера применения технолигий (Redis, RabbitMQ, Kafka), которые используются 
в индустрии. Если вы их освоите это будет плюсом, если вы захотите принять решение в реальных
проектах. 

Модифицируем код функции для регистрации устройств. Обратите внимание, нам нужно импортировать 
``BackgroundTasks``, а также добавить параметр ``tasks: BackgroundTasks``, что бы  FastAPI понял, 
что в этой функции используются фоновые задачи:

.. code-block:: python

    from fastapi import BackgroundTasks

    @app.post("/register/", response_model=dict)
    def register_device(device: DeviceRegistration, tasks: BackgroundTasks):

        # unaffected previous code

        message = (
            f"New device registered!\n"
            f"ID: {device_id}\n"
            f"Location: ({device.longitude}, {device.latitude})\n"
            f"Owner: {device.owner}\n"
            f"Measurement Type: {device.measurement_type}\n"
            f"Sensor Model: {device.sensor_model}"
        )
        tasks.add_task(send_telegram_notification, message)
        return {"device_id": device_id, "topic": topic}

И перезапустим сервис (не забыв прописать TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID), если не сделали 
это заранее:

.. code-block:: bash

    export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
    export TELEGRAM_CHAT_ID="your_telegram_chat_id"
    uvicorn main:app --host 0.0.0.0 --port 8000

Теперь при регистрации устройства устройства мы будем получать сообщение которое мы составили из
данных устройства. Однако теперь мы не получаем ответ от сообщений на ``/start``. Это происходит 
из-за того, что чтобы бот слушал сообщения нужно выполнить ``polling``, но это приведет тому что 
программа будет находиться в этом режиме постоянно, именно поэтому ``infinity_polling()`` был 
последней строкой в модуле, все что после него не будет достигнуто.

.. code-block:: python

    if __name__ == "__main__":
        send_telegram_notification("Hello there?")
        bot.infinity_polling()
        print("This will not be reached until polling stopped")

Как же быть? С одной стороны нам нужно постоянно слушать сообщения от пользователей по FastAPI
с другой стороны у нас есть Бот, который тоже должен быть постоянно включен. Хотя интуитивно, 
кажется что проблемы нет - мы же можем запускать множество программ и они работают. Здесь ситуация 
сложнее в том смысле, что нам с одной стороны нужно "отвязать" друг от друга два приложения, с другой
стороны мы не хотим терять связь и пользоваться ``send_telegram_notification``, когда нам нужно. 
Это достаточно частая задача и для ее решения можно использовать потоки.

Модифицируем код бота следующим образом:

.. code-block:: python

    def start_bot():
        """Runs the Telegram bot polling"""
        bot.polling(none_stop=True)

А в сервис добавим код который запустит бота в отдельном потоке в виде фонового процесса 
``daemon=True``.

.. code-block:: python

    from notifier import start_bot

    # Start Telegram bot in a separate thread
    threading.Thread(target=start_bot, daemon=True).start()


Теперь нам достаточно запустить только сервис, а он уже запустить бота в отдельном потоке, 
и ни одна из частей системы не будет блокировать другую.

