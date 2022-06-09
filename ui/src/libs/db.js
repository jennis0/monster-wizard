// db.js
import Dexie from 'dexie';
import React, { useEffect } from 'react';
import { useLiveQuery } from 'dexie-react-hooks'


export const db = new Dexie('pdf2vtt');
db.version(2).stores({
  sources: '++id, title, type, author, pages, file, upload, version, status, errors, frontpage',
  statblocks: '++id, source, original_data, modified_data, image',
  images: "++id, source, page, reference, data, bound",
  pdfs: "++id, source, title, file",
  uploads: "++id, title, time, status, progress, file_progress, errors, raw, store_images, source, request_id",
  collections: "++id, title, description, statblocks, image, searches"
});

export function useSource(id) {
  const result = useLiveQuery(() => db.sources.where("id").equals(Number(id)).toArray(), [id])

  if (!result || result.length === 0) {
    return null;
  }
  return result[0]
}


export async function addSource(title, author, pages, file, upload, version, status, errors, frontpage=null) {
  return await db.sources.add({title, author, pages, file, upload, version, status, errors, frontpage:null})
    .then(s_id => {
      if (frontpage) {
        const img_data = {source:s_id, page:0, reference: frontpage.id, data:frontpage.data, bound:frontpage.bound}
        db.images.add(img_data)
          .then(im_id => db.sources.update(s_id, {frontpage:im_id}))
      }
      return s_id
    })
} 

export function deleteSource(id) {
  db.sources.delete(id)
  db.statblocks.where("source").equals(id).delete()
  db.images.where("source").equals(id).delete()
  db.pdfs.where("source").equals(id).delete()
}

export async function addImage(source, page, data) {
  return await db.images.add({source:source, page:page, reference: data.id, data:data.data, bound:data.bound})
}

export async function addPDF(source, title, file) {
  return await db.pdfs.add({source:source, title:title, file:file})
}

export async function updateSource(source, update) {
  return await db.sources.update(source, update)
}

export async function addStatblock(source, statblock, image=null) {
  console.log(statblock)
  return await db.statblocks.add({source:source, original_data:statblock, modified_data:statblock, image:image})
}

export async function updateStatblock(id, statblock, image=null) {
  return await db.statblocks.update(id, {modified_data:statblock, image:image})

}

export async function deleteStatblock(id) {
  return await db.statblocks.delete(id)
}

export async function addUpload(title, time, status, progress, file_progress, errors, raw, store_images, source, request_id) {
  return await db.uploads.add({title, time, status, progress, file_progress, errors, raw, store_images, source, request_id})
}

export async function updateUpload(upload, update) {
  return await db.uploads.update(upload, update)
}

export async function deleteUpload(upload) {
  return await db.uploads.delete(upload)
}

export async function addCollection(title, description, image=null, statblocks=[], searches=[]) {
  return await db.collections.add({title:title, description:description, image:image, statblocks:statblocks, searches:searches})
}

export async function updateCollection(id, update) {
  return await db.collections.update(id, update)
}

export async function deleteCollection(id) {
  return await db.collections.delete(id)
}

