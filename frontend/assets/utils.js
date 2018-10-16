function porturl (port) {
    switch (port) {
        default:
            return `${location.protocol}//${location.hostname}:${port}`;
            break;
    }
};