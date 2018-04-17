import io
import os
import random
import time
import uuid
import datetime
import json

class LogIMU380Data:
    
    def __init__(self):
        '''Initialize and create a CSV file
        '''
        self.name = 'data-' + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '.csv'
        self.file = open('data/' + self.name, 'w')
        self.first_row = 0

    def log(self, data, odr_setting): 
        '''Write row of CSV file based on data received.  Uses dictionary keys for column titles
        '''
        odr_rates = { 0: 0, 1 : 100, 2 : 50, 4 : 25  }
        delta_t = 1.0 / odr_rates[odr_setting]

        if not self.first_row:
            self.first_row = 1
            header = ''.join('{0:s},'.format(key) for key in data)
            header = header[:-1]
            header = 'sample,' + header
            header = header + '\r\n'
        else:
            self.first_row += 1
            header = ''
        
        str = ''
        for key in data:
            if key == 'BITstatus' or key == 'GPSITOW' or key == 'counter' or key == 'timeITOW':
                str += '{0:d},'.format(data[key])
            else:
                str += '{0:3.5f},'.format(data[key])
        str = str[:-1]
        str = '{0:5.2f},'.format(delta_t * (self.first_row - 1)) + str
        str = str + '\r\n'
        self.file.write(header+str)
    
    def close(self):
        self.file.close()
        self.name = ''
