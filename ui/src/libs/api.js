export function post_file(data, callback) {
    fetch("http://localhost:8000/process_file/",
    {
        method:"POST", body: data
    })
    .then(r => r.json())
    .then(callback);
};
