import json
import requests
import pprint
from azure.storage.blob import AppendBlobService
from azure.storage.blob import ContentSettings

        
append_blob_service = AppendBlobService(account_name='navview', account_key='+roYuNmQbtLvq2Tn227ELmb6s1hzavh0qVQwhLORkUpM0DN7gxFc4j+DF/rEla1EsTN2goHEA1J92moOM/lfxg==', protocol='http')
append_blob_service.create_blob(container_name='data', blob_name="data-2018_05_04_13_13_24.csv",  content_settings=ContentSettings(content_type='text/plain'))
f = open("data/data-2018_05_04_13_13_24.csv" ,"r")
append_blob_service.append_blob_from_text('data',"data-2018_05_04_13_13_24.csv", f.read())