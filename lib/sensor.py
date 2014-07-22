import RPi.GPIO as GPIO
import logging


class TVPowerObserber(object):
    def __init__(self, channel):
        self.channel = channel
        GPIO.setup(channel, GPIO.IN)
        self.powerState = self.readPowerState()
        self.onStateChange = None

    def run(self):
        self.publish()
        GPIO.add_event_detect(self.channel, GPIO.BOTH, callback=self.on_change, bouncetime=300)

    def readPowerState(self):
        return GPIO.input(self.channel) == GPIO.LOW

    def on_change(self, channel):
        old_state = self.powerState
        self.powerState = self.readPowerState()
        if old_state != self.powerState:
            self.publish()

    def publish(self):
        if self.onStateChange:
            self.onStateChange(self, self.powerState)


