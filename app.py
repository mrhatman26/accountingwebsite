import ast, traceback
from flask import Flask, render_template, url_for, request, redirect, abort
from flask_login import LoginManager, current_user, login_user, logout_user
from db_handler_users import *
#from db_handler_admin import *
#from db_handler_main import *
#from db_handler_links import *
from action_logger import *
from version_handler import *
from user import User
from global_vars import deployed, live
from misc import fprint
#from user import User

'''Server Vars'''
version = update_version()
fprint("Version is now: " + str(version))
app = Flask(__name__) #Create the flask application
app.secret_key = "SeeThatMountain?YouCanClimbItJERSAIKGYHJIOERHGJ"

'''Login Manager'''
login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_fuser(id):
    user_check = user_check_reconfirm(id)
    if len(user_check) <= 0:
        return None
    else:
        return User(user_check[0], user_check[1], user_check[2])

def get_user():
    try:
        if hasattr(current_user, 'username'):
            return current_user.username
        else:
            return "Annonymous"
    except:
        return "Annonymous"

'''General Routes'''
#Home/Index
@app.route("/")
def home():
    access_log(request.remote_addr, get_user(), "/ (Home)")
    return render_template('home.html', page_name="Home", c_version=version)

'''User Routes'''
#Account Page
@app.route("/users/account/")
def user_account():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/users/account/ (Account Page)")
        user_data = user_get_data(current_user.id)
        for item in user_data:
            fprint(item + " | " + str(user_data[item]) + " | " + str(type(user_data[item])))
        return render_template("users/user_page.html", page_name=get_user(), user_data=user_data, c_version=version)
    else:
        access_log(request.remote_addr, get_user(), "/users/account/ (Account Page)", failed=True, no_auth=True)
        return redirect("/users/login/")

#Login
@app.route("/users/login/")
def user_login():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/users/login/ (Login)", failed=True)
        return redirect("/")
    else:
        access_log(request.remote_addr, get_user(), "/users/login/ (Login)")
        return render_template("users/login.html", page_name="Login", c_version=version)
@app.route("/users/login/validate/", methods=["POST"])
def user_login_validate():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/users/login/validate/ (Login Validation)", failed=True)
        return redirect("/")
    else:
        userdata = request.get_data()
        userdata = userdata.decode()
        try:
            userdata = ast.literal_eval(userdata)
            if user_check_exists(userdata["user_name"]):
                if user_check_pass(userdata):
                    admin_stat = user_check_admin(userdata["user_name"])
                    login_user(User(user_get_id(userdata["user_name"]), userdata["user_name"], admin_stat))
                    login_log(request.remote_addr, userdata["user_name"])
                    return "success"
                else:
                    login_log(request.remote_addr, userdata["user_name"], failed=True)
                    error_log(request.remote_addr, userdata["user_name"], "user_login_validate failed to validate login")
                    return "usernotexist"
            else:
                login_log(request.remote_addr, userdata["user_name"], failed=True)
                error_log(request.remote_addr, userdata["user_name"], "User does not exist")
                return "usernotexist"
        except Exception as e:
            login_log(request.remote_addr, userdata["user_name"], failed=True)
            error_log(request.remote_addr, userdata["user_name"], "Server error during login", theException=traceback.format_exc())
            return "servererror"

#Signup
@app.route("/users/signup/")
def user_signup():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/users/signup/ (Signup)", failed=True)
        return redirect("/")
    else:
        access_log(request.remote_addr, get_user(), "/users/signup/ (Signup)")
        return render_template("users/signup.html", page_name="Signup", c_version=version)
@app.route("/users/signup/validate/", methods=["POST"])
def user_signup_validate():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/users/signup/validate/ (Signup Validation)", failed=True)
        return redirect("/")
    else:
        access_log(request.remote_addr, get_user(), "/users/signup/validate/ (Signup Validation)")
        userdata = request.get_data()
        userdata = userdata.decode()
        userdata = ast.literal_eval(userdata)
        try:
            if user_check_exists(userdata["user_name"]) is False:
                if user_add_new(userdata) is True:
                    new_user_log(request.remote_addr, userdata["user_name"])
                    return "success"
                else:
                    new_user_log(request.remote_addr, userdata["user_name"], failed=True)
                    error_log(request.remote_addr, userdata["user_name"], "user_add_new failed to create a new user")
                    return "servererror"
            else:
                new_user_log(request.remote_addr, userdata["user_name"], failed=True)
                error_log(request.remote_addr, userdata["user_name"], "User already exists")
                return "userexists"
        except Exception as e:
            new_user_log(request.remote_addr, userdata["user_name"], failed=True)
            error_log(request.remote_addr, userdata["user_name"], "Server error during user creation", theException=traceback.format_exc())
            return "servererror"
    
#Modify Account
@app.route("/users/modify/validate/", methods=["POST"])
def user_modify():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/users/modify/validate/ (Modify Validation)")
        userdata = request.get_data()
        userdata = userdata.decode()
        userdata = ast.literal_eval(userdata)
        try:
            if user_check_exists(userdata["user_name"]) is False or current_user.username == userdata["user_name"]:
                userdata["user_id"] = current_user.id
                if user_modify_details(userdata) is True:
                    modify_user_log(request.remote_addr, get_user())
                    return "success"
                else:
                    modify_user_log(request.remote_addr, get_user(), failed=True)
                    error_log(request.remote_addr, get_user(), "user_modify_details failed to modify user details")
                    return "servererror"
            else:
                modify_user_log(request.remote_addr, get_user(), failed=True)
                error_log(request.remote_addr, get_user(), "New username already in use by another user")
                return "userexists"
        except Exception as e:
            modify_user_log(request.remote_addr, get_user(), failed=True)
            error_log(request.remote_addr, get_user(), "Server error during user modification", theException=traceback.format_exc())
            return "servererror"
    else:
        access_log(request.remote_addr, get_user(), "/users/modify/validate/ (Modify Validation)", failed=True, no_auth=True)
        abort(404)

#Delete Account (TBD)
@app.route("/users/modify/delete/")
def user_delete_validate():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/users/modify/delete/ (Delete Account Validate)")
        return render_template("confirmation.html", page_name="Are you sure?", message="Are you sure you want to delete your account?", dir_to_use="user_delete_confirmed", dir_to_return="user_account", yes_message="Yes, DELETE my account", no_message="No, return to my account page", c_version=version)
    else:
        access_log(request.remote_addr, get_user(), "/users/modify/delete/ (Delete Account Validate)", failed=True, no_auth=True)
        abort(404)
@app.route("/users/modify/delete/confirmed/")
def user_delete_confirmed():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/users/modify/delete/confirmed/ (Delete Account Confirmed)")
        old_user = get_user()
        logout_user()
        login_log(request.remote_addr, old_user, logout=True, auto=True)
        if user_delete(current_user.id) is True:
            delete_user_log(request.remote_addr, old_user)
            return redirect("/")
        else:
            delete_user_log(request.remote_addr, old_user, failed=True)
            abort(500)
    else:
        access_log(request.remote_addr, get_user(), "/users/modify/delete/confirmed/ (Delete Account Confirmed)", failed=True, no_auth=True)
        abort(404)
        
#Logout
@app.route("/users/logout/")
def user_logout():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/users/logout/ (Logout)")
        login_log(request.remote_addr, get_user(), logout=True)
        logout_user()
        return redirect("/")
    else:
        access_log(request.remote_addr, get_user(), "/users/logout/ (Logout)", failed=True)
        return redirect("/")
    
'''Admin Routes'''
#Main
@app.route("/admin/")
def admin_main():
    if current_user.is_authenticated:
        if current_user.is_admin:
            access_log(request.remote_addr, get_user(), "/admin/ (Admin: Main)", admin=True)
            return render_template("admin/admin_main.html", page_name="Admin: Main", c_version=version)
        else:
            access_log(request.remote_addr, get_user(), "/admin/ (Admin: Main)", failed=True, admin=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/admin/ (Admin: Main)", failed=True, admin=True, no_auth=True)
        abort(404)

#Error Pages
#These pages are only shown when the website encounters an error.
#404 is page not found.
@app.errorhandler(404)
def page_invalid(e):
    return render_template('errors/404.html'), 404
@app.errorhandler(405)
def page_wrong_method(e):
    return render_template('errors/405.html'), 405
@app.errorhandler(500)
def page_server_error(e):
    return render_template('errors/500.html'), 500

#Favicon
#Apparently supposed to be the icon used when a page is bookmarked.
#Even though this supresses the "favicon.ico" 404 error, it does not show this icon when bookmarked.
@app.route('/favicon.ico')
def favicon():
    return url_for("static", filename="favicon.ico")

#Launch Website
if __name__ == '__main__':
    if live is True:
        from waitress import serve
        serve(app, host="0.0.0.0", port=5000)
    else:
        app.run(host="0.0.0.0", debug=True)