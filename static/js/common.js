function parseSearch() {
	const args = {};
	const search = location.search.slice(1);
	if (search === '') {
		return args;
	}

	const items = search.split('&');
	for (let i in items) {
		let [k, v] = items[i].split('=', 2);
		args[k] = v;
	}

	return args;
}

function unparseSearch(pathname, argsObj) {
	const items = [];
	for (let k in argsObj) {
		let v = argsObj[k];
		items.push(`${k}=${v}`);
	}
	const search = items.join('&');

	return `${pathname}?${search}`;
}