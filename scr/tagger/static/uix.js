const setVersionContainer = document.getElementById("setVersionFormContainer");
const setVersionButton = document.getElementById("set-current-version").onclick = function() {
    console.log("set version button clicked");
    setVersionContainer.classList.toggle("hidden");
};