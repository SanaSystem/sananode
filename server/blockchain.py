import iota
import json
iotaNode = "https://field.deviota.com:443"

seed = ""
api = iota.Iota(iotaNode, seed)

tag_list = {
    'register' : 'VHXGXMNKDBSCVZHZKQNONMC9EQN',
    'body' : 'DSYT9KYMQOLBPPRRMARRBHDQYNA',
    'key': 'IZZX9MBFYQQFVQGMPPGPTQHQPWE',
    'permission': 'CZLRLSSZZIKEAUTLLBFXYEDFMWO',
    'file': 'AZLRLSSZZIKEAUTLLBFXYEDFMWO'
}

def random_address():
    return iota.Address.random(81)

def random_tag():
    return iota.Tag.random(27)

def register_address():
    pass

def serialize_decomposed(decomposed_list):
    serialized = []
    for e in decomposed_list:
        # print(e)
        obj = {
        'tag' : tag_list.get(e['tag'], iota.Tag.from_string(e['tag']).as_json_compatible()),
        'data' : iota.TryteString.from_string(json.dumps(e)),
        'address' : iota.Address.from_string(e['recipient']),
        }
        strict = True
        if strict:
            if obj['tag'] not in tag_list.keys():
                continue
        serialized.append(obj)
    return serialized

def deserialize_decomposed(decomposed_list):
    deseriazed = []
    for e in decomposed_list:
        e['data']
        

def send_message(address, tag, message):
    message = iota.TryteString.from_string(message)
    tag = iota.Tag.from_string(tag)
    address = iota.Address.from_string(address)
    txn = iota.ProposedTransaction(
        address=address,
        message=message,
        tag=tag,
        value=0
    )
    txn = api.send_transfer(depth=3, transfers=[txn])
    return txn

def recieve_messages(address, tag):
    tag = iota.Tag.from_string(tag)
    address = iota.Address.from_string(address)
    txns = api.find_transactions(tags=[tag], addresses=[address])['hashes']
    #print(txns)
    return txns

def decode_messages(txns):
    """Returns a list of decodable messages"""
    tryts = api.get_trytes(txns)['trytes']
    fail_count = 0
    messages = []
    for t in tryts:
        try:
            s = t.as_string()
            messages.append(s)
        except iota.TrytesDecodeError:
            fail_count += 1
    print("Decoded {} messages. Failed to decode {}.".format(len(messages), fail_count))
    return messages