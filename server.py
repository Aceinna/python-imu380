import tornado.httpserver
import tornado.websocket
import tornado.ioloop
from tornado.ioloop import PeriodicCallback
import tornado.web
import json
import time
import math
import imu380
import threading
import Tkinter
import tkMessageBox

server_version = '0.1 Beta'

class WSHandler(tornado.websocket.WebSocketHandler):
            
    def get_time(self):
        self.__time += 1
        return self.__time
        self.__start = 0

    def open(self):
        self.__time = 1
        self.__start = 1
        self.callback = PeriodicCallback(self.send_data, 33.3)
        self.callback.start()
        
    def send_data(self):
        if self.__start:
            d = imu.get_latest()
            d['time'] = self.get_time()
            str = json.dumps(d)
            str.encode()
            self.write_message(str)

    def on_message(self, message):
        global imu
        if message == 'status':
            self.write_message(json.dumps({ 'status' : server_version, 'odr' : imu.odr_setting, 'device_id' : imu.device_id  }))
        elif message == 'start_log' and imu.logging == 0:
            imu.start_log()
            self.write_message(json.dumps({ 'logfile' : imu.logger.name }))
        elif message == 'stop_log' and imu.logging == 1:
            imu.stop_log()
            self.write_message(json.dumps({ 'logfile' : '' }))
        else:
            message = json.loads(message)
            if message['cmd'] == "GF":
                data = imu.get_fields(message['data'], True)
                print('get fields')
                print(data)
                self.write_message(json.dumps({"cmd" : "GF", "data": data}))
            elif message['cmd'] == "RF":
                data = imu.read_fields(message['data'], True)
                print('read fields')
                print(data)
                self.write_message(json.dumps({"cmd" : "RF", "data": data}))
            elif message['cmd'] == "SF":
                data = imu.set_fields(message['data'], True)
                print('set fields')
                print(message['data'])
                print(data)
                self.write_message(json.dumps({"cmd" : "SF", "data": data}))
            elif message['cmd'] == "WF":
                data = imu.write_fields(message['data'], True)
                print('write fields')
                print(message['data'])
                print(data)
                self.write_message(json.dumps({"cmd" : "WF", "data": data}))
            




    def on_close(self):
        self.__start = 0
        # imu.disconnect()

    def check_origin(self, origin):
        return True
 
if __name__ == "__main__":
    application = tornado.web.Application([(r'/', WSHandler),])
    imu = imu380.GrabIMU380Data(ws=True)
    threading.Thread(target=imu.stream).start()
    print('starting web socket server')
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()