"uses strict";

import { dbInterface } from "./DBInterface.js";

// const setVersionContainer = document.getElementById("setVersionFormContainer");
// const setVersionButton = document.getElementById("set-current-version").onclick = function() {
//     console.log("set version button clicked");
//     setVersionContainer.classList.toggle("hidden");
// };

// TODO: later this global variable should be encapsulated in a class
let global_overview = null;

const mainGetTF_button = document.getElementById("main-get-tf");
mainGetTF_button.onclick = function () {
    console.log("main get tf button clicked"); 
    // we need this later for onclick dropdown
}


function getGesetzProperties(gesetzesnummer) {
    console.log("getGesetzProperties called with gesetzesnummer: " + gesetzesnummer);
}
window.getGesetzProperties = getGesetzProperties;


async function populateGesetzesnummerSelect() {
    const gesetzesNummerSelect = document.getElementById("gesetzesnummer-select");
    const gesetzeList = await dbInterface.getGesetzList();
    // console.log(gesetzeList);
    for (let gesetz of gesetzeList) {
        // console.log(gesetz);
        let option = document.createElement("option");
        option.value = gesetz.gesetzesnummer;
        option.text = gesetz.kurztitel;
        gesetzesNummerSelect.appendChild(option);
    }
   
}
populateGesetzesnummerSelect();

async function populateGesetzDocumentSelect() {
    const gesetzesnummer = document.getElementById("gesetzesnummer-select").value;

    if (gesetzesnummer === "") {
        console.log("no gesetzesnummer selected");
        return;
    }

    const gesetzDocumentSelect = document.getElementById("gesetz-document-select");
    
    const gesetzOverview = await dbInterface.getGesetzContenOverview(gesetzesnummer);
    
    // TODO: later this global variable should be encapsulated in a class
    global_overview = gesetzOverview;

    for (let item of gesetzOverview) {
        let option = document.createElement("option");
        option.value = item.id;
        if ("artikelnummer" in item) {
            if (item.artikelbuchstabe === null) {
                item.artikelbuchstabe = "";
            }
            option.text = `Art. ${item.artikelnummer}${item.artikelbuchstabe} (${item.absatz_length} Absätze)`;
        };
        if ("paragraphnummer" in item) {
            if (item.paragraphbuchstabe === null) {
                item.paragraphbuchstabe = "";
            }
            option.text = `§ ${item.paragraphnummer}${item.paragraphbuchstabe} (${item.absatz_length} Absätze)`;
        };
        gesetzDocumentSelect.appendChild(option);
    }
}
window.populateGesetzDocumentSelect = populateGesetzDocumentSelect;


function setAbsatzMax() {
    const absatzInput = document.getElementById("br-doc-paragraph");

    
    const max = global_overview.find(item => item.id === parseInt(document.getElementById("gesetz-document-select").value)).absatz_length;
    absatzInput.max = max - 1; // -1 because absatz is 0-based
}
window.setAbsatzMax = setAbsatzMax;