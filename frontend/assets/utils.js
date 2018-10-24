function porturl (port, pruned = false) {
    switch (port) {
        case 5984:
        case 5001:
            return `${pruned === true ? `` : `http://`}192.168.0.107${ pruned === true ? `` : `:${port}`}`;
            break;
        default:
            return `${location.protocol}//${location.hostname}${ pruned === true ? `` : `:${port}`}`;
            break;
    }
};