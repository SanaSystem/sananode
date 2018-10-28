(function () {
	const GENERAL = PouchDB('generaldata');
	let MEDBLOCK;

	function setUp () {
		MEDBLOCK = PouchDB(porturl(5984) + '/medblocks/', {
			fetch: function (url, opts) {
				opts.credentials = 'include';
				return PouchDB.fetch(url, opts);
			}
		});
	};

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
				throw e
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
		async fetchRecords () {
			let res = await MEDBLOCK.query('preview/list', {
				reduce: false,
				descending: true
			});
			let results = res.rows.map(function (block) {
				return {
					id: block.id,
					from: block.value.creator,
					to: block.value.recipient,
					title: block.value.title,
					files: block.value.files,
					permissions: block.value.permissions,
					denied: block.value.denied,
					keys: block.value.keys
				};
			});
			return results;
		},
		async fetchRecord (recordid) {
			let record = await MEDBLOCK.get(recordid);
			return record;
		},
		async addPermission (id, rsakey, useremail) {
			let uuid = await axios.get(porturl(5984) + '/_uuids?count=1');
			uuid = uuid.data.uuids[0];
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
				key: useremail
			});
			let reqs = perms.rows.map(function (perm) {
				return {
					docid: perm.id,
					reqkey: perm.value.permission,
					title: perm.value.title,
					requester: perm.value.requester,
					permid: perm.value.id
				};
			});
			return reqs;
		},
		async getPermissionDenied (useremail) {
			let denied = await MEDBLOCK.query('preview/denied', {
				key: useremail
			});
			let dens = denied.rows.map(function (perm) {
				return {
					docid: perm.id,
					reqkey: perm.value.permission,
					title: perm.value.title,
					requester: perm.value.requester,
					permid: perm.value.id
				}
			});
			return dens;
		},
		async allowPermission (item, enAESkey) {
			let block = await MEDBLOCK.get(item.docid);
			// Put into keys
			block.keys.push({
				RSAPublicKey: item.reqkey,
                encryptedAESKey: enAESkey
			});
			await MEDBLOCK.put(block);
		},
		async denyPermission (item) {
			let docid = item.docid;
			let permid = item.permid;
			let block = await MEDBLOCK.get(docid);
			block.denied.push(permid);
			await MEDBLOCK.put(block);
		},
		async saveIp (ip_) {
			try {
				let ip = await GENERAL.get('ip');
				ip.data = ip_;
				await GENERAL.put(ip);
			}
			catch (e) {
				if (e.status === 404) {
					await GENERAL.put({
						data: ip_,
						_id: 'ip'
					});
				}
				else {
					throw e;
				}
			}
		},
		async getIp () {
			try {
				let ip = await GENERAL.get('ip');
				return ip.data;
			}
			catch (e) {
				throw e;
			}
		},
		setUp: setUp
	};

	window.Database = DATABASE;
})();