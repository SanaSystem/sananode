from celery import shared_task, task
from .blockchain import *
import requests
import json
@shared_task
def add(x,y):
    return x+y
def remove_duplicates(decomposed_list):
    decomp_set = set() 
    for e in decomposed_list:
        decomp_set.add(json.dumps(e, sort_keys=True))
    print("Found {} duplicates".format(len(decomposed_list) - len(decomp_set)))
    return [json.loads(i) for i in decomp_set]

def decompose_medblocks(list_of_medblocks):
    decomposed = []
    for m in list_of_medblocks:
        medblock = m
        _id = medblock.pop('_id')
        body = {
            'id':_id,
            'tag':'body',
            'creator':medblock.pop('creator'),
            'format': medblock.pop('format'),
            'recipient':medblock.pop('recipient'),
            'title':medblock.pop('title')
        }
        decomposed.append(body)
        keys = medblock.pop('keys')
        for key in keys:
            k = {
                'id':_id,
                'tag':'key',
                'data': json.dumps(key),
                'recipient': body['recipient']
            }
            decomposed.append(k)
        
        files = medblock.pop('files')
        for file in files:
            f = {
                'id':_id,
                'tag':'file',
                'data':json.dumps(file),
                'recipient': body['recipient']
            }
            decomposed.append(f)
        other_keys = medblock.keys()
        # print("Medblock: {}\nOther keys: {}".format(_id, other_keys))
        for key in other_keys:
            element = medblock[key]
            frag = {
                'id':_id,
                'tag':key,
                'data':json.dumps(element),
                'recipient': body['recipient']
            }
            decomposed.append(frag)
        # remove duplicates
    decomposed = remove_duplicates(decomposed)
    return decomposed

def reconstruct_medblock(list_of_elements):
    list_of_elements = remove_duplicates(list_of_elements)
    ids = []
    for element in list_of_elements:
        if element['tag'] == 'body':
            ids.append(element['id'])
    print("Recovered {} ids".format(len(ids)))
    for id in ids:
        medblock = {
            '_id': id,
            'keys': [],
            'files': [],
        }
        for element in list_of_elements:
            if element['tag'] == 'key' and element['id'] == id :
                medblock['keys'].append(element)
            if element['tag'] == 'file' and element['id'] == id:
                medblock['files'].append(element)

        
@task
def check_iota_sync(email):
    # list all documents associated with user
    medblocks_on_disk = []
    # Decompose document into constituants
    decomposed_medblocks_on_disk = [[], [], []]
    # Get associated registered addresses on IOTA
    
    # Get all associated transactions with address

    # Decode txns
    decomposed_medblocks_on_iota = [[], [], []]

    # set.symmetric_difference, from where to where

    # Trigger iota update

    # Trigger couchdb update

    pass

@task 
def check_ipfs_sync(email):
    # Check IPFS sync

    # Check Pin status
    pass

@task
def trigger_sync(email):
    pass




