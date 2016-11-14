import RPi.GPIO as GPIO
import time

import socket
import sys

import traceback

import paho.mqtt.client as mqtt
from threading import Thread


class PowerMeterSource:
    gpio = None
    topic = None
    worker = None
    callback = None
    timestamp = time.time()
    last_value = 1

    def __init__(self, gpio, topic, callback):
        self.gpio = gpio
        self.topic = topic
        self.callback = callback
        self.worker = Thread(target=self.start)
        self.worker.setDaemon(True)
        self.worker.start()

    def start(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio, GPIO.IN)
        while True:
            value = GPIO.input(self.gpio)
            if value == 0 and self.last_value != 0:
                difference = time.time() - self.timestamp
                power = round(3600 / difference, 2)
                self.callback(self.topic, power)
                self.timestamp = time.time()
            self.last_value = value
            time.sleep(0.001)


class PowerMeterLogger:
    config = None
    mqtt_client = None
    mqtt_connected = False

    def __init__(self, config):
        self.config = config

    def verbose(self, message):
        if self.config and 'verbose' in self.config and self.config['verbose'] == 'true':
            sys.stdout.write('VERBOSE: ' + message + '\n')
            sys.stdout.flush()

    def error(self, message):
        sys.stderr.write('ERROR: ' + message + '\n')
        sys.stderr.flush()

    def mqtt_connect(self):
        if self.mqtt_broker_reachable():
            self.verbose('Connecting to ' + self.config['mqtt_host'] + ':' + self.config['mqtt_port'])
            self.mqtt_client = mqtt.Client(self.config['mqtt_client_id'])
            if 'mqtt_user' in self.config and 'mqtt_password' in self.config:
                self.mqtt_client.username_pw_set(self.config['mqtt_user'], self.config['mqtt_password'])

            self.mqtt_client.on_connect = self.mqtt_on_connect
            self.mqtt_client.on_disconnect = self.mqtt_on_disconnect

            try:
                self.mqtt_client.connect(self.config['mqtt_host'], int(self.config['mqtt_port']), 10)
                self.mqtt_client.loop_forever()
            except:
                self.error(traceback.format_exc())
                self.mqtt_client = None
        else:
            self.error(self.config['mqtt_host'] + ':' + self.config['mqtt_port'] + ' not reachable!')

    def mqtt_on_connect(self, mqtt_client, userdata, flags, rc):
        self.mqtt_connected = True
        self.verbose('...mqtt_connected!')

    def mqtt_on_disconnect(self, mqtt_client, userdata, rc):
        self.mqtt_connected = False
        self.verbose('Diconnected! will reconnect! ...')
        if rc is 0:
            self.mqtt_connect()
        else:
            time.sleep(5)
            while not self.mqtt_broker_reachable():
                time.sleep(10)
            self.mqtt_client.reconnect()

    def mqtt_broker_reachable(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        try:
            s.connect((self.config['mqtt_host'], int(self.config['mqtt_port'])))
            s.close()
            return True
        except socket.error:
            return False

    def start_sources(self):
        for source in self.config['sources']:
            PowerMeterSource(int(source['gpio']), source['topic'], self.publish_power)

    def publish_power(self, topic, power):
        if self.mqtt_connected:
            self.verbose('Publishing: ' + str(power))
            self.mqtt_client.publish(topic, str(power), 0, True)

    def start(self):
        self.start_sources()
        self.mqtt_connect()
