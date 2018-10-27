(function () {
	// STRING/ARRAY BUFFER HELPER FUNCTIONS
	function arrayToBase64(array) {
		return btoa(String.fromCharCode.apply(null, new Uint8Array(array)))
	}
	
	function Base64toArray(string) {
		decodedString = atob(string)
		len = decodedString.length
		var bytes = new Uint8Array(len)
		bytes = decodedString.split('').map(c=>c.charCodeAt(0))
		return bytes
	}

	function stringToArrayBuffer (str) {
		var buf = new ArrayBuffer(str.length * 2);
	    var bufView = new Uint16Array(buf);
	    for (var i = 0, strLen = str.length; i < strLen; i++) {
	    	bufView[i] = str.charCodeAt(i);
	    }
	    return buf;
	};
	function arrayBufferToString (buffer) {
		return String.fromCharCode.apply(null, new Uint16Array(buffer));
	};

	let ENCRYPT = {
		// RSA FUNCTIONS
		async encryptRSAString (str, publickey) {
			try {
				let arr = await crypto.subtle.encrypt('RSA-OAEP', publickey, stringToArrayBuffer(str));
				return arrayBufferToString(arr);
			}
			catch (e) {
				throw e;
			}
		},
		async encryptRSAStringToArray (str, publickey) {
			let buff = await crypto.subtle.encrypt('RSA-OAEP', publickey, stringToArrayBuffer(str));
			let arr = Array.from(new Uint8Array(buff));
			return arrayToBase64(arr);
		},
		async decryptRSAString (str, privatekey) {
			try {
				let arr = await crypto.subtle.decrypt('RSA-OAEP', privatekey, stringToArrayBuffer(str));
				return arrayBufferToString(arr);
			}
			catch (e) {
				throw e;
			}
		},
		async decryptRSAStringFromArray (arr, privatekey) {
			arr = Base64toArray(arr)
			let a = Uint8Array.from(arr);
			let buff = await crypto.subtle.decrypt('RSA-OAEP', privatekey, a.buffer);
			return arrayBufferToString(buff);
		},
		async newRSAKeys () {
			try {
				let prokey = await crypto.subtle.generateKey({
					name: 'RSA-OAEP',
					modulusLength: 2048,
					publicExponent: new Uint8Array([0x01, 0x00, 0x01]),
					hash: {
						name: 'SHA-256'
					}
				}, true, [
					"encrypt",
					"decrypt"
				]);
				let privatekey = await window.crypto.subtle.exportKey("jwk", prokey.privateKey);
				let publickey = await window.crypto.subtle.exportKey("jwk", prokey.publicKey);
				return {
					privateKey: privatekey,
					publicKey: publickey
				};
			}
			catch (e) {
				throw e;
			}
		},
		async importRSAKeys (propublickey, proprivatekey) {
			try {
				let publickey = await crypto.subtle.importKey("jwk", propublickey, {
					name: "RSA-OAEP",
					hash: {
						name: "SHA-256"
					}
				}, true, ['encrypt']);
				let privatekey = await crypto.subtle.importKey("jwk", proprivatekey, {
					name: "RSA-OAEP",
					hash: {
						name: "SHA-256"
					}
				}, true, ['decrypt']);
				return {
					publicKey: publickey,
					privateKey: privatekey
				};
			}
			catch (e) {
				throw e;
			}
		},
		async importRSAPublicKey (propublickey) {
			try {
				let publickey = await crypto.subtle.importKey("jwk", propublickey, {
					name: "RSA-OAEP",
					hash: {
						name: "SHA-256"
					}
				}, true, ['encrypt']);
				return publickey;
			}
			catch (e) {
				throw e;
			};
		},
		async exportRSAKey (prokey) {
			let key = await window.crypto.subtle.exportKey("jwk", prokey);
			return key;
		},

		// AES Functions
		async newAESKey () {
			try {
				let genkey = await crypto.subtle.generateKey({
					name: 'AES-CBC',
					length: 256
				}, true, [
					"encrypt",
					"decrypt"
				]);
				let key = await crypto.subtle.exportKey("jwk", genkey);
				return key.k;
			}
			catch (e) {
				throw e;
			}
		},
		async importAESKey (key) {
			try {
				return await crypto.subtle.importKey("jwk", {
					kty: "oct",
					k: key,
					alg: "A256CBC",
					ext: true
				}, "AES-CBC", false, [
					"encrypt",
					"decrypt"
				]);
			}
			catch (e) {
				throw e;
			}
		},
		async encryptAESString (str, key) {
			try {
				let iv = crypto.getRandomValues(new Uint8Array(16));
				let arr = await crypto.subtle.encrypt({
					name: 'AES-CBC',
					iv: iv
				}, key, stringToArrayBuffer(str));
				let enstr = arrayBufferToString(arr);
				return {
					enstr: enstr,
					iv: Array.from(iv)
				};
			}
			catch (e) {
				throw e;
			}
		},
		async encryptAESBuffer (buff, key) {
			try {
				let iv = crypto.getRandomValues(new Uint8Array(16));
				let arr = await crypto.subtle.encrypt({
					name: 'AES-CBC',
					iv: iv
				}, key, buff);
				return {
					enarr: arr,
					iv: Array.from(iv)
				};
			}
			catch (e) {
				throw e;
			}
		},
		async decryptAESString ({enstr: enstr, iv: iv}, key) {
			try {
				let arr = await crypto.subtle.decrypt({
					name: 'AES-CBC',
					iv: Uint8Array.from(iv)
				}, key, stringToArrayBuffer(enstr));
				let str = arrayBufferToString(arr);
				return str;
			}
			catch (e) {
				throw e;
			}
		},
		async decryptAESBuffer ({enarr: enarr, iv: iv}, key) {
			try {
				let arr = await crypto.subtle.decrypt({
					name: 'AES-CBC',
					iv: Uint8Array.from(iv)
				}, key, enarr);
				return arr;
			}
			catch (e) {
				console.log(e);
				throw e;
			}
		}
	};
	window.Encrypt = ENCRYPT;
})();