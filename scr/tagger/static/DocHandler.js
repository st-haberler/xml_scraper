"use strict";

class Doc {
  constructor(source = "eo", index = 0) {
    // LATER: check if index and source is really needed at object level
    // probably only for caching...
    // this._currentIndex = index;
    // this._currentSource = source;
    // this._document = null;
  }

  loadDoc(source, index) {
    return new Promise((resolve, reject) => {
      fetch(`/get_doc/${source}/${index}`)
        .then((response) => { return response.json(); })
        .then((document) => { resolve(document); })
        .catch((error) => { reject(error); });
    });
  }

  saveDoc(doc) {
    // upload doc as json data to server
    let data = JSON.stringify(doc);
    fetch("/save_doc", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: data,
    });
  }

  getLabels() {
    return new Promise((resolve, reject) => {
      fetch("/get_labels")
        .then((response) => response.json())
        .then((labels) => {
          resolve(labels);
        })
        .catch((error) => console.error(error));
    });
  }
}

export { Doc };