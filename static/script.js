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
}

function switchTheme(){
    const body = document.body;
    const switchThemeBtn = document.getElementById("switchThemeBtn");

    darkMode = !darkMode;
    
    body.style.backgroundColor = darkMode ? "#1a1a1a" : "white";
    body.style.color = darkMode ? "white" : "black";
    switchThemeBtn.innerHTML = darkMode ? "Dark Mode: On" : "Dark Mode: Off";

}

function addStudent(event){
    const message = document.getElementById("message");

    const fields = ["title", "desc", "subject", "month", "day", "year", "hour", "minute", "AMorPM"];
    const allFilled = fields.every(id => getValue(id) !== "" && !isNaN);

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