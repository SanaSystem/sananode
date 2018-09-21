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