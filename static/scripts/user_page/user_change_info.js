console.log("user_change_info.js loaded");
//let userNameBox = document.getElementById("user_forename");
//let userEmailBox = document.getElementById("user_email");
//let userMonthlySelectBox = document.getElementById("setting_monthly");
//let userPrevPaySelectBox = document.getElementById("setting_delete_prev");
//let userPUseBox = document.getElementById("user_setting_p_use");
let modifyForm = document.getElementById("modify_user_form");
let submitButton = document.getElementById("modify_submit_button");
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

function submitModification(event){
    event.preventDefault();
    var modifyData = {
        "user_name": modifyForm[0].value,
        "user_email": modifyForm[1].value,
        "user_setting_monthly": modifyForm[2].value,
        "user_setting_del_prev": modifyForm[3].value,
        "user_setting_def_p_use": modifyForm[4].value
    };
    $.ajax({
        type: "POST",
        url: "/users/modify/validate",
        data: JSON.stringify(modifyData),
        success: function(response){
            if (response === "success"){
                window.location.replace("/users/account/");
            }
            else if (response === "userexists"){
                var mainBody = document.getElementById("page_mainbody_home");
                if (oldErrorCheck() === false){
                    errorMessage = document.createElement("p");
                    errorMessage.id = "errorMessage";
                    errorMessage.style.color = "red";
                    errorMessage.innerHTML = "That username already exists!";
                    mainBody.appendChild(errorMessage);
                }
            }
            else{
                var mainBody = document.getElementById("page_mainbody_home");
                if (oldErrorCheck() === false){
                    errorMessage = document.createElement("p");
                    errorMessage.id = "errorMessage";
                    errorMessage.style.color = "red";
                    errorMessage.innerHTML = "A server error occured";
                    mainBody.appendChild(errorMessage);
                }
            }
        }
    });
}

submitButton.addEventListener("click", submitModification);