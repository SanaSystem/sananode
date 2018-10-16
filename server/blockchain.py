import iota
iotaNode = "https://field.deviota.com:443"

seed = ""
api = iota.Iota(iotaNode, seed)

def send_message(tag, message):
    message = iota.TryteString.from_string(message)
    address = api.get_new_addresses()['addresses'][0]
    txn = iota.ProposedTransaction(
        address=address,
        message=message,
        tag=iota.Tag(tag.encode()),
        value=0
    )
    return api.send_transfer(depth=3, transfers=[txn])

def recieve_message(tag):
    txns = api.find_transactions(tags=[iota.Tag(tag.encode())])
    print(txns)
    return txns