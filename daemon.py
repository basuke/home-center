import sys
sys.path.append('lib')

from messaging import MessageCenter, ON, OFF
from sensor import TVPowerObserber
from irkit import IRKit

import RPi.GPIO as GPIO
import json
import logging
import os

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

# GPIO setup
GPIO.setmode(GPIO.BOARD)

# TV topic and payload
TV = "home/living/tv"

# MessageCenter

client_id = "%s.%s.%d" % ("desk-pi", sys.argv[0], os.getpid())
message_center = MessageCenter(client_id)

def handle_message(topic, payload):
    TV_REQUEST = TV + "/req"

    if topic == TV_REQUEST:
        request = payload
        state = ON if tv.powerState else OFF

        if request not in [ON, OFF]:
            logging.info("Invalid TV POWER request '%s'" % (request, ))
            return

        logging.debug("TV POWER request '%s' on state '%s'" % (request, state))

        if request != state:
            irkit.send('sony_tv', 'power_on_off', lambda: tv.powerState == (request == ON))

message_center.onMessage = handle_message

# IRKit

irkit = IRKit()
irkit.defineCommand('sony_tv', 'power_on_off', json.loads('{"freq":38,"data":[4713,1111,2451,1111,1232,1111,2451,1111,1232,1111,2451,1111,1232,1111,1232,1111,2451,1111,1232,1111,1232,1111,1232,1111,1232,50610,4713,1111,2451,1111,1232,1111,2451,1111,1232,1111,2451,1111,1232,1111,1232,1111,2451,1111,1232,1111,1232,1111,1232,1111,1232,50610,4713,1111,2451,1111,1232,1111,2451,1111,1232,1111,2451,1111,1232,1111,1232,1111,2451,1111,1232,1111,1232,1111,1232,1111,1232,50610,4713,1111,2451,1111,1232,1111,2451,1111,1232,1111,2451,1111,1232,1111,1232,1111,2451,1111,1232,1111,1232,1111,1232,1111,1232,50610,4713,1111,2451,1111,1232,1111,2451,1111,1232,1111,2451,1111,1232,1111,1232,1111,2451,1111,1232,1111,1232,1111,1232,1111,1232,50610,4713,1111,2451,1111,1232,1111,2451,1111,1232,1111,2451,1111,1232,1111,1232,1111,2451,1111,1232,1111,1232,1111,1232,1111,1232],"format":"raw","id":2}'))

def irkit_is_ready(irkit):
    logging.info("IRKit is ready (%s)" % (irkit.server, ))
    message_center.publish("home/irkit/ip", irkit.address)

irkit.onReady = irkit_is_ready

# TV Power Observer

tv = TVPowerObserber(12)

def tv_power_changed(tv, state):
    message_center.publish(TV, ON if state else OFF)
    logging.info("TV POWER " + ("ON" if state else "OFF"))

tv.onStateChange = tv_power_changed


if __name__ == '__main__':
    logging.info("Launching.")
    
    irkit.start()
    tv.run()

    message_center.runloop()

