import json
import requests
import pprint
from azure.storage.blob import BlockBlobService, PublicAccess, ContentSettings

        
# Create the BlockBlockService that is used to call the Blob service for the storage account
block_blob_service = BlockBlobService(account_name='navview', account_key='+roYuNmQbtLvq2Tn227ELmb6s1hzavh0qVQwhLORkUpM0DN7gxFc4j+DF/rEla1EsTN2goHEA1J92moOM/lfxg==', protocol='http') 

# Create a container called 'quickstartblobs'.
container_name ='quickstartblobs'
block_blob_service.create_container(container_name) 

# Set the permission so the blobs are public.
block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

# List the blobs in the container
print("\nList blobs in the container")
generator = block_blob_service.list_blobs('data')
for blob in generator:
    print("\t Blob name: " + blob.name)