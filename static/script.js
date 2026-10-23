let currentID = "uncomplete";
let darkMode = false;

function getValue(id){
    const el = document.getElementById(id);
    return el ? el.value.trim() : "";
}

function switchDiv(nextID){
    document.getElementById(currentID).style.display = 'none';
    document.getElementById(nextID).style.display = 'block';
    currentID = nextID;

    try {sessionStorage.setItem("activeTab", nextID)} catch(e) {}
}

document.addEventListener("DOMContentLoaded", function () {
    if (!document.getElementById("uncomplete")) return;

    let saved = null;
    try { saved = sessionStorage.getItem("activeTab"); } catch (e) {}

    if (saved && document.getElementById(saved)) {
        switchDiv(saved);
    }
});

function applyTheme(theme){
    document.documentElement.dataset.theme = theme;
    const switchThemeBtn = document.getElementById("switchThemeBtn");
    switchThemeBtn.textContent = theme === 'dark' ? "Dark Mode: On" : "Dark Mode: Off";
    try { localStorage.setItem("theme", theme); } catch (e) {}
}

function switchTheme(){
    const root = document.documentElement;
    const darkMode = root.dataset.theme === 'dark'
    
    applyTheme(darkMode ? 'light' : 'dark');
}

document.addEventListener("DOMContentLoaded", function () {
    let saved = null;
    try { saved = sessionStorage.getItem("theme"); } catch (e) {}
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    if (saved || (prefersDark ? 'dark' : 'light')) {
        applyTheme(saved || (prefersDark ? 'dark' : 'light'));
    }
});

function addStudent(event){
    const message = document.getElementById("message");

    const fields = ["title", "desc", "subject", "AMorPM"];
    const numFields = ["month", "day", "year", "hour", "minute"];

    const allFilled = fields.every(id => getValue(id).trim() !== "")
    && numFields.every(id => getValue(id).trim() !== "" && !isNaN(getValue(id)));

    if(allFilled && isValidDueDate()){
        message.style.color = "green";
        message.innerHTML = "Successfully Added Student";
    }
    else{
        event.preventDefault()
        message.style.color = "red";
        message.innerHTML = "Failed adding student";
    }

}

function isValidDueDate(){
    const month = Number(getValue("month"));
    const day = Number(getValue("day"));
    const year = Number(getValue("year"));
    const hour = Number(getValue("hour"));
    const minute = Number(getValue("minute"));

    const currentYear = new Date().getFullYear();

    let is_leap = (year % 4 === 0 && year % 100 !== 0) || (year % 400 === 0);

    if(month > 12 && month < 1) return false;
    if(day > 31 && day < 1) return false;
    if (year < currentYear) return false;
    if(hour > 12 && hour < 1) return false;
    if(minute > 59 && minute < 0) return false;
    if(month === 2 && day > (isLeap ? 29 : 28)) return false;
    if([4, 6, 9, 11].includes(month) && day > 30) return false;

    return true;
   
}