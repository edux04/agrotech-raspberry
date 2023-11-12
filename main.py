import RPi.GPIO as GPIO
import Adafruit_DHT
from gpiozero import DigitalInputDevice
import time
import threading

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Load Firebase credentials from the JSON file
cred = credentials.Certificate("agrotech_key.json")
firebase_admin.initialize_app(cred)

# Create a Firestore client
db = firestore.client()

# Reference to the Firestore collection and create a new document
dht11_ref = db.collection('dht11_data').document()
moisture_ref = db.collection('moisture_sensor').document()
bomba_ref = db.collection('bomba').document()

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

# Variable para el control de la bomba y el lock para sincronización
bomba_encendida = False
lock = threading.Lock()

# Función para controlar la bomba y registrar eventos
def controlar_bomba(encendida):
    global bomba_encendida

    with lock:
        GPIO.output(pin_relay, GPIO.HIGH if encendida else GPIO.LOW)
        estado = "Encendida" if encendida else "Apagada"

        # Registra el evento solo si hay un cambio en el estado
        if bomba_encendida != encendida:
            bomba_ref.set({
                'estado': estado,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            print(f"Bomba {estado}")

        bomba_encendida = encendida

# Función para detectar temperatura y humedad cada minuto
def monitorear_temperatura_humedad():
    while True:
        # Leer la temperatura y la humedad
        humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)

        if humidity is not None and temperature is not None:
            print("Temperatura={0:0.1f}°C Humedad={1:0.1f}%".format(temperature, humidity))

            # Set the data in the document
            dht11_ref.set({
                'temperature': temperature,
                'humidity': humidity,
                'moisture': not MOISTURE_SENSOR.value,  # Reverse the moisture value
                'timestamp': firestore.SERVER_TIMESTAMP
            })
        else:
            print("No se pudo leer la temperatura")

        time.sleep(60)  # Espera 60 segundos antes de la próxima lectura

# Inicia el hilo para monitorear temperatura y humedad
thread_temperatura_humedad = threading.Thread(target=monitorear_temperatura_humedad)
thread_temperatura_humedad.start()

print("AgroTech Sistema de Monitoreo")

try:
    while True:
        if not MOISTURE_SENSOR.value:
            print("Agua detectada")

            # Registra el evento de detección de agua
            moisture_ref.set({
                'estado': 'Se detectó agua',
                'timestamp': firestore.SERVER_TIMESTAMP
            })

            bomba_encendida = False  # Apagar la bomba cuando se detecta agua
            controlar_bomba(bomba_encendida)

        else:
            print("No se detecta agua")

            # Registra el evento de no detección de agua
            moisture_ref.set({
                'estado': 'No se detectó agua',
                'timestamp': firestore.SERVER_TIMESTAMP
            })

            bomba_encendida = True  # Encender la bomba cuando no se detecta agua
            controlar_bomba(bomba_encendida)

        time.sleep(2)

except KeyboardInterrupt:
    GPIO.cleanup()