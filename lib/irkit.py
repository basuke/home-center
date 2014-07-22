import json
import urllib2
import logging
from zeroconf import ServiceBrowser, Zeroconf
from time import sleep
from socket import inet_ntoa
import threading


class IRKit(object):
    class DeviceObserver(object):
        """
        Observing IRKit device IP using ZeroConf and update IRKit's IP address
        """
        def __init__(self, device):
            self.device = device
            self.browser = ServiceBrowser(Zeroconf(), "_irkit._tcp.local.", self)

        def addService(self, zeroconf, type, name):
            info = zeroconf.getServiceInfo(type, name)
            if info is None:
                return

            device = self.device

            wasReady = device.isReady()

            device.address = inet_ntoa(info.getAddress())
            device.server = info.server
            device.port = info.port
            
            if not wasReady:
                if device.onReady:
                    device.onReady(device)

        def removeService(self, zeroconf, type, name):
            pass

    class CommandSender(threading.Thread):
        """
        Send command in background thread.
        """
        def __init__(self, irkit, domain, command, success_condition):
            threading.Thread.__init__(self)
            self.irkit = irkit
            self.domain = domain
            self.command = command
            self.success_condition = success_condition

        def run(self):
            irkit = self.irkit
            success_condition = self.success_condition

            data = irkit.getCommand(self.domain, self.command)
            if data is None:
                return

            url = "http://%s/messages" % (irkit.address, )
            data = json.dumps(data)

            def send():
                try:
                    urllib2.urlopen(url, data)
                except Exception as e:
                    logging.warning(str(e))

            if success_condition:
                n = 0
                trial = 1
                while not success_condition():
                    if n % 4 == 0:
                        logging.debug("Sending %s:%s Signal, trial %d" % (self.domain, self.command, trial))
                        send()
                        trial += 1
                    sleep(0.3)
                    n += 1
                logging.info("Sent %s:%s signal" % (self.domain, self.command))
            else:
                logging.info("Send %s:%s signal" % (self.domain, self.command))
                send()

    def __init__(self):
        self.onReady = None
        self.observer = None

        self.address = None
        self.server = None
        self.port = None
        self.commands = dict()

    def isReady(self):
        return self.address is not None

    def defineCommand(self, domain, command, data):
        commands = self.commands.get(domain)
        if not commands:
            self.commands[domain] = commands = dict()

        commands[command] = data

    def getCommand(self, domain, command):
        commands = self.commands.get(domain)
        if not commands:
            logging.warning("Unknown domain " + domain)
            return

        data = commands.get(command)
        if not data:
            logging.warning("Unknown command %s for domain %s" % (command, domain))
            return

        return data

    def send(self, domain, command, success_condition):
        if self.address is None:
            logging.warning("IRKit is not discovered yet")
            return

        self.CommandSender(self, domain, command, success_condition).start()

    def start(self):
        """ start discovering IRKit device """
        self.observer = self.DeviceObserver(self)


