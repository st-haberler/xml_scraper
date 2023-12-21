"uses strict"

import {Doc} from "./DocHandler.js";

const START = 0
const END = 1
const TYPE = 2


class DBQuery {
    constructor(source_type, index, year, annotation_version) {
        this.source_type = source_type; 
        this.index = index; 
        this.year = year;
        this.annotation_version = annotation_version; 
        this.doc_id = null;
    }
}


class AnnotatedTokens {
    constructor(tokenized_text, annotation) {
        this.tokenized_text = tokenized_text;
        this.annotation = annotation;
    }
}


class TokenFrame {
    constructor(meta_data, annotated_tokens_list) {
        this.meta_data = meta_data;
        this.body = annotated_tokens_list;
    }

}



class Annotator {
    constructor() {
        this._source_type = "Gesetz"; 
        this._source = "eo";
        this._paragraph_index = 0;
        this._tokenized_text = ["This ", "is ", "a ", "test", "."]; //array of tokens 
        this._entities = [[0, 1, "PER"], [2, 3, "LOC"]]; // array of entities
        this._currentLabel = "PER"; // current label
        
        this._preselectedTokens = []; // array of preselected tokens
        
        this._initStyle();
        // this._initNavigation();

        // this._docHandler = new Doc("eo", 0);
        // it works, but this cannot be right -- check later ... 
        // this._initLabels().then(this._fetchDoc("eo", 0).then(() => { this._displayText() }))
        
    }

    async _chooseDoc() {
        // choose document from server to annotate
        console.log("chooseDoc() not implemented yet");
        

    }


    async _fetchTF(query) {
        try {
            let token_frame = await this._docHandler.get_tf(query);
            console.log(token_frame);
        } catch (error) {
            console.log("_fetchTF() request failed, we stay with the same doc");
            // delete log message later - only for debugging
        }
    }

    async _fetchDoc(source_type, index, year) {
        try {
            let doc = await this._docHandler.loadDoc(source_type, index, year);
            this._tokenized_text = doc["tokenized_text"];
            this._entities = doc["entities"];
            this._source_type = doc["meta"]["type"];
            this._source = doc["meta"]["source"];
            this._paragraph_index = doc["meta"]["index"];
        } catch (error) {
            console.log("_fetchDoc() request failed, we stay with the same doc");
            // delete log message later - only for debugging
        }
    }

    _pushDoc() {
        // push current document to docLoader for saving at server 
        let doc = {
            "tokenized_text": this._tokenized_text,
            "entities": this._entities,
            "meta": {
                "type": this._source_type,
                "source": this._source,
                "index": this._paragraph_index
            }
        };
        this._docHandler.saveDoc(doc);
    }

    _initNavigation() {
        document.getElementById("commit").onclick = function() {
            this._commit();
        }.bind(this);

        document.getElementById("save").onclick = () => this._pushDoc();    

        document.getElementById("next").onclick = function() {
            this._commit();
            this._pushDoc();
            this._fetchDoc("eo", this._paragraph_index + 1).then(() => { this._displayText() });
        }.bind(this);

        document.getElementById("prev").onclick = function() {
            this._commit();
            this._pushDoc();
            if (this._paragraph_index > 0) {
                this._fetchDoc("eo", this._paragraph_index - 1).then(() => { this._displayText() });
            }      
        }.bind(this);

        document.addEventListener("keydown", function(event) {
            if (event.key === "Enter") { document.getElementById("commit").click(); };
            if (event.key === "ArrowRight") { document.getElementById("next").click(); };
            if (event.key === "ArrowLeft") { document.getElementById("prev").click(); };
        });

        this._chooseForm = document.getElementById("choose-form");
        this._chooseForm.onsubmit = function(event) {
            event.preventDefault();
            this._chooseDoc();
        }.bind(this);

        this._getTF = document.getElementById("load_source").onclick = function() {
            let query = new DBQuery("PHG", 0, null, null);
            this._fetchTF(query);

        }

        
    }

    _initStyle() {
        this._preSelectionHighlight = "gray";
        this._preSelectionTextColor = "white";
        this._backgroundColor = document.getElementById("text").style.backgroundColor;
    }

    async _initLabels() {
        // get labels from server and initialize label navigation
        this._labels = await this._docHandler.getLabels();
        let colors = ["red", "blue", "green", "yellow", "orange", "purple", "pink", "brown"]; 

        this._labelColormap = {};
        for (let label of this._labels) {
            // step 1: create color map for labels
            this._labelColormap[label] = colors.pop();

            // step 2: create button for label
            let button = document.createElement("button");
            button.id = label;
            button.innerHTML = label;
            button.onclick = function() {
                this._currentLabel = label;
            }.bind(this);
            document.getElementById("label-buttons").appendChild(button);
        }

        let newLabel = document.createElement("button");
        newLabel.id = "new";
        newLabel.innerHTML = "new label";
        newLabel.onclick = function() {
            let label = prompt("Enter new label");
            if (label) {
                this._labels.push(label);
                this._labelColormap[label] = colors.pop();
                let button = document.createElement("button");
                button.id = label;
                button.innerHTML = label;
                button.onclick = function() {
                    this._currentLabel = label;
                }.bind(this);
                document.getElementById("label-buttons").appendChild(button);
            }
        }.bind(this);
        document.getElementById("new-label").appendChild(newLabel);



    }

    _is_continuous() {
        // check if preselection is continuous
        // also sorts preselection in place

        if (this._preselectedTokens.length === 0) {
            return false;
        }
        if (this._preselectedTokens.length === 1) {
            return true;
        }

        this._preselectedTokens.sort();
        for (let i = 0; i < this._preselectedTokens.length - 1; i++) {
            if (this._preselectedTokens[i] + 1 !== this._preselectedTokens[i + 1]) {
                return false;
            }       
        }
        return true;
    }
    
    _commit() {
        // save preselection to entities
        
        // check if preselection is not empty and continuous

        if (this._preselectedTokens && this._is_continuous()) {
            let label = this._currentLabel;

            this._entities.push([this._preselectedTokens[0], this._preselectedTokens[this._preselectedTokens.length - 1] + 1, label]);
            this._applyLabel(this._preselectedTokens, label);
            this._preselectedTokens = [];
        }
    }

    _resetLabel(selection) {
        for (let index of selection) {
            // remove subscript from token_span if exists
            let subscript = document.getElementById("sub" + index.toString());
            if (subscript) {
                subscript.parentNode.removeChild(subscript);
            }

            // undo highlighting of token_span
            document.getElementById(index).style.backgroundColor = this._backgroundColor;
            document.getElementById(index).style.color = "black";
        }
    }

    _resetPreSelection(selection) {
        for (let index of selection) {
            // undo highlighting of token_span
            document.getElementById(index).style.backgroundColor = this._backgroundColor;
            document.getElementById(index).style.color = "black";
        }
    }

    _applyLabel(selection, label) {
        // let start = selection[0];
        // let end = selection[selection.length - 1];
        let highlight = this._labelColormap[label];

        // highlight span 
        for (let i = 0; i < selection.length; i++) {
            document.getElementById(selection[i]).style.color = "black";
            document.getElementById(selection[i]).style.backgroundColor = highlight;
        }

        // add subscript right after the end of highlighted span 
        let subscript = document.createElement("sub");
        subscript.id = "sub" + (selection[selection.length - 1]).toString();
        subscript.innerHTML = label;
        subscript.style.backgroundColor = highlight;
        document.getElementById(selection[selection.length - 1]).appendChild(subscript);
    }

    _displayText() {
        let text = document.getElementById("text");
        text.innerHTML = "";

        // create token_spans and add them to the workspace first 
        for (let i = 0; i < this._tokenized_text.length; i++) {
            let token_span = document.createElement("span");
            token_span.id = i;
            token_span.className = "doc-token";
            token_span.innerHTML = this._tokenized_text[i];

            // event listener for token_span
            token_span.onclick = function() {
                
                // check if token is already labeled (ie part of an entity); in this case remove label and return
                for (let j = 0; j < this._entities.length; j++) {
                    if (this._entities[j][START] <= token_span.id && token_span.id < this._entities[j][END]) {
                        
                        // remove subscript from token_span if exists
                        // undo highlighting of token_span if exists
                        let selection = []; 
                        for (let k = this._entities[j][START]; k < this._entities[j][END]; k++) {
                            selection.push(k);
                        }
                        this._resetLabel(selection)
                        
                        // remove label
                        this._entities.splice(j, 1);
                        return;
                    }
                }

                // check if token is already preselected; remove preselection and return
                let index = this._preselectedTokens.indexOf(parseInt(token_span.id));
                if (index !== -1) {
                    // remove token from preselection
                    this._preselectedTokens.splice(index, 1);

                    // undo highlighting of token_span; change text color back to black
                    let selection = [parseInt(token_span.id)];
                    this._resetPreSelection(selection);

                    return; 
                }

                // all checks are passed: lets label! 
                // add blank to preselection 
                this._preselectedTokens.push(parseInt(token_span.id));
                token_span.style.backgroundColor = this._preSelectionHighlight; 
                token_span.style.color = this._preSelectionTextColor;

            }.bind(this);
                
            text.appendChild(token_span);
        };

        // add labels that came from the server to text 
        for (let entity of this._entities) {
            let selection = [];
            for (let i = entity[START]; i < entity[END]; i++) {
                selection.push(i);
            }
            this._applyLabel(selection, entity[TYPE])
        }   
    }
}
     

let a = new Annotator();