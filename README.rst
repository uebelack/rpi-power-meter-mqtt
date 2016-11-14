Power Meter Logger for Raspberry Pi
=============================

Reads the led impulses of a power meter (Tested with Echelon 83320 from IWB, Basel) via light sensor, calculates the current power consumption and sends it to a mqtt broker.


Installation:
-------------------

    pip install rpi-power-meter-mqtt

Configuration:
-------------------

Needs a json configuration file as follows (don't forget to change ip's and credentials ;-)):

.. code:: json

    {
        "mqtt_client_id": "power_meter",
        "mqtt_host": "192.168.0.210",
        "mqtt_port": "1883",
        "sources": [
            {
              "gpio": "4",
              "topic": "halti/david/power_consumption"
            },
            {
              "gpio": "17",
              "topic": "halti/stweg/power_consumption"
            }
          ]
    }



Start:
-------------------

    rpi-power-meter-mqtt config.json
