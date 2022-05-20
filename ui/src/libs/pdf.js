export function load_pdf(filename, callback) {
    const reader = new FileReader();
    if (filename) {
        console.log(filename)
        reader.readAsDataURL(filename);
        reader.onload = () => {
            callback(reader.result);
        };
    }
}