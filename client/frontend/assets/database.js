	const GENERAL = PouchDB('generaldata');
	const MEDBLOCK = PouchDB(porturl(8001) + '/medblocks/', {skip_setup:true});

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
	// 		if (e.status === 404) {
	// 			await GENERAL.put({
	// 				data: users,
	// 				_id: 'userlist'
	// 			});
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
			// try {
			// 	let userlist = await GENERAL.get('userlist');
			// 	userlist = userlist.data;
			// 	let found = userlist.find(function (user) {
			// 		if (user.email === email) {
			// 			return true;
			// 		}
			// 		else {
			// 			return false;
			// 		}
			// 	});
			// 	if (found !== undefined && typeof found.publicKey === 'string') {
			// 		found.publicKey = JSON.parse(found.publicKey);
			// 	}
			// 	return found;
			// }
			// catch (e) {
			// 	throw e;
			// }
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
					metadata: meta,
					ajax: {
						withCredentials: false
					}
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
				let res = await MEDBLOCK.logIn(name, password, {
					ajax: {
						withCredentials: false
					}
				});
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
		async postNewMedblock (medblock) {
			let uuid = await axios.get(porturl(8001) + '/_uuids?count=1');
			uuid = uuid.data.uuids;
			medblock._id = uuid[0];
			console.log(medblock);
			try {
				await MEDBLOCK.put(medblock);
			}
			catch (e) {
				throw e;
			}
		}
	};

	// syncGeneralUserlist();

	window.Database = DATABASE;