import tornado.websocket
import tornado.ioloop
import tornado.httpserver
from tornado.ioloop import PeriodicCallback
import tornado.web
import json
import time
import math
import imu380
import threading
import Tkinter
import tkMessageBox
import os

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
            self.write_message(json.dumps({ 'messageType' : 'event',  'data' : { 'newOutput' : d }}))

    def on_message(self, message):
        global imu
        message = json.loads(message)
        if message['messageType'] != 'serverStatus':
            self.callback.stop()
            imu.disconnect()
            time.sleep(1)
        if message['messageType'] == 'serverStatus':
            if imu.device_id:
                with open('imu.json') as json_data:
                    imuProperties = json.load(json_data)
                self.write_message(json.dumps({ 'messageType' : 'serverStatus', 'data' : { 'serverVersion' : server_version, 'deviceId' : imu.device_id, 'deviceProperties' : imuProperties }}))
            else:
                self.write_message(json.dumps({ 'messageType' : 'serverStatus', 'data' : { 'serverVersion' : server_version, 'deviceId' : imu.device_id }}))
        elif message['messageType'] == 'requestAction':
            if list(message['data'].keys())[0] == 'getFields':
                data = imu.get_fields(list(map(int,message['data']['getFields'].keys())), True)
                print('get fields new')
                self.write_message(json.dumps({ "messageType" : "requestAction", "data" : { "getFields" : data }}))
                print(data)
            elif list(message['data'].keys())[0] == 'readFields':
                data = imu.read_fields(list(map(int,message['data']['readFields'].keys())), True)
                print('read fields new')
                self.write_message(json.dumps({ "messageType" : "requestAction", "data" : { "readFields" : data }}))
                print(data)
            elif list(message['data'].keys())[0] == 'setFields':
                setData = zip(list(map(int,message['data']['setFields'].keys())), list(map(int,message['data']['setFields'].values())))
                print('set fields new')
                print(setData)
                data = imu.set_fields(setData, True)
                # should be improved to really use data readback in UART protocol, and cross check values set correctly
                self.write_message(json.dumps({ "messageType" : "requestAction", "data" : { "setFields" : setData }}))
            elif list(message['data'].keys())[0] == 'writeFields':
                setData = zip(list(map(int,message['data']['writeFields'].keys())), list(map(int,message['data']['writeFields'].values())))
                print('write fields new')
                print(setData)
                data = imu.write_fields(setData, True)
                # should be improved to really use data readback in UART protocol, and cross check values set correctly
                self.write_message(json.dumps({ "messageType" : "requestAction", "data" : { "writeFields" : setData }}))
            elif list(message['data'].keys())[0] == 'startStream':
                imu.set_quiet()
                imu.restore_odr()
                threading.Thread(target=imu.connect).start()
                self.callback.start()  
            elif list(message['data'].keys())[0] == 'stopStream':
                imu.set_quiet()
            elif list(message['data'].keys())[0] == 'startLog' and imu.logging == 0:
                imu.set_quiet()
                imu.restore_odr()
                threading.Thread(target=imu.connect).start()
                imu.start_log() 
                self.callback.start()  
                self.write_message(json.dumps({ "messageType" : "requestAction", "data" : { "logfile" : imu.logger.name }}))
            elif list(message['data'].keys())[0] == 'stopLog' and imu.logging == 1:
                imu.stop_log()
                imu.set_quiet()
                imu.restore_odr()
                threading.Thread(target=imu.connect).start()
                self.callback.start()                  
                self.write_message(json.dumps({ "messageType" : "requestAction", "data" : { "logfile" : '' }}))
            elif list(message['data'].keys())[0] == 'listFiles':
                imu.set_quiet()
                logfiles = [f for f in os.listdir('data') if os.path.isfile(os.path.join('data', f))]
                self.write_message(json.dumps({ "messageType" : "requestAction", "data" : { "listFiles" : logfiles }}))
            elif list(message['data'].keys())[0] == 'loadFile':
                imu.set_quiet()
                print(message['data']['loadFile']['graph_id'])
                f = open("data/" + message['data']['loadFile']['graph_id'],"r")
                self.write_message(json.dumps({ "messageType" : "requestAction", "data" : { "loadFile" :  f.read() }}))


    def on_close(self):
        self.__start = 0
        # imu.disconnect()

    def check_origin(self, origin):
        return True
 
if __name__ == "__main__":
    application = tornado.web.Application([(r'/', WSHandler)])
    imu = imu380.GrabIMU380Data(ws=True)
    threading.Thread(target=imu.stream).start()
    print('starting web socket server')
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()