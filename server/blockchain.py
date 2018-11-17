import iota
import json
from itertools import groupby
import couchdb
import pickle
import base64
from sananode.settings import COUCHDB_BASE_URL, tag_list, iotaNode
from .models import SyncParameters
# Using Test node. Public node commented.
# iotaNode = "https://field.deviota.com:443"

seed = ""
api = iota.Iota(iotaNode, seed)
server = couchdb.Server(COUCHDB_BASE_URL)

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

# Slow. Each send_transfer must be async
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

def check_txn_db(hashes):
    """Returns {'new_hashes': [...], 'cached':{'txn_hash':txn,...}}"""
    # sync = SyncParameters.objects.get(pk=1)
    # sync.lock1 = True
    # sync.save()
    
    db = server['txns']
    new_hashes = []
    cached = []
    for h in hashes:
        try:
            txn = db[str(h)]
            txn = json_to_txn(txn)
            cached.append(txn)
        except couchdb.http.ResourceNotFound:
            new_hashes.append(h)
    
    return {
        'new_hashes': new_hashes,
        'cached': cached,
    }

# Slow...make it async
def hashes_to_txns(hashes):
    """Also writes it to cache"""
    db = server['txns']
    trytes = api.get_trytes(hashes)['trytes']
    txns = []
    for tryte in trytes:
        txn = iota.Transaction.from_tryte_string(tryte)
        # print(txn_json['hash_'])
        # print(txn_json['hash_'].__dict__)
        db[str(txn.hash)] = txn_to_json(txn)
        print("[+] txn {} written to databse".format(txn.hash))
        txns.append(txn)
    return txns

def txn_to_string(txn):
    """Pickles the txn and returns base64 representation of it"""
    string = pickle.dumps(txn)
    string = base64.b64encode(string)
    return string.decode()

def string_to_txn(string):
    """Returns the txn object from a base64 encoded string"""
    string = base64.b64decode(string.encode())
    txn = pickle.loads(string)
    return txn

def txn_to_json(txn):
    return {
        'data': txn_to_string(txn)
    }
def json_to_txn(json):
    return string_to_txn(json['data'])

def get_messages_from_transactions(txns):
    data = []
    txn_count = 0
    bundle_count = 0
    for txn in txns:
        message = txn.signature_message_fragment
        message = iota.TryteString(message)
        try:
            message = message.decode()
            message = json.loads(message)
            data.append(message)
            txn_count += 1
        except iota.TrytesDecodeError:
            print("[-] Trytes Decode Error. Trying to get message from the bundle")
            hash = txn.hash
            messages = get_message_from_bundle(hash)
            bundle_count += len(messages)
            print("[+] Got {} message(s) from bundle".format(len(messages)))
            data += messages
    
    print("Retrived data from: {} txns, {} bundles".format(txn_count, bundle_count))
    return data

def get_message_from_bundle(hash):
    try:
        bundle = api.get_bundles(hash)
        bundle = bundle["bundles"]
        print("[+] Recieved bundle")
        messages = []
        for b in bundle:
            messages += b.get_messages()
        json_messages = [json.loads(message) for message in messages]
    except iota.BadApiResponse:
        print("[-] Bundle skipped. BadApiResponse. (Probably not tail transaction?)")
        pass
    return json_messages

def retrieve_from_tangle(email):
    print("[+] Recieving data from tangle")
    address = iota.Address.from_string(email)
    hashes = api.find_transactions(addresses=[address], tags=list(tag_list.values()))['hashes']
    if len(hashes) == 0:
        print("[-] No matching hashes found")
        return [], False
    print("[+] Checking db for cached transactions")
    db_check = check_txn_db(hashes)
    cached = db_check['cached']
    new_hashes = db_check['new_hashes']
    if len(new_hashes) > 1:
        print("[+] Detected {} new hashes".format(len(new_hashes)))
        # Also writes to cache
        txns = hashes_to_txns(new_hashes)
        messages = get_messages_from_transactions(txns + cached)
        return messages, True
    else:
        print("[o] No new hashes detected. Returning cached messages")
        messages = get_messages_from_transactions(cached)
        return messages, False


# def decode_messages(hashes):
#     """Returns a list of decodable messages"""
#     tryts = api.get_trytes(hashes)['trytes']
#     fail_count = 0
#     messages = []
#     for t in tryts:
#         try:
#             s = t.as_string()
#             messages.append(s)
#         except iota.TrytesDecodeError:
#             fail_count += 1
#     print("Decoded {} messages. Failed to decode {}.".format(len(messages), fail_count))
#     return messages