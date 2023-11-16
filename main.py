User
import RPi.GPIO as GPIO
import Adafruit_DHT
from gpiozero import DigitalInputDevice
import time
import threading
from datetime import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Load Firebase credentials from the JSON file
cred = credentials.Certificate("agrotech_key.json")
firebase_admin.initialize_app(cred)

# Create a Firestore client
db = firestore.client()

# Configuración de los pines GPIO
pin_relay = 23
moisture_pin = 26
DHT_PIN = 14

# Identificamos sensores
DHT_SENSOR = Adafruit_DHT.DHT11
MOISTURE_SENSOR = DigitalInputDevice(moisture_pin)

# Inicialización de los pines GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_relay, GPIO.OUT)

# Variable para controlar la ejecución del bucle
running = True

# Función para controlar la bomba y registrar eventos
def controlar_bomba(encendida):
    GPIO.output(pin_relay, GPIO.HIGH if encendida else GPIO.LOW)
    estado = "Encendida" if encendida else "Apagada"

    # Crear un nuevo documento para registrar el evento de encendido o apagado
    bomba_ref = db.collection('bomba').document()
    bomba_ref.set({
        'estado': estado,
        'timestamp': firestore.SERVER_TIMESTAMP
    })

    print(f"Bomba {estado}")

# Función para leer la temperatura y actualizar Firestore
def monitorear_temperatura():
    while running:
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)

        if humidity is not None and temperature is not None:
            print("Temperatura={0:0.1f}°C Humedad={1:0.1f}%".format(temperature, humidity))

            # Crear un nuevo documento para cada lectura
            dht11_ref = db.collection('dht11_data').document()
            dht11_ref.set({
                'temperature': temperature,
                'humidity': humidity,
                'moisture': not MOISTURE_SENSOR.value,  # Reverse the moisture value
                'timestamp': firestore.SERVER_TIMESTAMP
            })

            time.sleep(60)  # Esperar 1 minuto
        else:
            print("No se pudo leer la temperatura")

# Hilo para monitorear la temperatura
temperature_thread = threading.Thread(target=monitorear_temperatura)

print("AgroTech Sistema de Monitoreo")

try:
    # Iniciar el hilo de monitoreo de temperatura
    temperature_thread.start()

    while True:
        if not MOISTURE_SENSOR.value:
            print("Agua detectada")

            # Crear un nuevo documento para registrar el evento de detección de agua
            moisture_ref = db.collection('moisture_sensor').document()
            moisture_ref.set({
                'estado': 'Se detectó agua',
                'timestamp': firestore.SERVER_TIMESTAMP
            })

            bomba_encendida = False  # Apagar la bomba cuando se detecta agua
            controlar_bomba(bomba_encendida)
            time.sleep(30)  # Esperar 30 segundos antes de verificar nuevamente
        else:
            print("No se detecta agua")

            # Crear un nuevo documento para registrar el evento de no detección de agua
            moisture_ref = db.collection('moisture_sensor').document()
            moisture_ref.set({
                'estado': 'No se detectó agua',
                'timestamp': firestore.SERVER_TIMESTAMP
            })

            bomba_encendida = True  # Encender la bomba cuando no se detecta agua
            controlar_bomba(bomba_encendida)

        time.sleep(2)

except KeyboardInterrupt:
    running = False  # Detener el hilo de monitoreo de temperatura
    GPIO.cleanup()
    temperature_thread.join()  # Esperar a que el hilo termine