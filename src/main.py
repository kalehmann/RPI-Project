#! /usr/bin/env python

import RPi.GPIO as gpio
import ConfigParser
import os
import time
import errno
import sys
import signal

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

class Context(object):
    def __init__(self, config):
        self.config = config
        self.logfile = open(config.get("global", "logfile"), "a+")
        self.door_controller = None
        self.pidpath = None

    def log(self, tolog):
        self.logfile.write("%s : %s \n" % (time.asctime(), tolog))

    def updateLogfile(self):
        self.logfile.close()
        self.logfile = open(self.config.get("global", "logfile"), "a+")

    def cleanup(self):
        self.log("Shuting service down.")
        self.logfile.close()
        if self.pidpath:
            os.remove(self.pidpath)

    def getPidFromFile(self):
        self.pidpath = context.config.get("global", "pidfile")
        if os.path.isfile(self.pidpath):
            try:
                pidfile = open(self.pidpath, "r")
                pid = int(pidfile.read())
                pidfile.close()
                return pid
            except ValueError:
                self.log("Error! Could not read pid from pidfile %s" %
                          self.pidpath)
        return -1

    def registerPid(self):
        pid = self.getPidFromFile()
        if pid > 0:
            try:
                os.kill(pid, 0)
                return False
            except OSError as err:
                if err.errno == errno.EPERM:
                    # Process runnig, but we have no access to it
                    return False
        pidfile = open(self.pidpath, "w+")
        pidfile.write(str(os.getpid()))
        pidfile.close()
        return True

    def setupDoorController(self):
        self.door_controller = DoorController(self)
        if self.config.getboolean("doorsensor", "use_door_sensor"):
            exec_opened_closed = (
                self.config.get("doorsensor", "execute_on_opened"),
                self.config.get("doorsensor", "execute_on_closed"))
            self.door_controller.setDoorSensor(self.config.getint(
                "doorsensor", "door_sensor_gpio"), exec_opened_closed)
        if self.config.getboolean("servo_lock", "use_servo_lock"):
            self.door_controller.setServoLock(
                self.config.getint("servo_lock", "servo_gpio"),
                self.config.getint("servo_lock", "frequency"),
                self.config.getfloat("servo_lock", "duty_cycle_open"),
                self.config.getfloat("servo_lock", "duty_cycle_closed"),
                self.config.getfloat("servo_lock", "open_close_time"))

class DoorController(object):
    def __init__(self, context):
        self.use_door_sensor = False
        self.use_servo_lock = False
        self.door_opened = ""
        self.door_closed = ""
        self.context = context

    def setDoorSensor(self, sensor_gpio, exec_open_close):
        self.use_door_sensor = True
        self.sensor_gpio = sensor_gpio
        gpio.setmode(gpio.BCM)
        gpio.setup(self.sensor_gpio, gpio.IN, pull_up_down=gpio.PUD_UP)
        gpio.add_event_detect(self.sensor_gpio, gpio.BOTH,
                              self._doorCallback)
        self.door_opened = exec_open_close[0]
        self.door_closed = exec_open_close[1]

    def setServoLock(self, servo_gpio, frequency, duty_cycle_open,
                     duty_cycle_closed, open_close_time):
        self.use_servo_lock = True
        self.servo_gpio = servo_gpio
        gpio.setmode(gpio.BCM)
        gpio.setup(self.servo_gpio, gpio.OUT)
        self.servo_pwm = gpio.PWM(self.servo_gpio, frequency)
        self.servo_pwm.start(0)
        self.dcopen = duty_cycle_open
        self.dcclosed = duty_cycle_closed
        self.open_close_time = open_close_time

    def openDoor(self):
        if self.use_servo_lock:
            self.servo_pwm.ChangeDutyCycle(self.dcopen)
            time.sleep(self.open_close_time)
            self.servo_pwm.ChangeDutyCycle(0)
        else:
            self.context.log(
                "Warning! Attemp to open door before initializing servo lock.")

    def closeDoor(self):
        if self.use_servo_lock:
            self.servo_pwm.ChangeDutyCycle(self.dcclosed)
            time.sleep(self.open_close_time)
            self.servo_pwm.ChangeDutyCycle(0)
        else:
            self.context.log(
                "Warning! Attemp to close door before initializing servo lock.")

    def isDoorOpen(self):
        if self.use_door_sensor:
            if gpio.input(self.sensor_gpio):
                return True
            else:
                return False
        else:
            self.context.log(
                "Warning! Attemp to access door state without sensor.")
            

    def _doorCallback(self, channel):
        path = (self.door_opened if gpio.input(self.sensor_gpio)
                                 else self.door_closed)
        files = [os.path.join(path,fn) for fn in next(os.walk(path))[2]]
        for f in files:
            os.system(f)

class BierHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if "doorstate" in self.path:
            context.log("GET doorstate from %s" % self.client_address[0])
            self.send_response(200)
            self.send_header("Content-type", "text-html")
            self.end_headers()
            self.wfile.write("Open" if context.door_controller.isDoorOpen() else
                             "Closed")
        elif "open_door" in self.path:
            context.log("GET open_door from %s" % self.client_address[0])
            self.send_response(200)
            self.send_header("Content-type", "text-html")
            self.end_headers()
            context.door_controller.openDoor()
        elif "close_door" in self.path:
            context.log("GET open_door from %s" % self.client_address[0])
            self.send_response(200)
            self.send_header("Content-type", "text-html")
            self.end_headers()
            context.door_controller.closeDoor()

def start_service(context):
    # context.registerPid() returns false, if there is already an instance of
    # this service.
    if not context.registerPid():
        context.log("Error! Attempt to start this service twice.")
        return None
    context.log("Starting doorcontrollerservice")
    context.setupDoorController()

    addr = ""
    if context.config.getboolean("webapi", "local_access_only"):
        addr = "127.0.0.1"
    
    server_address = (addr, context.config.getint("webapi", "port"))
    httpd = HTTPServer(server_address, BierHTTPRequestHandler)
    context.log("Starting server on port %d" % server_address[1])
    httpd.serve_forever()  

if __name__ == "__main__":           

    try:
        start_config = ConfigParser.RawConfigParser()
        start_config.read("/opt/doorcontrollerservice/default_start_config")
        start_config.read("/etc/default/doorcontrollerservice")

        config = ConfigParser.RawConfigParser()
        config_path = start_config.get("default", "config")
        config.read("/opt/doorcontrollerservice/default_config")
        context = Context(config)
        try:
            context.config.read(config_path)
            context.updateLogfile()
        except Exception as err:
            context.log("Error! %s" % err)

        if len(sys.argv) > 1:
            if sys.argv[1] in ("stop", "--stop", "restart", "--restart"):
                pid = context.getPidFromFile()
                if pid > 0:
                    os.kill(pid, signal.SIGTERM)
                if sys.argv[1] in ("stop", "--stop"):
                    sys.exit()
                
        if start_config.getboolean("default", "enabled"):
            start_service(context)
    except Exception as error:
        if locals().has_key("context"):
            context.log("Error! %s" % error)
            context.cleanup()
