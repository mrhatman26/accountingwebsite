console.log("modify.js loaded");
let modifyForm = document.getElementById("modify_form");
let mainBody = document.getElementById("page_mainbody_home");
let errorMessage = null;

function oldErrorCheck(){
    var oldErrorMessage = document.getElementById("errorMessage");
    if (oldErrorMessage === null){
        return false;
    }
    else{
        return true;
    }
}

function submitLogin(event){
    event.preventDefault();
    //Make sure password does not contain text from the other boxes
    if (modifyForm[2].value != ""){
        if (modifyForm[2].value.includes(modifyForm[0].value.split(" ")[0]) || modifyForm[2].value.includes(modifyForm[0].value.split(" ")[1]) || modifyForm[2].value.includes(modifyForm[1].value.split("@")[0])){
            if (oldErrorCheck() === false){
                var mainBody = document.getElementById("page_mainbody_home");
                errorMessage = document.createElement("p");
                errorMessage.id = "errorMessage";
                errorMessage.style.color = "red";
                errorMessage.innerHTML = "Password cannot contain your email or name.";
                mainBody.appendChild(errorMessage);
            }
            else{
                errorMessage.innerHTML = "Password cannot contain your email or name.";
            }
            return;
        }
    }
    //Phone number correction
    if (modifyForm[3].value != ""){
        if (!modifyForm[3].value.includes(" ")){
            modifyForm[3].value = modifyForm[3].value.slice(0, 5) + " " + modifyForm[3].value.slice(5);
        }
    }
    var modifyData = {
        "fullname": modifyForm[0].value,
        "email": modifyForm[1].value,
        "password": modifyForm[2].value,
        "phone": modifyForm[3].value
    };
    $.ajax({
        type: "POST",
        url: "/users/account/modify/validate/",
        data: JSON.stringify(modifyData),
        success: function(response){
            if (response === "success"){
                window.location.replace("/users/account/");
            }
            else if (response === "userexists"){
                if (oldErrorCheck() === false){
                    var mainBody = document.getElementById("page_mainbody_home");
                    errorMessage = document.createElement("p");
                    errorMessage.id = "errorMessage";
                    errorMessage.style.color = "red";
                    errorMessage.innerHTML = "Username already in use";
                    mainBody.appendChild(errorMessage);
                }
                else{
                    errorMessage.innerHTML = "Username already in use";
                }
            }
            else{
                if (oldErrorCheck() === false){
                    var mainBody = document.getElementById("page_mainbody_home");
                    errorMessage = document.createElement("p");
                    errorMessage.id = "errorMessage";
                    errorMessage.style.color = "red";
                    errorMessage.innerHTML = "A server error occured";
                    mainBody.appendChild(errorMessage);
                }
                else{
                    errorMessage.innerHTML = "A server error occured";
                }
            }
        }
    });
}

modifyForm.addEventListener("submit", submitLogin);