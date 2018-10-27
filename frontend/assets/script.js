// IPFS Node
// const NODE = new Ipfs();

// NODE.on('ready', async () => {
//     let version = await NODE.version();

//     console.log(version);
// })

const DATA = {
    current: 'settings',
    stats: {
        numberofrecords: 0,
        isCouchDBRunning: false,
        isIPFSRunning: false
    },
    currentUser: {
        publicKey: '',
        privateKey: '',
        name: '',
        email: '',
        user: false,
        saved: false
    },
    records: {
        list: [],
        startkey: "",
        loader: true,
        step: 3
    },
    notifications: [],
    ipAddress: '',
    ipAddressValid: false,
    peerslist: 0,
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
        },
        viewRecord: {
            title: '',
            from: '',
            to: '',
            files: [],
            decryptionStatus: 0,
            status: 0
        }
    }
};
let TIMER = "";

function porturl (port, pruned = false) {
    switch (port) {
        case 5984:
        case 5001:
            return `${pruned === true ? `` : `http://`}${DATA.ipAddress}${ pruned === true ? `` : `:${port}`}`;
            break;
        default:
            return `${location.protocol}//${location.hostname}${ pruned === true ? `` : `:${port}`}`;
            break;
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
    if (prouser.email !== "" && prouser.privateKey.p) {
        password = prouser.privateKey.p.slice(0, 20);
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
                await Database.setUser(currentuserstr);
                // Run through record permissions
                await setRecordPermissions(DATA.records.list);
                // Get permissions and setup permission polling
                TIMER = setInterval(function () {
                    getPermissionRequests(DATA.currentUser.email);
                }, 5000);
                getPermissionRequests(DATA.currentUser.email);
            }
        }
        catch (e) {
            if (e.status == 401) {
                // Sign up user to CouchDB
                console.log("Signing up new user")
                Database.signUp(email, password, {
                    username: name,
                    publicKey: prouser.publicKey
                })
                .then((sucess) => {
                    if (sucess) {
                        // Set current user
                        setUser(JSON.stringify(prouser));
                    }
                })
                .catch(function (e) {
                    if (e.status == 409) {
                        alert("Wrong user file. User already exists with different private key.");
                    }
                    else {
                        throw e;
                    }
                });
            }
            else {
                throw e;
            }
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
    await Database.setUser(currentuserstr);
    // Signout of pouchdb
    await Database.signOut();
    // Run through record permissions
    await setRecordPermissions(DATA.records.list);
    // Clear Permissions polling
    clearInterval(TIMER);
    DATA.notifications = [];
};
function downloadObjectAsJson (exportObj, exportName) {
    var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({
        name: exportObj.name,
        email:exportObj.email,
        publicKey: exportObj.publicKey,
        privateKey: exportObj.privateKey
    }));
    var downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", exportName + ".json");
    // document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
};
function downloadArrayBuffer (buff, name, type) {
    var blob = new Blob([buff], {type: type});
    var downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", URL.createObjectURL(blob));
    downloadAnchorNode.setAttribute("download", name);
    // document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
};
async function generateZipFileFromRecord () {
    let zip = new JSZip();
    DATA.formData.viewRecord.files.forEach(function (file) {
        zip.file(file.name, file.data, {
            binary: true
        });
    });
    let zipfile = await zip.generateAsync({
        type: 'blob'
    });
    var downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", URL.createObjectURL(zipfile));
    downloadAnchorNode.setAttribute("download", DATA.formData.viewRecord.title + '.zip');
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
async function getFileTreeFromHashTree (filelist, aeskey) {
    let filelistunit = 80 / filelist.length;
    let AESKey = await Encrypt.importAESKey(aeskey);
    let promises = filelist.map(async function (file) {
        let data = await IPFSUtils.getFile(file.hash);
        // Decrypt data
        data = await Encrypt.decryptAESBuffer({
            enarr: data,
            iv: file.iv
        }, AESKey);
        delete file.hash;
        delete file.iv;
        file.data = data;
        DATA.formData.viewRecord.decryptionStatus += filelistunit;
        return file;
    });
    let results = await Promise.all(promises);
    return results;
};
async function getRecordsBatch () {
    try {
        let records = await Database.fetchRecords(DATA.records.step, DATA.records.startkey);
        if (records.length > 0) {
            // Set the startkey
            DATA.records.startkey = records[records.length - 1].id;
        }
        // Check if the length > step
        if (records.length < DATA.records.step) {
            DATA.records.loader = false;
        }
        // return batch of records
        return records;
    }
    catch (e) {
        throw e;
    }
};
async function decryptPossible (publickeys) {
    let currentUserKey = await Encrypt.exportRSAKey(DATA.currentUser.publicKey);
    let currentUserKey_str = currentUserKey.n;
    let found = publickeys.find(function (key) {
        if (key.RSAPublicKey.n === currentUserKey_str) {
            return true;
        }
        else {
            return false;
        }
    });
    return found;
};
async function updateRecords () {
    try {
        let records = await getRecordsBatch();
        await setRecordPermissions(records);
        DATA.records.list = DATA.records.list.concat(records);
    }
    catch (e) {
        throw e;
    }
};
async function setRecordPermissions (recordlist) {
    // Check if not an array
    if (!(recordlist instanceof Array)) {
        recordlist = [recordlist];
    }
    let userkey;
    if (DATA.currentUser.user) {
        // Get current user rsa key
        userkey = await Encrypt.exportRSAKey(DATA.currentUser.publicKey);
        userkey = userkey.n;
    }
    // run through each record and put if permitted or not
    recordlist.forEach(function (record) {
        if (userkey) {
            // map out all the keys to json
            let keys = record.keys.map(key => key.RSAPublicKey.n);
            if (keys.indexOf(userkey) === -1) {
                // map out all the permissions to json
                let permissions = record.permissions.map(perm => perm.RSAPublicKey.n);
                if (permissions.indexOf(userkey) === -1) {
                    // Can ask for permission
                    record.permissionstatus = 3;
                }
                else {
                    // Asked for permission already
                    let denied = record.denied;
                    let decider = record.permissions
                        // Check which all permissions have the userkey
                        .filter(function (perm) {
                            if (perm.RSAPublicKey.n === userkey) {
                                return true;
                            }
                            else {
                                return false;
                            }
                        })
                        // Check which of these permissions are not denied
                        .filter(function (perm) {
                            if (denied.indexOf(perm.id) === -1) {
                                return true;
                            }
                            else {
                                return false;
                            }
                        });
                    if (decider.length > 0) {
                        // Processing
                        record.permissionstatus = 2;
                    }
                    else {
                        // Denied so can ask again
                        record.permissionstatus = 3;
                    }
                }
            }
            else {
                // User has permission
                record.permissionstatus = 1;
            }
        }
        else {
            // User not signed in
            record.permissionstatus = 0;
        }
    });
};
async function displayRecord (record) {
    // Open Modal Window
    document.querySelector('#viewRecord').classList.add('is-active');
    // Set the Variables
    DATA.formData.viewRecord.title = record.title;
    DATA.formData.viewRecord.from = record.creator.email;
    DATA.formData.viewRecord.to = record.recipient;
    // Start Decryption
    // Set state to 0
    DATA.formData.viewRecord.status = 0;
    // Check if decryption is possible
    let possible = await decryptPossible(record.keys);
    if (possible) {
        try {
            // Decrypt AES Key
            let AESKey = await Encrypt.decryptRSAStringFromArray(possible.encryptedAESKey, DATA.currentUser.privateKey);
            DATA.formData.viewRecord.decryptionStatus += 20;
            // create File Tree from IPFS
            let files = await getFileTreeFromHashTree(record.files, AESKey);
            // Set to files
            DATA.formData.viewRecord.files = files;
            // Set state to 1
            DATA.formData.viewRecord.status = 1;
        }
        catch (e) {
            throw e;
        }
    }
    else {
        // Set state to -1
        DATA.formData.viewRecord.status = -1;
    }
};
function isCouchDBRunning () {
    axios
        .get(porturl(5984))
        .then(function (r) {
            if (r.status === 200) {
                DATA.stats.isCouchDBRunning = true;
            }
            else {
                DATA.stats.isCouchDBRunning = false;
            }
        })
        .catch(function () {
            DATA.stats.isCouchDBRunning = false;
        })
};
function isIPFSRunning () {
    DATA.stats.isIPFSRunning = false;
};
async function getPermissionRequests (usermail) {
    let perms = await Database.getPermissionRequests(usermail);
    DATA.notifications = perms;
};
async function setIpAdress (address) {
    let flag = true;
    // check if pouch is running
    try {
        let couchdb = await axios.get(`http://${address}:5984`);
        console.log(couchdb);
        if (couchdb.data.vendor.name !== "Medblocks") {
            flag = false;
        }
    }
    catch (e) {
        console.log(e);
        flag = false;
    }
    // check if ipfs is running
    try {
        let ipfs = IpfsApi(address, 5001);
        let id = await ipfs.id();
        if (id.protocolVersion !== "ipfs/0.1.0") {
            flag = false;
        }
    }
    catch (e) {
        console.log(e);
        flag = false;
    }
    // set ipAddressValid
    if (flag === true) {
        // Everything ok
        DATA.ipAddressValid = true;
        await onIpSet();
    }
    else {
        // Everything not okay
        DATA.ipAddressValid = false;
        return false;
    }
};
async function onIpSet () {
    // Save IP
    await Database.saveIp(DATA.ipAddress);
    // Setups
    Database.setUp();
    IPFSUtils.setUp();
    // Set current stats
    try {
        let numberofrecords = await Database.numberOfRecords();
        if (numberofrecords.rows.length > 0) {
            DATA.stats.numberofrecords = numberofrecords.rows[0].value;
        }
        else {
            DATA.stats.numberofrecords = 0;
        }
        let peerslist = await IPFSUtils.getPeersList();
        console.log
        DATA.peerslist = peerslist;
    }
    catch (e) {
        throw e;
    }
    // User
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
    DATA.stats.isCouchDBRunning = true;
    DATA.stats.isIPFSRunning = true;
    // Medblocks records
    updateRecords();
    // Open status page
    DATA.current = 'status';
}

var main = new Vue({
    el: '#app',
    data: DATA,
    async mounted () {
        console.log("This is running")
        this.ipAddress = await Database.getIp();
        this.handleCheckIp();
    },
    methods: {
        handleCheckIp () {
            if (/^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$/gm.test(this.ipAddress)) {
                setIpAdress(this.ipAddress);
            }
            else {
                this.ipAddressValid = false;
            }
        },
        changeTab: function (tabname) {
            if (this.ipAddressValid) {
                this.current = tabname;
            }
            else {
                this.current = 'settings';
            }
        },
        // ReWrite
        async generateKey () {
            let keys = await Encrypt.newRSAKeys();
            this.formData.newUser.privateKey = keys.privateKey;
            this.formData.newUser.publicKey = keys.publicKey;
        },
        handleUserSubmit () {
            // Sign up user to CouchDB
            Database.signUp(this.formData.newUser.email, this.formData_newUser_password, {
                username: this.formData.newUser.name,
                publicKey: this.formData.newUser.publicKey
            })
            .then(async (sucess) => {
                if (sucess) {
                    // Download as JSON
                    await downloadObjectAsJson(this.formData.newUser, 'user');
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
                // Store Encrypted file on IPFS and get IPFS Hash
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
                let enAESkey = await Encrypt.encryptRSAStringToArray(proAESkey, recipientKey);
                // Current user key
                let currentuserKey = await Encrypt.exportRSAKey(this.currentUser.publicKey);
                let enAESkey_current = await Encrypt.encryptRSAStringToArray(proAESkey, this.currentUser.publicKey);
                // console.log(proAESkey, enAESkey);
                // Create Medblock object
                let medblockobj = {
                    title: title,
                    files: encryptedfiles,
                    keys: [
                        {
                            RSAPublicKey: user.publicKey,
                            encryptedAESKey: enAESkey
                        },
                        {
                            RSAPublicKey: currentuserKey,
                            encryptedAESKey: enAESkey_current
                        }
                    ],
                    format: 'MEDBLOCK_FILES_AES-CBC_RSA-OAEP',
                    type: 'medblock',
                    permissions: [],
                    denied: [],
                    creator: {
                        publicKey: currentuserKey,
                        email: this.currentUser.email
                    },
                    recipient: this.formData.uploadRecords.recipient
                };
                // Post to database
                let newblock = await Database.postNewMedblock(medblockobj);
                // Cleanup
                document.querySelector('#newRecord').classList.remove('is-active');
                document.querySelector('#uploadRecords-submit').classList.remove('is-loading');
                document.querySelector('#uploadRecords-submit').removeAttribute('disabled');
                // Update records list
                let rec = {
                    id: newblock._id,
					from: newblock.creator.email,
					to: newblock.recipient,
					title: newblock.title,
					files: newblock.files.length,
					permissions: newblock.permissions,
					keys: newblock.keys
                };
                await setRecordPermissions(rec);
                this.records.list.unshift(rec);
                // Number of Records
                try {
                    let numberofrecords = await Database.numberOfRecords();
                    if (numberofrecords.rows.length > 0) {
                        this.stats.numberofrecords = numberofrecords.rows[0].value;
                    }
                    else {
                        this.stats.numberofrecords = 0;
                    }
                }
                catch (e) {
                    throw e;
                }
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
        handleLoadMoreRecords () {
            updateRecords();
        },
        async handleOpenRecord (item) {
            // Get record
            let record = await Database.fetchRecord(item.id);
            // Display record
            displayRecord(record);
        },
        handleDownloadRecordFile (item) {
            downloadArrayBuffer(item.data, item.name, item.type);
        },
        async handleDownloadAllRecordFiles () {
            // Zip the files
            await generateZipFileFromRecord();
        },
        async handleRequestRecordPermission  (item) {
            let userkey = await Encrypt.exportRSAKey(this.currentUser.publicKey);
            let useremail = this.currentUser.email;
            // Check if permission isn't already there
            let userkey_ = userkey.n;
            let permissions = item.permissions.map(perm => perm.RSAPublicKey.n);
            if (permissions.indexOf(userkey_) === -1) {
                await Database.addPermission(item.id, userkey, useremail);
            }
            // change item permission status
            item.permissionstatus = 2;
        },
        async handlePermitPermission (item) {
            // if (confirm("Are you sure you want to allow " + item.requester + " permission to " + item.title + "?")) {
                // Fetch Record
                let record = await Database.fetchRecord(item.docid);
                // Get recipient key object
                let userKey = await Encrypt.exportRSAKey(this.currentUser.publicKey);
                let userKey_ = userKey.n;
                let recipientKey = record.keys.find(function (key) {
                    if (key.RSAPublicKey.n === userKey_) {
                        return true;
                    }
                    else {
                        false;
                    }
                });
                if (recipientKey) {
                    // Decode AES key
                    let aesKeyStr = await Encrypt.decryptRSAStringFromArray(recipientKey.encryptedAESKey, this.currentUser.privateKey);
                    // Encode with permissed key
                    let permissedKey = await Encrypt.importRSAPublicKey(item.reqkey);
                    let enAESkey = await Encrypt.encryptRSAStringToArray(aesKeyStr, permissedKey);
                    // Put back in database
                    await Database.allowPermission(item, enAESkey);
                    // Refresh notifications
                    getPermissionRequests(this.currentUser.email);
                }
            // }
        },
        async handleDenyPermission (item) {
            await Database.denyPermission(item);
            // Refresh notifications
            getPermissionRequests(this.currentUser.email);
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
    },
    computed: {
        formData_newUser_password: function () {
            return this.formData.newUser.privateKey.p.slice(0, 20);
        }
    }
});