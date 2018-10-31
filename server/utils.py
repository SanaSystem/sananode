import json
from itertools import groupby
from sananode.settings import tag_list

def to_set(list_of_objs):
    return set([json.dumps(obj, sort_keys=True) for obj in list_of_objs])

def to_dict_list(set_of_json):
    return [json.loads(string) for string in set_of_json]

def remove_duplicates(decomposed_list):
    return to_dict_list(to_set(decomposed_list))

def decompose_medblocks(list_of_medblocks):
    decomposed = []
    for m in list_of_medblocks:
        medblock = m
        _id = medblock.pop('_id')
        medblock.pop('_rev')
        medblock.pop('type')
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

        try:
            permissions = medblock.pop('permissions')
        except KeyError:
            permissions = []
        for permission in permissions:
            p = {
                'id':_id,
                'tag':'permission',
                'data':json.dumps(permission),
                'recipient': body['recipient']
            }
            decomposed.append(p)
        # print("Medblock: {}\nOther keys: {}".format(_id, other_keys))
        try:
            denied = medblock.pop('denied')
        except KeyError:
            denied = []
        for deny in denied:
            d = {
                'id':_id,
                'tag':'denied',
                'data':json.dumps(deny),
                'recipient': body['recipient']
            }
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

def approved_decompose_medblocks(list_of_medblocks):
    decomposed = decompose_medblocks(list_of_medblocks)
    return [medfrag for medfrag in decomposed if medfrag['tag'] in tag_list.keys()]
    
def reconstruct_medblocks(decomposed_list):
    # To Do
    # Add 'type'
    # Add '_id'
    medblocks = []
    # Group by i
    decomposed_list = sorted(decomposed_list, key=lambda x:str(x['id']))
    for id, medfrag_iterator in groupby(decomposed_list, key=lambda x: str(x['id'])):
        medblock = {
            '_id': id,
            'keys': [],
            'files': [],
            'permissions': [],
            'type':'medblock'
        }
        for medfrag in list(medfrag_iterator):
            if medfrag['tag'] == 'body':
                medblock['creator']=medfrag['creator']
                medblock['format']= medfrag['format']
                medblock['recipient']=medfrag['recipient']
                medblock['title']=medfrag['title']
            elif medfrag['tag'] == 'key':
                medblock['keys'].append(json.loads(medfrag['data']))
            elif medfrag['tag'] == 'file':
                medblock['files'].append(json.loads(medfrag['data']))
            elif medfrag['tag'] == 'permission':
                medblock['permissions'].append(json.loads(medfrag['data']))
            elif medfrag['tag'] == 'denied':
                medblock['denied'].append(json.loads(medfrag['data']))
            else:
                medblock[medfrag['tag']] = json.loads(medfrag['data'])
        medblocks.append(medblock)
    return medblocks

