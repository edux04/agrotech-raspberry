AgroTech Sistema de Monitoreo

Este es un sistema de monitoreo desarrollado para AgroTech que utiliza Raspberry Pi para leer datos de temperatura, humedad y detectar la presencia de agua. Los datos se almacenan en Firebase Firestore y se controla una bomba en función de la detección de agua.
Instalación

    Raspberry Pi: Asegúrate de tener una Raspberry Pi configurada y conectada a Internet.

    Python y Librerías: Instala Python y las librerías necesarias. Puedes hacerlo ejecutando:

    bash

    pip install RPi.GPIO Adafruit_DHT gpiozero firebase-admin

    Firebase: Configura un proyecto en Firebase y descarga el archivo JSON de credenciales. Asegúrate de nombrarlo como "agrotech_key.json" y colócalo en la misma carpeta que tu script.

    Configuración de Pines GPIO: Conecta los sensores y dispositivos a los pines GPIO especificados en tu script.

Uso

Ejecuta el script Python en tu Raspberry Pi:

bash

python nombre_del_script.py

Este script monitorea la temperatura, humedad y la presencia de agua, y controla una bomba en función de la detección de agua. Además, guarda los datos en tiempo real en Firebase Firestore.
Estructura del Proyecto

    agrotech_key.json: Archivo de credenciales de Firebase.
    nombre_del_script.py: Script principal que controla la lógica del sistema.

Dependencias

    RPi.GPIO: Controla los pines GPIO de la Raspberry Pi.
    Adafruit_DHT: Interfaz para los sensores DHT.
    gpiozero: Biblioteca para la interacción con pines GPIO.
    firebase-admin: SDK de administración de Firebase para Python.
