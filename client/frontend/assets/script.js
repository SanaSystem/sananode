// IPFS Node
// const NODE = new Ipfs();

// NODE.on('ready', async () => {
//     let version = await NODE.version();

//     console.log(version);
// })

const DATA = {
    current: 'records',
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
        newUser: {
            publicKey: '',
            privateKey: '',
            name: '',
            email: '',
            password: ''
        },
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
    let keys, name, email, password;
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
    if (prouser.email === "" && Database.searchUsersByEmail(prouser.email) === undefined) {
        flag = false;
    }
    else {
        email = prouser.email;
    }
    if (prouser.email !== "") {
        password = prompt('You are currently logged in as ' + email + '. Please confirm your password.');
        if (password === null) {
            flag = false;
        }
    }
    // Check flag
    if (flag === true) {
        try {
            // Login to couch db
            let response = await Database.signIn(email, password);
            if (response === true) {
                 // Set current user
                DATA.currentUser.publicKey = keys.publicKey;
                DATA.currentUser.privateKey = keys.privateKey;
                DATA.currentUser.name = name;
                DATA.currentUser.email = email;
                // Set currentuser to true
                DATA.currentUser.user = true;
                // Save
                let currentuserstr = await stringifyCurrentUser();
                Database.setUser(currentuserstr);
            }
        }
        catch (e) {
            throw e;
            // TODO Notification
        }
    }
    else {
        if (prouser.saved === false) {
            // TODO Notification for User Invalid.
            window.alert("User is invalid.");
        }
        // Clear any current user
        clearUser();
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
    // Save
    let currentuserstr = await stringifyCurrentUser();
    Database.setUser(currentuserstr);
};
function downloadObjectAsJson(exportObj, exportName){ // FIXME fix export of publick and private keys
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportObj, function (key, value) {
        if (['publicKey', 'privateKey', 'name', 'email'].indexOf(key) > -1) {
            return value;
        }
        else {
            return undefined;
        }
    }));
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
        // FIXME - Remove InputNode on cancel event from file
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
            this.formData.newUser.privateKey = keys.privateKey;
            this.formData.newUser.publicKey = keys.publicKey;
        },
        handleUserSubmit () {
            // Sign up user to CouchDB
            Database.signUp(this.formData.newUser.email, this.formData.newUser.password, {
                username: this.formData.newUser.name,
                publicKey: this.formData.newUser.publicKey
            })
            .then((sucess) => {
                if (sucess) {
                    // Download as JSON
                    downloadObjectAsJson(this.formData.newUser, 'user');
                    // Set current user
                    setUser(JSON.stringify(this.formData.newUser));
                }
            })
            .catch(function (e) {
                throw e;
            });
            // Close modal
            document.querySelector('#createKey').classList.remove('is-active');
        },
        async handleRecordSubmit () {
            document.querySelector('#uploadRecords-submit').classList.add('is-loading');
            document.querySelector('#uploadRecords-submit').setAttribute('disabled', 'true');
            // Validation
            if (await (async () => {
                // Check current user
                let currentUser = this.currentUser.user && this.currentUser.publicKey;
                if (currentUser === false) {
                    return false;
                }
                // Check user
                let user = await Database.searchUsersByEmail(this.formData.uploadRecords.recipient);
                if (user === undefined) {
                    return false;
                }
                // Check Title
                if (!/^(\w|\d)+/.test(this.formData.uploadRecords.title)) {
                    return false;
                }
                // Check length of files > 0
                if (this.formData.uploadRecords.files.length === 0) {
                    return false;
                }
                return true;
            })()) {
                // Get title of medblock
                let title = this.formData.uploadRecords.title;
                // Get recipient is valid & get RSA Key
                let user = await Database.searchUsersByEmail(this.formData.uploadRecords.recipient);
                // Convert Files Array to hold file data too
                let files = await createFileTree(this.formData.uploadRecords.files);
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
                // console.log(encryptedfiles);
                // Store Encrypted file on IPFS and get IPFS Hash COMBAK
                let ipfsfiles = encryptedfiles.map(f => {
                    return {
                        path: '/' + f.name,
                        content: f.data
                    };
                });
                let ipfsHashes = await IPFSUtils.putFile(ipfsfiles);
                // map ipfsHashes to their files
                encryptedfiles.forEach((f, index) => {
                    delete f.data;
                    f.hash = ipfsHashes[index].hash;
                });
                // Encrypt AES key with RSA
                let recipientKey = await Encrypt.importRSAPublicKey(user.publicKey);
                let enAESkey = await Encrypt.encryptRSAString(proAESkey, recipientKey);
                // console.log(proAESkey, enAESkey);
                // Create Medblock object TODO
                console.log(this.currentUser.publicKey);
                let medblockobj = {
                    title: title,
                    files: encryptedfiles,
                    keys: [
                        {
                            RSAPublicKey: user.publicKey,
                            encryptedAESKey: enAESkey
                        }
                    ],
                    format: 'MEDBLOCK_FILES_AES-CBC_RSA-OAEP',
                    type: 'medblock',
                    creator: {
                        publicKey: Encrypt.exportRSAKey(this.currentUser.publicKey),
                        email: this.currentUser.email
                    },
                    user: this.currentUser.email
                };
                // Post to database
                Database.postNewMedblock(medblockobj);
                // Cleanup
                document.querySelector('#newRecord').classList.remove('is-active');
                document.querySelector('#uploadRecords-submit').classList.remove('is-loading');
                document.querySelector('#uploadRecords-submit').removeAttribute('disabled');
            }
            else {
                // TODO Show notification error
                console.log("error");
                document.querySelector('#uploadRecords-submit').classList.remove('is-loading');
                document.querySelector('#uploadRecords-submit').removeAttribute('disabled');
            }
        },
        async handleRecordAdd () {
            // Get files
            let files = await getFiles();
            let filesarr = Array.from(files).map(file => file);
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
        async handleRecordRecpientChange () {
            // change recipient state to loading
            this.formData.uploadRecords.recipientValid = 1;
            // search users
            let recipient = await Database.searchUsersByEmail(this.formData.uploadRecords.recipient);
            if (recipient === undefined) {
                this.formData.uploadRecords.recipientValid = -1;
            }
            else {
                this.formData.uploadRecords.recipientValid = 2;
            }
            // Check if field is empty
            if (this.formData.uploadRecords.recipient === '') {
                this.formData.uploadRecords.recipientValid = 0;
            }
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