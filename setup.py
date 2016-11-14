# -*- coding: utf-8 -*-
from setuptools import setup


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='rpi-power-meter-mqtt',
    version='0.0.1',
    description='Send current power consumption of a power meters to mqtt broker',
    long_description=readme,
    author='David Uebelacker',
    author_email='david@uebelacker.ch',
    url='https://github.com/goodfield/rpi-power-meter-mqtt.git',
    license=license,
    packages=['rpi_power_meter_mqtt'],
    install_requires=['paho-mqtt'],
    scripts=['bin/rpi-power-meter-mqtt']
)
