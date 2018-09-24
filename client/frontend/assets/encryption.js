function strToArrayBuffer(str) {
    var buf = new ArrayBuffer(str.length * 2);
    var bufView = new Uint16Array(buf);
    for (var i = 0, strLen = str.length; i < strLen; i++) {
      bufView[i] = str.charCodeAt(i);
    }
    return buf;
  }

function arrayBufferToString(buf) {
return String.fromCharCode.apply(null, new Uint16Array(buf));
}
var algoKeyGen = {
name: 'AES-GCM',
length: 256
};

function randomString(length) {
    return [...Array(length)].map(i=>(~~(Math.random()*36)).toString(36)).join('')
}

function RsaEncryptString(string, publicKey) {
  return crypto.subtle.encrypt("RSA-OAEP", publicKey, strToArrayBuffer(string))
  .then(array=>arrayBufferToString(array))
}

function RsaDecryptString(string, privateKey) {
  return crypto.subtle.decrypt("RSA-OAEP", privateKey, strToArrayBuffer(string))
  .then(array=>arrayBufferToString(array))
}

function exportNewAesKey() {
  return window.crypto.subtle.generateKey(
    {
        name: "AES-CBC",
        length: 256, //can be  128, 192, or 256
    },
    true, //whether the key is extractable (i.e. can be used in exportKey)
    ["encrypt", "decrypt"] //can be "encrypt", "decrypt", "wrapKey", or "unwrapKey"
    )
    .then(key=>window.crypto.subtle.exportKey(
      "jwk", //can be "jwk" or "raw"
      key //extractable must be true
    )).then(key=>key.k)
}

function importAesKey(k) {
  return window.crypto.subtle.importKey(
    "jwk", //can be "jwk" or "raw"
    {   //this is an example jwk key, "raw" would be an ArrayBuffer
        kty: "oct",
        k: k,
        alg: "A256CBC",
        ext: true,
    },
    {   //this is the algorithm options
        name: "AES-CBC",
    },
    false, //whether the key is extractable (i.e. can be used in exportKey)
    ["encrypt", "decrypt"] //can be "encrypt", "decrypt", "wrapKey", or "unwrapKey"
)
}

function AesEncryptString(string, key) {
  iv = window.crypto.getRandomValues(new Uint8Array(16))
  
  return window.crypto.subtle.encrypt(
    {
        name: "AES-CBC",
        //Don't re-use initialization vectors!
        //Always generate a new iv every time your encrypt!
        iv: iv,
    },
    key, //from generateKey or importKey above
    strToArrayBuffer(string) //ArrayBuffer of data you want to encrypt
)
.then(array=>arrayBufferToString(array))
.then(data=>{return {iv:arrayBufferToString(iv), string:data}})
}

function AesDecryptString({iv:iv, string:string}, key){
  console.log(iv)
  console.log(string)
  return window.crypto.subtle.decrypt(
    {
        name: "AES-CBC",
        iv: iv, //The initialization vector you used to encrypt
    },
    key, //from generateKey or importKey above
    strToArrayBuffer(string) //ArrayBuffer of the data
)
}

