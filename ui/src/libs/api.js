export function post_file(data, callback) {
    fetch("/process_file/",
    {
        method:"POST", body: data
    })
    .then(r => r.json())
    .then(callback);
};
