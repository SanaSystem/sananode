(function () {
	const GENERAL = PouchDB('generaldata');
	let MEDBLOCK;

	function setUp () {
		MEDBLOCK = PouchDB(porturl(5984) + '/medblocks/', {
			fetch: function (url, opts){
			opts.credentials = 'include';
			return PouchDB.fetch(url, opts);
			}
		});
	};
	// // Sync for GENERAL.userlist
	// // TODO make sync automatic
	// async function syncGeneralUserlist () {
	// 	let users = await axios.get(porturl(8000) + '/users/');
	// 	users = users.data;
	// 	try {
	// 		let userlist = await GENERAL.get('userlist');
	// 		userlist.data = users;
	// 		await GENERAL.put(userlist);
	// 	}
	// 	catch (e) {
	// 		if (e.status === 404) {										\   \	   ____      /  /
	// 			await GENERAL.put({										 \   \    /    \    /  /
	// 				data: users,										  \   \  /  __  \  /  /
	// 				_id: 'userlist'										   \   V   /  \  V  /
	// 			});															\____/     \___/
	// 		}
	// 		else {
	// 			throw e;
	// 		}
	// 	}
	// };

	let DATABASE = {
		async getUser () {
			try {
				let user = await GENERAL.get('user');
				return user.data;
			}
			catch (e) {
				throw e;
			}
		},
		async setUser (jsonstr) {
			try {
				let curruser = await GENERAL.get('user');
				curruser.data = jsonstr;
				await GENERAL.put(curruser);
			}
			catch (e) {
				if (e.status === 404) {
					await GENERAL.put({
						data: jsonstr,
						_id: 'user'
					});
				}
				else {
					throw e;
				}
			}
		},
		async searchUsersByEmail (email) {
			try {
				let user = await MEDBLOCK.getUser(email);
				return user;
			}
			catch (e) {
				if (e.name === 'not_found') {
					console.log("User not found.");
					return undefined;
				}
				else {
					throw e;
				}
			}
			return true;
		},
		// async getAllUsers () {
		// 	try {
		// 		return await GENERAL.get('userlist');
		// 	}
		// 	catch (e) {
		// 		throw e;
		// 	}
		// },
		async signUp (name, password, meta) {
			try {
				meta = meta || {};
				let res = await MEDBLOCK.signUp(name, password, {
					metadata: meta
				});
				if (res.ok === true) {
					return true;
				}
				else {
					console.log(res); // Gracefull TODO
					return false;
				}
			}
			catch (e) {
				throw e;
			}
		},
		async signIn (name, password) {
			try {
				let res = await MEDBLOCK.logIn(name, password);
				if (res.ok === true) {
					return true;
				}
				else {
					console.log(res) // Gracefull TODO
					return false;
				}
			}
			catch (e) {
				throw e;
			}
		},
		async signOut () {
			try {
				await MEDBLOCK.logOut();
			}
			catch (e) {
				throw e;
			}
		},
		async postNewMedblock (medblock) {
			let uuid = await axios.get(porturl(5984) + '/_uuids?count=1');
			uuid = uuid.data.uuids;
			medblock._id = uuid[0];
			try {
				await MEDBLOCK.put(medblock);
			}
			catch (e) {
				throw e;
			}
			return await MEDBLOCK.get(uuid[0]);
		},
		async fetchRecords (step = 5, startkey = "") {
			let res = await MEDBLOCK.query('preview/list', {
				startkey: startkey,
				limit: step,
				skip: (startkey === "" ? 0 : 1),
				reduce: false
			});
			let results = res.rows.map(function (block) {
				return {
					id: block.id,
					from: block.value.creator,
					to: block.value.recipient,
					title: block.value.title,
					files: block.value.files,
					permissions: block.value.permissions,
					keys: block.value.keys
				};
			});
			return results;
		},
		async fetchRecord (recordid) {
			let record = await MEDBLOCK.get(recordid);
			return record;
		},
		async numberOfRecords () {
			try {
				let records = await MEDBLOCK.query('preview/list', {reduce:true});
				return records;
			}
			catch (e) {
				throw e;
			}
		},
		async addPermission (id, rsakey, useremail) {
			let uuid = await axios.get(porturl(5984) + '/_uuids?count=1');
			uuid = uuid.data.uuids;
			let block = await MEDBLOCK.get(id);
			block.permissions.push({
				RSAPublicKey: rsakey,
				email: useremail,
				id: uuid
			});
			await MEDBLOCK.put(block);
		},
		async getPermissionRequests (useremail) {
			let perms = await MEDBLOCK.query('preview/permissions', {
				key: useremail,
				include_docs: true
			});
			let reqs = perms.rows.map(function (perm) {
				return {
					id: perm.id,
					reqkey: perm.value.permission,
					title: perm.value.title,
					requester: perm.value.requester
				};
			});
			return reqs;
		}
	};

	// syncGeneralUserlist();

	setUp();

	window.Database = DATABASE;
})();