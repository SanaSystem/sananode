from django.test import TestCase
import ipfsapi
import time
# Create your tests here.
class TestSetup(TestCase):
    def test_ipfs(self):
        for attempt in range(5): 
            try:
                api = ipfsapi.connect("ipfs",5001)
                break
            except:
                if attempt == 4:
                    raise ConnectionError
                print("[+] Attempt {} to connect to IPFS failed. Sleeping for 1 second.".format(attempt))
                time.sleep(1)
        hash = "QmS4ustL54uo8FzR9455qaxZwuMiUhyvMcX9Ba8nUH4uVv/readme"
        response_must_be = "Hello and Welcome to IPFS!\n\n\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\n\u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2554\u2550\u2550\u2550\u2550\u255d\u2588\u2588\u2554\u2550\u2550\u2550\u2550\u255d\n\u2588\u2588\u2551\u2588\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u2588\u2588\u2588\u2588\u2588\u2557  \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\n\u2588\u2588\u2551\u2588\u2588\u2554\u2550\u2550\u2550\u255d \u2588\u2588\u2554\u2550\u2550\u255d  \u255a\u2550\u2550\u2550\u2550\u2588\u2588\u2551\n\u2588\u2588\u2551\u2588\u2588\u2551     \u2588\u2588\u2551     \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2551\n\u255a\u2550\u255d\u255a\u2550\u255d     \u255a\u2550\u255d     \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d\n\nIf you're seeing this, you have successfully installed\nIPFS and are now interfacing with the ipfs merkledag!\n\n -------------------------------------------------------\n| Warning:                                              |\n|   This is alpha software. Use at your own discretion! |\n|   Much is missing or lacking polish. There are bugs.  |\n|   Not yet secure. Read the security notes for more.   |\n -------------------------------------------------------\n\nCheck out some of the other files in this directory:\n\n  ./about\n  ./help\n  ./quick-start     <-- usage examples\n  ./readme          <-- this file\n  ./security-notes\n"
        response = api.cat(hash)
        response = response.decode()
        print(response)
        self.assertEqual(response, response_must_be)
