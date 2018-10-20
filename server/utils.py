import json

def remove_duplicates(decomposed_list):
    decomp_set = set() 
    for e in decomposed_list:
        decomp_set.add(json.dumps(e, sort_keys=True))
    # print("Found {} duplicates".format(len(decomposed_list) - len(decomp_set)))
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