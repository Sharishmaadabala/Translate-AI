// ===============================
// CHARACTER COUNTER
// ===============================

const inputText = document.getElementById("inputText");
const count = document.getElementById("count");

if (inputText && count) {

    function updateCounter() {
        count.innerText = inputText.value.length;
    }

    inputText.addEventListener("input", updateCounter);
    updateCounter();
}

// ===============================
// COPY TRANSLATION
// ===============================

function copyTranslation() {

    const output = document.getElementById("outputText");

    if (!output) return;

    navigator.clipboard.writeText(output.value);

    showToast("Copied Successfully!");

}

// ===============================
// COPY FROM HISTORY
// ===============================

function copyText(text){

    navigator.clipboard.writeText(text);

    showToast("Copied!");

}

// ===============================
// CLEAR INPUT
// ===============================

function clearText(){

    if(document.getElementById("inputText"))
        document.getElementById("inputText").value="";

    if(document.getElementById("outputText"))
        document.getElementById("outputText").value="";

    if(document.getElementById("count"))
        document.getElementById("count").innerHTML=0;

}

// ===============================
// SEARCH HISTORY
// ===============================

const searchInput=document.getElementById("searchInput");

if(searchInput){

searchInput.addEventListener("keyup",function(){

let value=this.value.toLowerCase();

document.querySelectorAll(".history-card").forEach(card=>{

card.style.display=

card.innerText.toLowerCase().includes(value)

?

"block"

:

"none";

});

});

}

// ===============================
// TOAST
// ===============================

function showToast(message){

const toast=document.getElementById("toast");

if(!toast) return;

toast.innerHTML=message;

toast.classList.add("show");

setTimeout(function(){

toast.classList.remove("show");

},2500);

}

// ===============================
// LOADING
// ===============================

function showLoading(){

const loading=document.getElementById("loading");

if(loading){

loading.style.display="flex";

}

}

function hideLoading(){

const loading=document.getElementById("loading");

if(loading){

loading.style.display="none";

}

}

// ===============================
// FORM LOADER
// ===============================

document.querySelectorAll("form").forEach(form=>{

form.addEventListener("submit",()=>{

showLoading();

});

});

// ===============================
// DARK MODE
// ===============================

const themeSwitch=document.getElementById("themeSwitch");

if(themeSwitch){

themeSwitch.addEventListener("change",()=>{

document.body.classList.toggle("dark");

localStorage.setItem(

"theme",

document.body.classList.contains("dark")

?

"dark"

:

"light"

);

});

}

window.onload=function(){

const theme=localStorage.getItem("theme");

if(theme==="dark"){

document.body.classList.add("dark");

if(themeSwitch){

themeSwitch.checked=true;

}

}

}

// ===============================
// AUTO RESIZE
// ===============================

document.querySelectorAll("textarea").forEach(area=>{

area.addEventListener("input",function(){

this.style.height="auto";

this.style.height=this.scrollHeight+"px";

});

});

// ===============================
// VOICE RECOGNITION
// ===============================

let recognition;

if("webkitSpeechRecognition" in window){

recognition=new webkitSpeechRecognition();

recognition.continuous=false;

recognition.lang="en-IN";

recognition.onresult=function(event){

const text=event.results[0][0].transcript;

const speech=document.getElementById("speechText");

if(speech){

speech.value=text;

}

};

}

const mic=document.getElementById("micButton");

if(mic){

mic.addEventListener("click",()=>{

if(recognition){

recognition.start();

showToast("Listening...");

}

});

}

// ===============================
// COPY VOICE
// ===============================

function copyVoiceTranslation(){

const output=document.getElementById("translatedSpeech");

if(output){

navigator.clipboard.writeText(output.value);

showToast("Copied!");

}

}

// ===============================
// FADE ANIMATION
// ===============================

const observer=new IntersectionObserver(entries=>{

entries.forEach(entry=>{

if(entry.isIntersecting){

entry.target.classList.add("fade-up");

}

});

});

document.querySelectorAll(".feature,.history-card,.glass,.profile-card").forEach(el=>{

observer.observe(el);

});