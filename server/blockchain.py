import iota
import json
from itertools import groupby
# Using Test node. Public node commented.
# iotaNode = "https://field.deviota.com:443"
iotaNode = "https://nodes.testnet.iota.org:443"
seed = ""
api = iota.Iota(iotaNode, seed)

tag_list = {
    'register' : 'GFAQBESKMJIPYWPARQBZMROJVFP',
    'body' : 'M9CJ9DLLGBDI9ZPXRIIPDCEBWGO',
    'key': 'GQAZH9JTKGRTKMWQSLSYSVQ9HJG',
    'permission': 'FKXHTC9ERWPKOXEBAFFYUTRDXJO',
    'file': 'WYKOYVPPSGWVSPZIJXWHJTUEU9O',
    'deny': 'K9FZJKOSGDRNRYCTGOPWSDBGYAL'
}

reverse_tag_list = {v:k for k,v in tag_list.items()}

def random_address():
    return iota.Address.random(81)

def random_tag():
    return iota.Tag.random(27)

def register_address():
    pass

def serialize_decomposed(decomposed_list):
    serialized = []
    for e in decomposed_list:
        obj = {
        'tag' : tag_list.get(e['tag'], iota.Tag.from_string(e['tag']).as_json_compatible()),
        'data' : iota.TryteString.from_string(json.dumps(e)),
        'address' : iota.Address.from_string(e['recipient']),
        }
        strict = True
        if strict:
            if obj['tag'] not in tag_list.values():
                continue
        serialized.append(obj)
    return serialized

def dict_to_txns(serialized_list):
    txns = []
    for e in serialized_list:
        txn = iota.ProposedTransaction(
            address = e['address'],
            message=e['data'],
            tag=e['tag'],
            value=0
        )
        txns.append(txn)
    return txns


def broadcast_on_tangle(decomposed_list):
    print("[+] Broadcast to tangle initiated")
    serialized = serialize_decomposed(decomposed_list)
    txns = dict_to_txns(serialized)
    bundles = []
    for txn in txns:
        bundle = api.send_transfer(depth=3, transfers = [txn])
        bundles.append(bundle)
        print("[+] Broadcast successful. Bundle generated: {}".format(bundle))
    return bundles

def retrieve_from_tangle(email):
    print("[+] Recieving data from tangle")
    address = iota.Address.from_string(email)
    hashes = api.find_transactions(addresses=[address], tags=list(tag_list.values()))['hashes']
    if len(hashes) == 0:
        return []
    bundle_count = 0
    data = []
    for hash in hashes:
        try:
            bundle = api.get_bundles(hash)
            bundle = bundle["bundles"]
            print("[+] Recieved data. Total bundles recieved: {}".format(bundle_count+1))
            bundle_count += 1
            messages = []
            for b in bundle:
                messages += b.get_messages()
            json_messages = [json.loads(message) for message in messages]
            data += json_messages
        except iota.BadApiResponse:
            print("[-] Bundle skipped. BadApiResponse. (Probably not tail transaction?)")
            pass
    print("Recieved messages from {} bundles".format(bundle_count))
    return data
    
    # for 
    # # print("Total transactions: {}".format(len(txns)))
    # unique_bundles = set(map(lambda txn:txn.bundle_hash, txns))
    # # print("Found {} bundles: {}".format(len(unique_bundles), unique_bundles))
    # data = []
    # messages = [[(txn.signature_message_fragment, txn.current_index, txn.hash) for txn in txns if txn.bundle_hash==h] for h in unique_bundles]
    
    # for message in messages:
    #     m = ""
    #     for i in sorted(message, key=lambda message:message[1]):
    #         m += str(i[0])
            
    #     try:
    #         print("Decoding: {}".format(m))
    #         string = iota.TryteString(m).decode()
    #     except Exception as e:
    #         #print("Error while decoding transaction hash: {}".format(message[2]))
    #         print(e)
    #     data.append(json.loads(string))
    # return data


def decode_messages(hashes):
    """Returns a list of decodable messages"""
    tryts = api.get_trytes(hashes)['trytes']
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