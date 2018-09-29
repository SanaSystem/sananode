// IPFS Node
// const NODE = new Ipfs();

// NODE.on('ready', async () => {
//     let version = await NODE.version();

//     console.log(version);
// })

const DATA = {
    current: 'records',
    newUser: {
        publicKey: '',
        privateKey: '',
        name: '',
        email: ''
    },
    currentUser: {
        publicKey: '',
        privateKey: '',
        name: '',
        email: '',
        user: false,
        saved: false
    },
    ipAddress: '',
    formData: {
        uploadRecords: {
            recipient: '',
            recipientValid: 0,
            title: '',
            files: []
        }
    }
};

async function stringifyCurrentUser () {
    // Clone object
    let data = {
        publicKey: (DATA.currentUser.publicKey !== '') ? (await Encrypt.exportRSAKey(DATA.currentUser.publicKey)) : (''),
        privateKey: (DATA.currentUser.privateKey !== '') ? (await Encrypt.exportRSAKey(DATA.currentUser.privateKey)) : (''),
        name: DATA.currentUser.name,
        email: DATA.currentUser.email
    };
    // Stringify
    let str = JSON.stringify(data);
    return str;
};
async function setUser (userjson) {
    let prouser = JSON.parse(userjson);
    // Validate JSON TODO
    let flag = true;
    let keys, name, email;
    if (prouser.privateKey === "" && prouser.publicKey === "") {
        flag = false;
    }
    else {
        keys = await Encrypt.importRSAKeys(prouser.publicKey, prouser.privateKey);
    }
    if (prouser.name === "") {
        flag = false;
    }
    else {
        name = prouser.name;
    }
    if (prouser.email === "") {
        flag = false;
    }
    else {
        email = prouser.email;
    }
    // Check flag
    if (flag) {
        // Set current user
        DATA.currentUser.publicKey = keys.publicKey;
        DATA.currentUser.privateKey = keys.privateKey;
        DATA.currentUser.name = name;
        DATA.currentUser.email = email;
        // Set currentuser to true
        DATA.currentUser.user = true;
        DATA.currentUser.saved = false;
        // Save
        let currentuserstr = await stringifyCurrentUser();
        Database.setUser(currentuserstr);
    }
    else {
        if (prouser.saved === false) {
            window.alert("User is invalid.");
        }
    }
};
async function clearUser () {
    // Set Current User to null
    DATA.currentUser.publicKey = '';
    DATA.currentUser.privateKey = '';
    DATA.currentUser.name = '';
    DATA.currentUser.email = '';
    // Set user to false
    DATA.currentUser.user = false;
    DATA.currentUser.saved = true;
    // Save
    let currentuserstr = await stringifyCurrentUser();
    Database.setUser(currentuserstr);
};
function downloadObjectAsJson(exportObj, exportName){
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportObj));
    var downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", exportName + ".json");
    // document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
};
function getFiles () {
    return new Promise(function (res, rej) {
        // Create input
        let inputNode = document.createElement('input');
        inputNode.setAttribute("type", "file");
        inputNode.setAttribute("multiple", "");
        // document.body.appendChild(inputNode); // required for firefox
        // Set up listener
        inputNode.addEventListener("change", function () {
            // Get file list
            let files = this.files;
            inputNode.remove();
            res(files);
        });
        // FIXME - Remove InputNode on cancle event from file
        // Fire the file input
        inputNode.click();
    });
};
async function createFileTree (filelist) {
    let promises = filelist.map(function (file) {
        return new Promise(function (res, rej) {
            const reader = new FileReader();
            reader.onload = function (e) {
                res({
                    name: file.name,
                    size: file.size,
                    type: file.type,
                    data: e.target.result
                });
            };
            reader.readAsArrayBuffer(file);
        });
    });
    let results = await Promise.all(promises);
    return results;
};
async function encryptFileTree (filelist, key) {
    let promises = filelist.map(async function (file) {
        let enfiledata = await Encrypt.encryptAESBuffer(file.data, key);
        return {
            data: enfiledata.enarr,
            iv: enfiledata.iv,
            name: file.name,
            size: file.size,
            type: file.type
        };
    });
    let results = await Promise.all(promises);
    return results;
};

var main = new Vue({
    el: '#app',
    data: DATA,
    async created() {
        try {
            // Set the current user if any
            let userjson = await Database.getUser();
            setUser(userjson);
        }
        catch (e) {
            // Clear the user
            clearUser();
            throw e;
        }
    },
    methods: {
        // ReWrite
        async generateKey () {
            let keys = await Encrypt.newRSAKeys();
            this.newUser.privateKey = keys.privateKey;
            this.newUser.publicKey = keys.publicKey;
        },
        handleUserSubmit () {         
            downloadObjectAsJson(this.newUser, 'user');
            setUser(JSON.stringify(this.newUser));
            // Close modal
            document.querySelector('.modal.create-key').classList.remove('is-active')
        },
        async handleRecordSubmit () {
            // Validation TODO
            // Check if recipient is valid & get RSA Key TODO
            // Convert Files Array to hold file data too
            let files = await createFileTree(this.formData.uploadRecords.files.map(f => f.file));
            // Get an AES Key
            let proAESkey = await Encrypt.newAESKey();
            let AESkey = await Encrypt.importAESKey(proAESkey);
            // Encrypt each file with AES and get IVs
            let encryptedfiles = await encryptFileTree(files, AESkey);
                                // // Test decryption
                                // let file_0 = encryptedfiles[0];
                                // let defile = await Encrypt.decryptAESBuffer({enarr: file_0.data, iv: file_0.iv}, AESkey);
                                // let decoder = new TextDecoder();
                                // let contents = decoder.decode(defile);
                                // console.log(contents);
            console.log(encryptedfiles);
            // Store Encrypted file on IPFS and get IPFS Hash // COMBAK
            
            // Encrypt AES key with RSA
            // Create Medblock object
        },
        async handleRecordAdd () {
            // Get files
            let files = await getFiles();
            let filesarr = Array.from(files).map(file => {
                return {
                    file: file,
                    status: 'Not Uploaded'
                };
            });
            this.formData.uploadRecords.files.splice(this.formData.uploadRecords.files.length, 0, ...filesarr);
            // let samplefile = filesarr[0];
            // const reader = new FileReader();
            // reader.onload = e => {
            //     console.log(e.target.result);
            // };
            // reader.readAsText(samplefile);
        },
        handleRecordDelete (item) {
            this.formData.uploadRecords.files.splice(this.formData.uploadRecords.files.indexOf(item), 1);
        },
        // ReWrite
        loadTextFromFile(ev) {
            const file = ev.target.files[0];
            const reader = new FileReader();
            reader.onload = e => {
                setUser(e.target.result);
            };
            reader.readAsText(file);
        },
        signOut () {
            clearUser();
        }
    }
})