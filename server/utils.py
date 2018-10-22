import json

def to_set(list_of_objs):
    return set([json.dumps(obj, sort_keys=True) for obj in list_of_objs])

def to_dict_list(set_of_json):
    return [json.loads(string) for string in set_of_json]

def remove_duplicates(decomposed_list):
    return to_dict_list(to_set(decompose_medblocks))

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

def reconstruct_medblocks(decomposed_list):
    # To Do
    return
