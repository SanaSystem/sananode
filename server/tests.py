from django.test import TestCase
from .utils import decompose_medblocks
from .blockchain import broadcast_on_tangle, retrieve_from_tangle, tag_list
import json
# Create your tests here.
class TestIotaFunctions(TestCase):
    def test_iota_sync(self):
        test_medblock_string = '{"_id":"bd18752be498b40bd086a601440034a0","_rev":"1-322c6d3fbefb4b36661103b14ea2b462","title":"Testing medblocks","files":[{"iv":[252,111,225,75,43,243,240,230,221,183,190,112,21,83,87,75],"name":"IMG_5923.jpg","size":1134953,"type":"image/jpeg","hash":"QmP2ChSRMMZYPjTGUfh156SQPJGLo7hTiSB3XNSbC8CZC7"}],"keys":[{"RSAPublicKey":{"alg":"RSA-OAEP-256","e":"AQAB","ext":true,"key_ops":["encrypt"],"kty":"RSA","n":"v2cmlEyPBNjcM8KsNTOPy__DRuYnmssRhSW48yqMAsBioytELjK6mQVpdPtPP5kLD8onQqdjMlrqwrD6ESvRRcMmDrFekdBESCrbxjVGo31U2T9xYbr77uUtqDTB0xNLPXinbDwAFvkXUzjHfeQxFVgGTBHSOpvffCAWzGwNoO3AqYgFitydFG5N913VKLAVYEQPgV5DqZWTaoYkBvvECiaG_bpcLlG7Uiusgp7peRuctGEf6_hKmpE3fxL-A7IX7B_QUWDMfyi_JCUJMw-UeqeZWY0bzv3rO8omgFnT1HypOnfduoYjeikzBlwEqi-uGwb3jMsMYHEvWCbT3eH9BQ"},"encryptedAESKey":[13,2,245,184,229,84,30,147,54,138,140,157,211,149,9,164,7,231,84,9,169,35,239,87,227,195,62,250,251,28,189,15,249,73,254,178,212,118,36,145,6,43,105,178,231,67,104,222,233,74,60,79,104,214,206,85,186,168,137,104,228,208,46,3,5,203,234,36,146,91,13,87,10,249,73,140,156,107,227,13,225,196,245,189,110,98,101,49,126,35,18,89,136,232,210,212,142,244,216,101,126,46,157,30,33,193,106,53,21,35,101,54,203,114,29,4,247,121,157,152,69,38,55,219,48,162,182,20,46,213,97,149,77,167,198,143,250,0,119,52,41,8,196,218,35,229,70,70,29,236,9,80,28,184,65,196,28,5,208,118,65,235,3,59,157,203,148,68,58,41,53,242,127,84,94,67,142,237,181,122,252,92,236,224,56,170,69,41,192,121,49,80,139,156,29,148,213,221,130,18,253,190,173,248,215,185,62,85,186,103,247,149,221,154,208,147,230,205,241,108,245,59,0,91,8,204,9,58,14,245,21,250,106,38,129,155,64,220,161,202,164,253,20,228,1,40,204,132,212,6,97,0,69,128,216,49]}],"format":"MEDBLOCK_FILES_AES-CBC_RSA-OAEP","type":"medblock","creator":{"publicKey":{"alg":"RSA-OAEP-256","e":"AQAB","ext":true,"key_ops":["encrypt"],"kty":"RSA","n":"u73kmR3JD2jiZSbg1oMD4z2Pw_A0-MTrcmDJQDUkvf2l_fc-EnuWyh2i0_ET__Uq9r7l_9h2tm9yzlwE0nI9tRrWm0ztw3qL2KRgYzbBqmF02Ol-C8gYB7eozln9c0xdFDjEr1S1eKhpmaoT5gCKUVHbPAyCnW3GIvLsS5kq1QBOzdrRvMFpMvikM_f4uD_yQOCgzoCHmNUWwDc_eG1yJagFx2VrnvZ_wt_OBoRcQzCgDPi8vyxZOdHSGlEQ76A2QV1ThjXG5I50e15evhRA2pnWHicUeFgFdysT9-inDRXv7UIIrK8iAJhQDAR9zA0yOUXOIMkF8X2HhdU8SN5ngw"},"email":"tornadoalert@gmail.com"},"recipient":"tornadoalert@gmail.com"}'
        medblock = json.loads(test_medblock_string)
        medblock2 = json.loads(test_medblock_string)
        medblocks = [medblock, medblock2]
        medefrags = decompose_medblocks(medblocks)
        # print(broadcast_on_tangle(medefrags))
        medfrags_from_tangle = retrieve_from_tangle('tornadoalert@gmail.com')
        difference = set([json.dumps(i, sort_keys=True) for i in medefrags]) - set([json.dumps(i, sort_keys=True) for i in medfrags_from_tangle])
        difference = {json.loads(d)['tag'] for d in difference}
        for d in difference:
            assert d not in tag_list.keys()


