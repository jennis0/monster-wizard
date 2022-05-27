// db.js
import Dexie from 'dexie';
import React from 'react';
import { useLiveQuery } from 'dexie-react-hooks'


export const db = new Dexie('pdf2vtt');
db.version(1).stores({
  sources: '++id, title, author, pages, file, upload, version, status, frontpage, pdf',
  statblocks: '++id, source, original_data, modified_data, image',
  images: "++id, source, page, reference, data, bound",
  pdfs: "++id, source, file",
  uploads: "++id, filename, file, time, status, progress, errors"
});

export function useSource(id, watch_params=[]) {
  const result = useLiveQuery(() => db.sources.where("id").equals(Number(id)).toArray(), watch_params)
  if (!result || result.length === 0) {
    return null;
  }
  return result[0]
}


export async function addSource(title, author, pages, file, upload, version, status, frontpage=null, pdf=null) {
  return await db.sources.add({title, author, pages, file, upload, version, status, frontpage:null, pdf:null})
    .then(s_id => {
      if (frontpage) {
        db.images.add({source:s_id, page:0, reference: frontpage.id, data:frontpage.data, bound:frontpage.bound})
          .then(im_id => db.sources.update(s_id, {frontpage:im_id}))
      }
      if (pdf) {
        db.pdfs.add({source:s_id, file:pdf}).then(pdf_id => db.sources.update(s_id, {pdf:pdf_id}))
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

export async function addPDF(source, file) {
  return await db.pdfs.add({source:source, file:file})
}

export async function updateSource(source, update) {
  return await db.sources.update(source, update)
}

export async function addStatblock(source, statblock, image=null) {
    return await db.statblocks.add({source:source, original_data:statblock, modified_data:statblock, image:image})
}

export async function addUpload(filename, file, time, status, progress, errors) {
  return await db.uploads.add({filename, file, time, status, progress, errors})
}

