import os
import sys
import traceback
import hvac
import psycopg2
import psycopg2.extras
from pymongo import MongoClient
import numpy as np

APPNAME = os.environ.get("APPNAME")

ssl_verify = os.environ.get('SSL_VERIFY')=="true"
vault_url = os.environ.get('VAULT_URL')
vault_token = os.environ.get('VAULT_TOKEN')
client = hvac.Client(url=vault_url,verify=ssl_verify)
client.token = vault_token
response = client.read(f'secret/{APPNAME}')
mongo_uri = response['data']['docstoreDBurl']
mongo_client = MongoClient(mongo_uri)
collection = mongo_client.docstore.reportstore

def myquery():

    mylist = []
    query_key = {"ok"}
    fetched = collection.find(query_key)
    for row in fetched:
        if 'thumbnails' in row.keys():
            for k,v in row['thumbnails'].items():
                item = {}
                item.update(row['aaa'])
                item['abc']=k
                item['abc_path']=v
                mylist.append(item)

    return mylist
    
if __name__ == "__main__":
    myquery()
    print("done")

"""

python utils.py

"""
