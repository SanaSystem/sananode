(function () {
	// Connect to IPFS Node
	let NODE = IpfsApi('127.0.0.1', 5001);

	let IPFS = {
		// COMBAK
		async putFile (arrbuff, progresscallback) {
			progresscallback = (progresscallback typeof === "function") ? progresscallback : function () {}
			let buff = buffer.Buffer.from(arrbuff);
			let res = await NODE.add(buff, {progress: progresscallback});
			return res;
		}
	};
})();