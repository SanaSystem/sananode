(function () {
	const GENERAL = PouchDB('generaldata');

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
		}
	};

	window.Database = DATABASE;
})();