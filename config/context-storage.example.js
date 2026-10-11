// Configuration snippet for Node-RED settings.js.
// Insert inside the module.exports object.
// Replace any existing contextStorage property.
// Do not paste inside a comment.
// This is not a complete settings.js file.

contextStorage: {
    default: "memoryOnly",
    memoryOnly: {
        module: "memory"
    },
    file: {
        module: "localfilesystem"
    }
},
