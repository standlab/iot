MQTT
====

Когда мы используем "интернет людей" для доступа к каким любо ресурсам в сети мы используем модель 
взаимодействия запрос-ответ (request-response). Это достаточно распространенная модель хотя и не 
исчерпывает все разнообразие сценариев. Здесь человек или приложение, которым пользуется человек 
отправляет запрос на сервер и получается ответ. В случае если ответ не пришел, будет сообщение
что "запрос прервав по таймауту", т.е. было превышено разумное время, которое можно потратить на 
ожидание ответа. 

.. image:: https://www.altexsoft.com/static/content-image/2024/7/374b1404-54e6-4ba1-8aae-0482237eeb05.webp
  :width: 600
  :alt: "Модель запрос-ответ"

Передача сообщений pub-sub
--------------------------

В интернете вещей более чато используется модель publisher-subscriber (**поставщик** данных - **потребитель** данных). 
Мы можем заметить, что в названии этой модели нет сервера (спойлер сервер всеже нужен). Это отражает 
смысловую нагрузку, которуюмы вкладываем в эту модель и то как ее используем: нам интересно 
вхаимодействие устройств, которое проихводить данные и устройства, которое эти данные потребляет 
для осуществления, какого либо сценария. Например, датчик говорит что на улице воздух стал гряхным, 
и устройство, которое отвечает за окна, закрывает окно. И хотя сервер, нам здесь не нужен для 
планирования того, что мы хотим сделать, он нужен нам для связи Поставщика и Потребителя. Ниже 
приведен пример, когда у нас есть два Поставщика (слева) и три Потребителя (справа). Посередине
находится сервер, который так же называют **брокером**. Сервер берет на себя роль посредника, между 
Потребителями и Поставщиками, и взависимости от настроек гаранитирует доставку с большей или 
меньшей степенью надежности. Обратите внимение на количество сообщений в системе (конвертиков).
В отсутвии сервера-посредника, Поставщиками пришлось бы отправить данные каждом потребителю,
которому они нужны, а при наличии посредника всего однин раз.

.. image:: https://a.storyblok.com/f/231922/1726x800/3100b5f90a/pub-sub-model.png/m/0x0/
  :width: 800
  :alt: "Модель запрос-ответ"

Может возникнуть вопрос - будут ли все клиенты получать все данные в системе как только они 
подключаться к брокеру. Ответ - нет, и действительно это было бы неразумно. Потребитель будет 
получать только те данные, на которые **подписался** (subscribe). Для того чтобы разделить данные 
внутри внутри сисетмы используются темы (topic). Как только в Тему публикуется сообщение, брокер
пытается отправить его всем Потребителям, которые подписаны на эту Тему. При этом отправляет каждое
сообщение, каждому Потребителю.

.. image:: https://cloud.google.com/static/solutions/images/event-driven-architecture-pubsub-3-pubsub-model.svg
  :width: 800
  :alt: "Topic"

Тема строятся следующим образом: разные уровни разделяются слэшами, в начале и в конце слэш не ставиться. 
Можно построить иерархию на основе планирваки помещения:


.. code-block:: bash

    home/kitchen/light               #топик чтобы узнать включен или выключен свет на кухне
    home/kitchen/luminosity          #топик чтобы узнать освещенность на кухне
    home/kitchen/humidity            #топик чтобы узнать влажность на кухне
    home/livingroom/light            #топик чтобы узнать включен или выключен свет в гостинной
    home/livingroom/luminosity       #топик чтобы узнать освещенность в гостинной
    home/livingroom/flower/humidity  #топик чтобы узнать влажность почвы у цветка в гостиной
    
А можно наоборот вынести типа данные наверх. Это остается на усмотрение разработчика.

.. code-block:: bash

    light/home/kitchen               #топик чтобы узнать включен или выключен свет на кухне
    light/home/livingroom/           #топик чтобы узнать включен или выключен свет в гостинной
    luminosity/home/kitchen          #топик чтобы узнать освещенность на кухне
    luminosity/home/livingroom       #топик чтобы узнать освещенность в гостинной
    humidity/kitchen/home            #топик чтобы узнать влажность на кухне
    humidity/home/livingroom/flower  #топик чтобы узнать влажность почвы у цветка в гостиной
    

Практика
--------

Посмотрим сначала как можно сделать общение по модели pub-sub на ПК, используя python. Как мы помним
у нас есть два вида клиентов - Потребитель и Поставщик. Реализуем каждого из них в отдельном модуле.
Представим, что мы в лаборатории разрабатываем теплицу с датчиками, одинм из которых быть датчик 
освещенности. Мы будет использовать показания датчика для того, чтобы включать дополнительное 
освещение. Назовем Тему для освещенности ``laboratoty/greenhouse/luminosity``, мы будем случайным 
образом генерировать занчения, это будет достаточно для проверки коммуникации. В реальных сценариях
будут отправлять реальные показания датчика. В примере ниже мы используем общедоступный брокер 
``broker.emqx.io``, но можно использоать любой другой или поднять свой собственный, например ``mosquitto``.
Код для генерации данных и отправки поместив в цикл. 

.. code-block:: python

    import time
    from paho.mqtt.client import Client
    from paho.mqtt.enums import CallbackAPIVersion
    import random

    broker="broker.emqx.io"
    luminosity_topic = "laboratory/greenhouse/luminosity"

    # ID is important to broker make sure it is unique. 
    if __name__ == "__main__":
        client= Client(
            callback_api_version = CallbackAPIVersion.VERSION2,
            client_id = f'MY_CLIENT_ID_{random.randint(10000, 99999)}'
        )
        client.connect(broker) 

        for itteration in range(10):
            val = str(random.randint(100, 999))
            client.publish(luminosity_topic, val)
            print(f"Itteration {itteration} publish luminosity - {val} to {luminosity_topic}")
            time.sleep(10)
            
        client.disconnect()


Теперь напишем код для потребителя эти данных. Естественно нам нужно подключиться к тому же брокеру и 
подписать на туже Тему в которую Поставщик отправляет данные. Обратите внимание, что мы заново генерируем
ID клиента, так чтобы оно не пересекалось с ID Поставщик (есть небольшой шанс, что будет сгенерировано 
такое же число, но мы будем надеятся что нам повезет). Так же мы определем функцию ``on_connect`` и подменим 
ей метод ``client.on_connect = on_connect``, для того чтобы получить сообщение о том удалось или нет 
подключиться к брокеру для подписки. Чтобы сделать какое либо действие при получении сообщения нам так же 
необходимо определить функцию ``on_connect`` и подменить ею метод клиента-Потребителя 
``client.on_message = on_message``. В коде поставщика этой функции не было, так как не предполагалось,
что он будет получать сообщения. Пока мы не реализуем какую либо логику и просто логируем информацию о
пришедших данных ``print(f"Received message {data} from topic {topic}")``


.. code-block:: python

    import time
    from paho.mqtt.client import Client, MQTTMessage
    from paho.mqtt.enums import CallbackAPIVersion
    import random

    broker = "broker.emqx.io"
    luminosity_topic = "laboratory/greenhouse/luminosity"
    light_status_topic = "laboratory/greenhouse/light"
    light_state = "off"

    def on_connect(client: Client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", reason_code)

    def on_message(client: Client, userdata, message: MQTTMessage):
        data = str(message.payload.decode("utf-8"))
        topic = message.topic
        print(f"Received message {data} from topic {topic}")

    # ID is important to broker make sure it is unique. 
    if __name__ == "__main__":
        client= Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id = f'MY_CLIENT_ID_{random.randint(10000, 99999)}'
        )
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker) 

        client.connect(broker) 
        client.loop_start() 
        print(f"Subcribing to {luminosity_topic}")
        client.subscribe(luminosity_topic)
        time.sleep(1800)
        client.disconnect()
        client.loop_stop() 

Давайте теперь напишем несколько функций для того, чтобы использовать данные датчика освещенности. 
Мы пока не будем использовать реальное подключение к микроконтроллеру, просто сделаем несколько 
функций дописать которые можно будет позднее под конкретный проект. Функции ``set_light_on()`` и
``set_light_off()`` будут отвечать за отправку команды на включение или выключения света и менять 
состояние ``light_state``. Функция ``process_luminosity_data()`` реализует всю логику управления 
освещением - предположим что мы включаем свет когда стало темно т.е. показания меньше 500 единиц 
и наоборот освещение больше 500 единиц говорит нам о том что свет нужно выключить. Если пришли 
данные по которым мы решаем (условие ``float(data) < 500``), что нужно включить свет и свет 
*еще не включен* (``light_state == "off"``), мы его включаем (вызываем ``set_light_on()``). Наоборот 
если приходять данные, по которым мы решаем, что свет нужно выключить (условие ``float(data) > 500``)
и *свет включен* (``light_state == "on"``) мы его выключаем. Все остальные случаи не приводят к каким
либо действиям (ветка ``else`` в ``process_luminosity_data()``). Добавим также вызов 
``process_luminosity_data`` в ``on_message()`` что выполнить наш сценарий, когда пришли данные.

.. code-block:: python

    import time
    from paho.mqtt.client import Client, MQTTMessage
    from paho.mqtt.enums import CallbackAPIVersion
    import random

    broker = "broker.emqx.io"
    luminosity_topic = "laboratory/greenhouse/luminosity"
    light_status_topic = "laboratory/greenhouse/light"
    light_state = "off"

    def set_light_on() -> str:
        # do stuff
        light_state = "on"
        return light_state

    def set_light_off() -> str:
        # do stuff
        light_state = "off"
        return light_state

    def process_luminosity_data(data: bytes, client: Client):
        global light_state
        data = str(data)
        if float(data) < 500 and light_state == "on":
            print("Setting light off")
            light_state = set_light_off()
            client.publish(light_status_topic, light_state)
            print(f"Published status {light_state} to {light_status_topic}")
        elif float(data) > 500 and light_state == "off":
            print("Setting light on")
            light_state = set_light_on()
            client.publish(light_status_topic, light_state)
            print(f"Published status {light_state} to {light_status_topic}")
        else:
            print("Light state remains the same")

    def on_connect(client: Client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", reason_code)

    def on_message(client: Client, userdata, message: MQTTMessage):
        data = str(message.payload.decode("utf-8"))
        topic = message.topic
        print(f"Received message {data} from topic {topic}")
        if topic == luminosity_topic:
            process_luminosity_data(data, client)

    # ID is important to broker make sure it is unique. 
    if __name__ == "__main__":
        client= Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id = f'MY_CLIENT_ID_{random.randint(10000, 99999)}'
        )
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker) 

        client.connect(broker) 
        client.loop_start() 
        print(f"Subcribing to {luminosity_topic}")
        client.subscribe(luminosity_topic)
        client.publish(light_status_topic, light_state)
        time.sleep(1800)
        client.disconnect()
        client.loop_stop()

На данном этапе наша системы состоит из датчика Поставщика данных (``mqtt_photosensor.py``) и 
актуатора Потребителя данных (``mqtt_light.py``). Если внимательно посмотреть на функцию, которая 
управляет логикой приложения, то можно увидеть что там происходит кое-что еще, а именнно отправка
сообщения в топик ``light_status_topic``. Мы не только потребляем данныев ``mqtt_light.py``, но и 
производим свои - сообщаем в каком состоянии сейчас находится искусственное освещение теплицы. 
**Вопрос: когда это может быть важно?**. 

Давайте соверщим последний в этом материале шаг и напишем мониторинг (``mqtt_monitor.py``), который 
будет собирать данные с системы. Такой модуль может быть полезен для контроля правильности работы 
системы - например мы знаем в каких условиях свет должен включиться (показания меньше 500 и 
предыдущее состояние света выклчено) и знаем, что за этим должно следовать определнное сообщение
("on" в топике "laboratory/greenhouse/light"). Если этого не происходит, то это повод сообщить
администратору системы, что актуатор не прореагировал нужным образом. Т.е. этот модуль собирает 
обратную связь от компонентов системы и агрергирует ее для предоставления пользователю. 

Cоздадим новый модуль ``mqtt_monitor.py``.  

    Мониторинг должен иметь доступ ко всем топиками в нашем случае мы просто продублируем топики 
    из других модулей, но для больших проектов, удобнее вести все топики в модуле ``topics.py`` и 
    импортировать топики из него в других модулях проекта. 

Обратите внимание что мы подписываемся не только на топик ``luminosity_topic`` как мы делали в коде 
управления светом, но и на ``light_status_topic`` (если бы были дургие мы так же пописались на них).
И для иллюстарции того, как нам можеть быть полезен мониторинг напишем код, который будет 


.. code-block:: python

    from paho.mqtt.client import Client, MQTTMessage
    from paho.mqtt.enums import CallbackAPIVersion
    from datetime import datetime, timedelta
    import random

    broker = "broker.emqx.io"

    luminosity_topic = "laboratory/greenhouse/luminosity"
    light_status_topic = "laboratory/greenhouse/light"
    topics = [
        luminosity_topic, 
        light_status_topic
    ]

    states = dict(
        light = "off"
    )

    sensor_data = dict(
        luminosity = 0
    )

    check_states = dict(
        light = (False, datetime.now())
    )

    def on_connect(client: Client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", reason_code)

    def on_message(client: Client, userdata, message: MQTTMessage):
        data = str(message.payload.decode("utf-8"))
        topic = message.topic
        print(f"Received message {data} from topic {topic}")
        if topic == luminosity_topic:
            sensor_data["luminosity"] = float(data)
            check_states["light"] = (True, datetime.now() + timedelta(seconds = 5))
        if topic == light_status_topic:
            states["light"] = data

    def check_light():
        state = states["light"]
        data =  sensor_data["luminosity"]
        if state == "off" and data < 500:
            print("System work normaly, light off")
        elif state == "on" and data > 500:
            print("System work normaly, light on")
        else:
            print(f"Something went wrong. State {state} and data {data}")
        check_states["light"] = (False, datetime.now())

    if __name__ == "__main__":
        # ID is important to broker make sure it is unique. 
        client= Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id = f'MY_CLIENT_ID_{random.randint(10000, 99999)}'
        )
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker) 

        client.connect(broker) 
        client.loop_start() 
        for topic in topics:
            print(f"Subcribing to {topic}")
            client.subscribe(topic)
        while True:
            try:
                for actuator, (need_check, check_time) in check_states.items():
                    if need_check and check_time < datetime.now():
                        if actuator == "light":
                            check_light()
                        # other check here
            except KeyboardInterrupt:
                print("Monitoring finisshed....")
                break

        client.disconnect()
        client.loop_stop()