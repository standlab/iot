Интерактивная коммуникация
==========================

Вводные
-------

Часто микроконтроллеры используются в автономном режиме, когда загруженная прошивка работает без участия человека или 
управляющего устройства, например более мощного компьютера. В этом случае работает прошивка, которая ориентируется на 
показания датчиков для совершения каких-то действий, или просто работает по расписанию. Например как простой сфетофор,
цикл переключения зеленый-желтый красный в котором фиксирован. Но часто требуется интерактивное управление 
микроконтроллером и нужно разработать прошивку с учетом, такой возможности.   


Serial
------

Первый и универсальный способ общения с микроконтроллером это UART, который в Arduino IDE можно использовать через класс.
Рассмотрим стадартный пример Blink и добавим в него интерактивности.

.. code-block:: c++

  void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
  }

  void loop() {
    digitalWrite(LED_BUILTIN, HIGH);  
    delay(1000);                      
    digitalWrite(LED_BUILTIN, LOW);   
    delay(1000);                      
  }

В коде ниже мы уже используем `Serial` для отправки инфолрмации с микроконтроллера на ПК, но не обратно.

.. code-block:: c++

  // adding Serial.begin(9600) to begin communicate, 9600 is speed
  // adding Serial.println() to send string to PC

  void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    Serial.begin(9600);                                            // new line
  }

  void loop() {
    digitalWrite(LED_BUILTIN, HIGH);  
    Serial.println("Led should be ON if it is direct polarity");   // new line
    delay(1000);                      
    digitalWrite(LED_BUILTIN, LOW);   
    Serial.println("Led should be OFF if it is direct polarity");  // new line
    delay(1000);                      
  }


.. code-block:: c++

  // adding Serial.available() to see if user send a command
  // adding Serial.read() to read one symbol (byte) from PC
  // adding conditions to process user commands

  const char CMD_ON = 'u';
  const char CMD_OFF = 'd';
  const char CMD_BLINK = 'b';
  char cmd = ' ';

  void setup() {
    pinMode(LED_BUILTIN, OUTPUT);
    Serial.begin(9600);                                            
  }

  void loop() {
    if(Serial.available() > 0) {                                      // new line
        cmd = Serial.read();                                          // new line
    }                                                                 // new line
    if(cmd == CMD_ON){                                                // new line
        digitalWrite(LED_BUILTIN, HIGH);                              // new line
        Serial.println("Led should be ON if it is direct polarity");  // new line 
    }                                                                 // new line        
    if(cmd == CMD_OFF){                                               // new line
        digitalWrite(LED_BUILTIN, LOW);                              // new line
        Serial.println("Led should be ON if it is direct polarity");  // new line 
    }                                                                 // new line    
    if(cmd == CMD_BLINK) {                                            // new line
        digitalWrite(LED_BUILTIN, HIGH);  
        Serial.println("Led should be ON if it is direct polarity");  
        delay(1000);                      
        digitalWrite(LED_BUILTIN, LOW);   
        Serial.println("Led should be OFF if it is direct polarity"); 
        delay(1000);           
    }                                                                 // new line      
  }




