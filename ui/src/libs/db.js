// db.js
import Dexie from 'dexie';
import React from 'react';
import { useLiveQuery } from 'dexie-react-hooks'


export const db = new Dexie('pdf2vtt');
db.version(1).stores({
  sources: '++id, title, author, pages, file, upload, version, status, frontpage',
  statblocks: '++id, source, data, image',
  images: "++id, source, page, data"
});

export function useSource(id, watch_params=[]) {
  const result = useLiveQuery(() => db.sources.where("id").equals(Number(id)).toArray(), watch_params)
  if (!result || result.length === 0) {
    return null;
  }

  return result[0]
}


export async function addSource(title, author, pages, file, upload, version, status, frontpage=null) {
  return await db.sources.add({title, author, pages, file, upload, version, status, frontpage:null})
    .then(s_id => {
      if (frontpage) {
        db.images.add({source:s_id, page:0, data:frontpage})
          .then(im_id => db.sources.update(s_id, {frontpage:im_id}))
      }
      return s_id
    })
} 

export async function deleteSource(id) {
  db.sources.delete(id)
  db.statblocks.where("source").equals(id).delete()
  db.images.where("source").equals(id).delete()
}

export async function addImage(source, page, data) {
  return await db.images.add({source, page, data})
}

export async function updateSource(source_id, update, callback=null) {
  console.log(source_id, update)
  db.sources.update(Number(source_id), update).then(e => console.log("result", e))
  console.log("done")
}

export async function addStatblock(source, data, modified, image=null) {
    return await db.statblocks.add({source, data, modified, image})
}

