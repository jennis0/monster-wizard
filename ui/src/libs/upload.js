import { addSource, addUpload, addImage, addStatblock, db, updateUpload } from "./db"
import { v4 as uuidv4 } from 'uuid';
import { get_process_update, post_file } from "./api";


function handleFinished(upload_id, response) {
    console.log(upload_id)
    db.uploads.where("id").equals(upload_id).toArray().then(
        uploads => {
        const upload=uploads[0]
        console.log("finished")
        console.log(upload)
    
        for (const source of response.sources) {
            addSource(
                upload.source.title, 
                upload.source.author, 
                source.num_pages, 
                source.filepath, 
                Date.toString(), 
                source.version, 
                "finished", 
                response.errors[source.filepath],
                source.page_images[0],
                upload.raw
            )
            .then(
                (id) => {
                    for (const sb of source.statblocks) {
                        addStatblock(id, sb)
                    }
                    if (upload.store_images) {
                        for (const image of source.images) {
                            addImage(id, image.page, image)
                        }
                    }
                    console.log("finished save")
            })
        }
    })  
}

function handleMajorError(id, e) {
    console.log("error", e)
    return
}

function handleUploadUpdate(id, response) {
    console.log("response", response)
    if (response.status === "finished") {
        handleFinished(id, response)
    } 
    updateUpload(id, 
            {
                status:response.status, 
                progress:response.progress, 
                file_progress:response.file_progress,
                errors:response.errors
            }
    )
}

export function get_request_status( uploads ) {

    for (const upload of uploads) {
        if (upload.status === "error" || upload.status === "finished") {
            continue
        }

        get_process_update(upload.request_id)
         .then(r => r.json(), (e) => handleMajorError(upload.id, e))
         .then(r => handleUploadUpdate(upload.id, r), (e) => console.log("Error", e))
    }
}

export function uploadRequest(requests, source, store_images, store_raw) {
    const form = new FormData()
    const request_id = uuidv4()

    console.log(source);
  
    form.append("extract_images",store_images)
    form.append("uuid", request_id)
    for (const request of requests) {
      form.append("files", request.file)
      form.append("pages", JSON.stringify(request.pages))
    }
    form.append("source", JSON.stringify(source))
  
    addUpload(
      source.title,
      Date.now().toString(),
      "file_upload",
      [-1,-1],
      [0, requests.length],
      [],
      store_raw ? requests.map(r => r.file) : null,
      store_images,
      source,
      request_id
    ).then(id => {
        post_file(form)
          .then(r => r.json(), (e) => handleMajorError(id, e))
          .then(r => handleUploadUpdate(id, r), (e) => console.log("Error", e))
    })

    
}
  
