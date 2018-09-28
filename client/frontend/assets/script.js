// IPFS Node
// const NODE = new Ipfs();

// NODE.on('ready', async () => {
//     let version = await NODE.version();

//     console.log(version);
// })

const DATA = {
    current: 'status',
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
    ipAddress: ''
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
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
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
        async generateKey () {
            let keys = await Encrypt.newRSAKeys();
            this.newUser.privateKey = keys.privateKey;
            this.newUser.publicKey = keys.publicKey;
        },
        handleSubmit () {         
            downloadObjectAsJson(this.newUser, 'user');
            setUser(JSON.stringify(this.newUser));
            // Close modal
            document.querySelector('.modal.create-key').classList.remove('is-active')
        },
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