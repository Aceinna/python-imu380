import io
import os
import random
import time
import uuid
import datetime
import json
import requests
import urllib2

from azure.storage.blob import AppendBlobService
from azure.storage.blob import ContentSettings

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

    def write_to_azure(self):
        if not self.internet_on(): 
            return False

        # record file to cloud
        self.append_blob_service = AppendBlobService(account_name='navview', account_key='+roYuNmQbtLvq2Tn227ELmb6s1hzavh0qVQwhLORkUpM0DN7gxFc4j+DF/rEla1EsTN2goHEA1J92moOM/lfxg==', protocol='http')
        self.append_blob_service.create_blob(container_name='data', blob_name=self.name,  content_settings=ContentSettings(content_type='text/plain'))
        f = open("data/" + self.name,"r")
        self.append_blob_service.append_blob_from_text('data',self.name, f.read())

        # TODO: check if success

        # record record to ansplatform
        self.record_to_ansplatform()


    def record_to_ansplatform(self):
        data = { "unit" : "1234", "mode" : "S1", "url" : self.name, "userId" : 1 }
        url = "https://ans-platform.azurewebsites.net/api/datafiles/replaceOrCreate"
        data_json = json.dumps(data)
        headers = {'Content-type': 'application/json', 'Authorization' : 'Gmv1uXxMYdcDpqNMTJQLy4eicicCWNCRWv9r21aK7sWdauVVUQvxmCcR7S7xCbHq' }
        response = requests.post(url, data=data_json, headers=headers)
        response = response.json()
        print(response)

    def internet_on(self):
        try:
            urllib2.urlopen('https://ans-platform.azurewebsites.net', timeout=1)
            return True
        except urllib2.URLError as err: 
            return False

    def close(self):
        self.file.close()
        self.write_to_azure()
        self.name = ''
