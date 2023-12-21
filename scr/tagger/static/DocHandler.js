"use strict";

class Doc {
  constructor(source_type = "eo", index = 0) {
    // LATER: check if index and source is really needed at object level
    // probably only for caching...
    // this._currentIndex = index;
    // this._currentSource = source;
    // this._document = null;
  }

  get_tf(query) {
    return new Promise((resolve, reject) => {
        fetch("/get_token_frame", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
      })
        .then(response => response.json()) // Assuming the response is in JSON format
        .then(token_frame => resolve(token_frame))
        .catch((error) => reject(error));
        });
    };
  


  loadDoc(source_type, index, year) {
    return new Promise((resolve, reject) => {
      fetch(`/get_token_frame/${source_type}/${index}/${year}`)
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