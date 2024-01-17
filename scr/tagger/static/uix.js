"uses strict";

import { dbInterface } from "./DBInterface.js";

// const setVersionContainer = document.getElementById("setVersionFormContainer");
// const setVersionButton = document.getElementById("set-current-version").onclick = function() {
//     console.log("set version button clicked");
//     setVersionContainer.classList.toggle("hidden");
// };



const mainGetTF_button = document.getElementById("main-get-tf");
mainGetTF_button.onclick = function () {
    console.log("main get tf button clicked"); 
}



async function getGesetzListe() {
    const gesetzSelector = document.getElementById("gesetzesnummer-select");
    const gesetzeList = await dbInterface.getGesetzList();
    // console.log(gesetzeList);
    for (let gesetz of gesetzeList) {
        // console.log(gesetz);
        let option = document.createElement("option");
        option.value = gesetz.gesetzesnummer;
        option.text = gesetz.kurztitel;
        gesetzSelector.appendChild(option);
    }
   
}

getGesetzListe();