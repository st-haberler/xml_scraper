"uses strict"

import { Doc } from "./DBInterface.js";
import { dbInterface } from "./DBInterface.js";



//NEXT STEP: UPDATE LABEL INIT 
class Annotator {
    constructor() {
        //this._source_type = "Gesetz"; 
        //this._source = "eo";
        //this._paragraph_index = 0;
        //this._tokenized_text = ["This ", "is ", "a ", "test", "."]; //array of tokens 
        //this._entities = [[0, 1, "PER"], [2, 3, "LOC"]]; // array of entities
        
        this._token_frame = {
            tech_id: "TEST0001", 
            doc_paragraph_index: 0,
            applikation: "BrKons", 
            gericht: null,
            geschaeftszahl: null,
            entscheidungsdatum: null,
            kurztitel: "Testgesetz, Kurztitel", 
            langtitel: "Testgesetz, Langtitel",
            gesetzesnummer: 12345678890,
            artikelnummer: null,
            paragraphennummer: 1,
            tokenized_text: ["This ", "is ", "a ", "test", ". ", "Get ", "TF ", "button ", "works ", "now", "."],
            annotations: [{begin: 0, end: 1, label: "PER", version: 0}, 
                            {begin: 2, end: 3, label: "LOC", version: 0}, 
                            {begin: 5, end: 6, label: "PER", version: 1}]
        }
        this._preselectedTokens = []; // array of preselected tokens
        this._currentAnnotationVersion = 0;
        this._labels = ["PER", "LOC", "ORG"]; // array of labels
        this._currentLabel = "PER"; // current label

        this._initStyle();
        this._initNavigation();
        this._initLabels()
            .then(() => { this._displayText() });

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
            let newTokenFrame = await dbInterface.getTF(query);
            console.log(newTokenFrame);
            this._token_frame = newTokenFrame;
            this._displayText();
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

        // this._chooseForm = document.getElementById("choose-form");
        // this._chooseForm.onsubmit = function(event) {
        //     event.preventDefault();
        //     this._chooseDoc();
        // }.bind(this);

        document.getElementById("get_tf").onclick = function() {
            // for now, we use a dummy query. later: get query data from form
            const query = {
                geschaeftszahl: "E4603/2021",
                gesetzesnummer: null,
                paragraph: null,
                doc_paragraph_id: 0
              };
            this._fetchTF(query)
        }.bind(this);

        
    }

    _initStyle() {
        this._preSelectionHighlight = "gray";
        this._preSelectionTextColor = "white";
        this._backgroundColor = document.getElementById("text").style.backgroundColor;
    }

    async _initLabels() {
        // get labels from server and initialize label navigation
        // until server is ready, use dummy labels
        let colors = ["red", "blue", "green", "yellow", "orange", "purple", "pink", "brown"]; 
        let annotationList = await dbInterface.getLabels(this._currentAnnotationVersion);
        
        this._labelColormap = {};
        this._labels = [];

        for (let annotation of annotationList) {
            // step 1: create color map for labels
            this._labelColormap[annotation.label] = colors.pop();

            // step 2: create button for label
            let button = document.createElement("button");
            button.id = annotation.label;
            button.innerHTML = annotation.label;
            button.onclick = function() {
                this._currentLabel = annotation.label;
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

            this._token_frame.annotations.push({
                begin: this._preselectedTokens[0],
                end: this._preselectedTokens[this._preselectedTokens.length - 1] + 1,
                label: label,
                version: this._currentAnnotationVersion
            });
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
        // let begin = selection[0];
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
        for (let i = 0; i < this._token_frame.tokenized_text.length; i++) {
            let token_span = document.createElement("span");
            token_span.id = i;
            token_span.className = "doc-token";
            token_span.innerHTML = this._token_frame.tokenized_text[i];

            // event listener for token_span
            token_span.onclick = function() {
                
                // check if token is already labeled (ie part of an entity); in this case remove label and return
                for (let j = 0; j < this._token_frame.annotations.length; j++) {
                    if (this._token_frame.annotations[j].begin <= token_span.id && token_span.id < this._token_frame.annotations[j].end) {
                        
                        // remove subscript from token_span if exists
                        // undo highlighting of token_span if exists
                        let selection = []; 
                        for (let k = this._token_frame.annotations[j].begin; k < this._token_frame.annotations[j].end; k++) {
                            selection.push(k);
                        }
                        this._resetLabel(selection)
                        
                        // remove label
                        this._token_frame.annotations.splice(j, 1);
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
        let visibleAnnotations = this._token_frame.annotations
            .filter(annotation => annotation.version === this._currentAnnotationVersion);
        console.log("visible annotations: " + visibleAnnotations);
        for (let annotation of visibleAnnotations) {
            let selection = [];
            for (let i = annotation.begin; i < annotation.end; i++) {
                selection.push(i);
            }
            console.log("selection for annotated tokens per server: " + selection)
            console.log(selection)
            this._applyLabel(selection, annotation.label)
        }   
    }
}
     

let a = new Annotator();