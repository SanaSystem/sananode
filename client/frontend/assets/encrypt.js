// STRING/ARRAY BUFFER HELPER FUNCTIONS
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

// RSA FUNCTIONS
async function encryptRSAString (str, publickey) {
	let arr = await crypto.subtle.encrypt('RSA-OAEP', publickey, stringToArrayBuffer(str));
	return arrayBufferToString(arr);
};
async function decryptRSAString (str, privatekey) {
	let arr = await crypto.subtle.decrypt('RSA-OAEP', privatekey, stringToArrayBuffer(str));
	return arrayBufferToString(arr);
};

// AES Functions
async function newAESKey () {
	let genkey = await crypto.subtle.generateKey({
		name: 'AES-CBC',
		length: 256
	}, true, [
		"encrypt",
		"decrypt"
	]);
	let key = await crypto.subtle.exportKey("jwk", genkey);
	return key.k;
};
async function importAESKey (key) {
	return crypto.subtle.importKey("jwk", {
		kty: "oct",
		k: key,
		alg: "A256CBC",
		ext: true
	}, "AES-CBC", false, [
		"encrypt",
		"decrypt"
	]);
};
async function encryptAESString (str, key) {
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
};
async function decryptAESString ({enstr: enstr, iv: iv}, key) {
	let arr = await crypto.subtle.decrypt({
		name: 'AES-CBC',
		iv: Uint8Array.from(iv)
	}, key, stringToArrayBuffer(enstr));
	let str = arrayBufferToString(arr);
	return str;
};