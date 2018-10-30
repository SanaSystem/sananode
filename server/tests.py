from django.test import TestCase
from .utils import decompose_medblocks
from .blockchain import broadcast_on_tangle, retrieve_from_tangle, tag_list
import json
from .tasks import check_iota_sync
# Create your tests here.
class TestIotaFunctions(TestCase):
    # def test_iota_sync(self):
    #     test_medblock_string = '{"_id":"05793173857b52707cb1e51426dc6a57","_rev":"1-b31ebc5e027fedc1029da2077268e696","title":"New New Format","files":[{"iv":[142,59,31,132,184,105,101,225,212,5,39,140,228,251,173,90],"name":"bottle.jpeg","size":132854,"type":"image/jpeg","hash":"QmdPgfiC6T6wcqKNQZ3Bvwc9F7SzCE3NmvL6X3ew8wRWjP"}],"keys":[{"RSAPublicKey":{"alg":"RSA-OAEP-256","e":"AQAB","ext":true,"key_ops":["encrypt"],"kty":"RSA","n":"uArGBluemvZ4QbBE99bOUIyTGWnnTCrAyxhgJvU2nxfony3j_q1oo1WjsveuP2daMfyEUJtmNTVJQMf-96ysUk4gqj_gIhRs1Dgf6sNx-mFm0sMae8hKxPjRBzPcaHhLp2DqxzP9Y_znOgbWZcmig7X87XAAgNO9io_gGw-I3_wINmu_uS31mbg65sKD5F_q9Gp9UOt5oV9VyZBoFMa7wptZK-YBzJ9EPH-mgUu6lRibm6DMgX31lLLNxGk2F8l22EIkNI7hthaWjbqVZZTrvzvztF5-N2BRKHgDUkf6kcDfy5pQEBaCORfB5jCWQfe_pL8Wvyfn7X08e9q0LAlbwQ"},"encryptedAESKey":"NUJXSWB7Ai4Ts1FM9jsyTDUM2pSOqAnpL9ixnLC10ll+Ynw1oHT7QLu0Q488NxlFWV6ojeV41V3//FVDHLpUcdpX8nWAw5+05LxTJQzFyvOgumJiqGyPAfFOzRIT+DwmR8ulTqSUrmkhjJvAcMJbdjv1CGneE3suGCDumMWYeSllsQU3ceHVkkHx2s0A6DDm9SMQp3gdqiZy1sF7E+nRtAmMkm1ht+E/3RMYz7A6ka+Wh45DLVpo9TujUu1Ly0MJcNnUje4IpMfbtV67Jddi4a0szLU/tuvewcJkltiLvX2OXaLWanzcKySjpmgvcUyZ5YOoUG7ql8Muvbcfs2R7lw=="},{"RSAPublicKey":{"alg":"RSA-OAEP-256","e":"AQAB","ext":true,"key_ops":["encrypt"],"kty":"RSA","n":"wI1BoU_K-WGvQYobR-HZylSKNwMt0Vih5qtNtxR0XgE7VJXfvQ38bJg-Ln02e75oRxL0aAwG-BLIB-C61V-atqpxvmlA16pQ8AOnVhfXgNaTVl_XysjdgEUcpOluVybGOCnq_ZM_tf9aNV4bIBWQpnfVE8O3f2JS5Ad_Cxy19nAh4ra4CM6IwOZJ22F0vbJZ2oqgvhrfL_cNe1kzJBI9JSmz19Gox7WpC9f3iZbXi8WzhNwjVdegu13mOe4xbR3W4ZXaNy9Q_HIZ-PK6SK3kOFv-CiXNSewDqvNIRrO8m8ZaUM3VliuCSBq4pq0Nqt2lvGlniRl7YvTU5lKrbQILzQ"},"encryptedAESKey":"H/4my2z/MyUWnpmUEpwRvz/4Y6xNOTnH2N4nO1V4a8B1+RdRn5v9CeS9SrL9Q0/fNfnuAsvio3YKtX1Bn3DKtiMZnu4i1F4jR+4Pk/ivgwxN6oEki7xci1XsuVEjjTeR0rxprau9rTUOrn7ehjr0I6mZm8j9XfdR+M28Z2TW5HyggtGA46lvypMhdQLNWdF1ZH1jAc4tyUJPpyOKFToUPIT3fNji1L6y5ZRZSxTdRMpYmuVdyEP05ZiCsMOsz6PDSxQXDwyQlPiAKf2RMZBUiaxSLk7RMAXnP+48lscMkdLm/Kiec+iwPwL07NzHLrpATjgWTtwBVh1F+eZkDagoPA=="}],"format":"MEDBLOCK_FILES_AES-CBC_RSA-OAEP","type":"medblock","permissions":[],"denied":[],"creator":{"publicKey":{"alg":"RSA-OAEP-256","e":"AQAB","ext":true,"key_ops":["encrypt"],"kty":"RSA","n":"wI1BoU_K-WGvQYobR-HZylSKNwMt0Vih5qtNtxR0XgE7VJXfvQ38bJg-Ln02e75oRxL0aAwG-BLIB-C61V-atqpxvmlA16pQ8AOnVhfXgNaTVl_XysjdgEUcpOluVybGOCnq_ZM_tf9aNV4bIBWQpnfVE8O3f2JS5Ad_Cxy19nAh4ra4CM6IwOZJ22F0vbJZ2oqgvhrfL_cNe1kzJBI9JSmz19Gox7WpC9f3iZbXi8WzhNwjVdegu13mOe4xbR3W4ZXaNy9Q_HIZ-PK6SK3kOFv-CiXNSewDqvNIRrO8m8ZaUM3VliuCSBq4pq0Nqt2lvGlniRl7YvTU5lKrbQILzQ"},"email":"tornadoalert2@gmail.com"},"recipient":"tornadoalert@gmail.com"}'
    #     medblock = json.loads(test_medblock_string)
    #     medblock2 = json.loads(test_medblock_string)
    #     medblocks = [medblock, medblock2]
    #     medefrags = decompose_medblocks(medblocks)
    #     # print(broadcast_on_tangle(medefrags))
    #     medfrags_from_tangle = retrieve_from_tangle('boo@test.com')
    #     assert len(medfrags_from_tangle) > 2
    #     tags = [med['tag'] for med in medfrags_from_tangle]
    #     print(tags)
    #     for tag in tags:
    #         assert tag in tag_list.keys()
    
    def test_task(self):
        check_iota_sync("tornadoalert@gmail.com")