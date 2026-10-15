let currentID = "uncomplete";
let darkMode = false;

function switchDiv(nextID){
    document.getElementById(currentID).style.display = 'none';
    document.getElementById(nextID).style.display = 'block';
    currentID = nextID;
}

function switchTheme(){
    const body = document.body;
    const switchThemeBtn = document.getElementById("switchThemeBtn");
    if(!darkMode){
        body.style.backgroundColor = "#1a1a1a";
        body.style.color = "white";
        darkMode = true;

        switchThemeBtn.innerHTML = "Dark Mode: On";
    }
    else{
        body.style.backgroundColor = "white";
        body.style.color = "black";
        darkMode = false;

        switchThemeBtn.innerHTML = "Dark Mode: Off";
    }

}

