let currentID = "uncomplete"; // Shows uncomplete assignments that aren't past due as default
let darkMode = false; // Light mode is default

// Gets the value of a an element with less code
function getValue(id){
    const el = document.getElementById(id);
    return el ? el.value.trim() : "";
}

// Hides the previous div and shows the div requested
function switchDiv(nextID){
    document.getElementById(currentID).style.display = 'none';
    document.getElementById(nextID).style.display = 'block';
    currentID = nextID;

    try {sessionStorage.setItem("activeTab", nextID)} catch(e) {}
}

// Ony switched div if one of the navigation buttons are pressed
document.addEventListener("DOMContentLoaded", function () {
    if (!document.getElementById("uncomplete")) return;

    let saved = null;
    try { saved = sessionStorage.getItem("activeTab"); } catch (e) {}

    if (saved && document.getElementById(saved)) {
        switchDiv(saved);
    }
});

// Change from light mode to dark mode, or dark mode to light mode
function applyTheme(theme){
    document.documentElement.dataset.theme = theme;
    const btn = document.getElementById("switchThemeBtn");
    if(btn){
        btn.textContent = theme === 'dark' ? "Dark Mode: On" : "Dark Mode: Off";
    }

    try { localStorage.setItem("theme", theme); } catch (e) {}
}

// Request to apply theme
function switchTheme(){
    const root = document.documentElement;
    const darkMode = root.dataset.theme === 'dark';
    
    applyTheme(darkMode ? 'light' : 'dark');
}

// Applys the same them even when navigating different pages
document.addEventListener("DOMContentLoaded", function () {
    let saved = null;
    try { saved = localStorage.getItem("theme"); } catch (e) {}
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    applyTheme(saved || (prefersDark ? 'dark' : 'light'));
});

async function validateAssignment(event){
    const message = document.getElementById("message"); // Message to display when submit is pressed

    const fields = ["title", "desc", "subject", "AMorPM"]; // Non-interger fields
    const numFields = ["month", "day", "year", "hour", "minute"]; // Integer fields

    // Check for invalid fields
    const missing = [
        ...fields.filter(id => getValue(id) === ""),
        ...numFields.filter(id => getValue(id) === "" || isNaN(getValue(id)))
    ];

    // Displays invalid fields if any
    if (missing.length > 0) {
        event.preventDefault();
        message.style.color = "red";
        message.innerHTML = "Missing or invalid: " + missing.join(", ");
        return;
    }

    // Another error if not valid due date
    if (!isValidDueDate()) {
        event.preventDefault();
        message.style.color = "red";
        message.innerHTML = "Due date is invalid or in the past";
        return;
    }

    // Displays when all fields are valid
    message.style.color = "green";
    message.innerHTML = "Successfully Added Student";
    await wait(2000);
}

// Check for valid due date
function isValidDueDate(){
    const month = Number(getValue("month")); // Month 
    const day = Number(getValue("day")); // Day
    const year = Number(getValue("year")); // Year
    const hour = Number(getValue("hour")); // Hour
    const minute = Number(getValue("minute")); // Monute
    const meridiem = getValue("AMorPM").toUpperCase(); // AM or PM

    if (![month, day, year, hour, minute].every(Number.isInteger)) return false; // All need to be integers
    if (hour < 1 || hour > 12 || minute < 0 || minute > 59) return false; // Hour needs to be between 1 and 12, and minute needs to be 0 and 59

    const hour24 = (hour % 12) + (meridiem === "PM" ? 12 : 0); // Adds 12 if meridiem is PM
    const due = new Date(year, month - 1, day, hour24, minute); // Instantiate new date with selected date properites

    if (meridiem !== "AM" && meridiem !== "PM") return false; // Validate if meridiem is AM or PM

    // Extra validation
    if (
        due.getFullYear() !== year ||
        due.getMonth() !== month - 1 ||
        due.getDate() !== day
    ) return false;

    if (due <= new Date()) return false; // false if due date is less than current date

    return true;
}

const title = document.getElementById("title"); // Title input
const titleCharLength = document.getElementById("titleCharLength"); // For displaying chracter length of title

const desc = document.getElementById("desc"); // Description input
const descCharLength = document.getElementById("descCharLength"); // For displaying chracter length of description

// Display live character count for each
title.addEventListener("input", () =>{
    titleCharLength.innerHTML = "Characters: " + title.value.length + "/50";
});

desc.addEventListener("input", () =>{
    descCharLength.innerHTML = "Characters: " + desc.value.length + "/255";
});
