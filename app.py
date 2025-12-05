import ast, traceback
from flask import Flask, render_template, url_for, request, redirect, abort
from flask_login import LoginManager, current_user, login_user, logout_user
from db_handler_users import *
#from db_handler_admin import *
#from db_handler_main import *
#from db_handler_links import *
#from action_logger import *
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

#Games
#Game List
@app.route("/games/")
@app.route("/games/pid=<pid>")
@app.route("/games/pid=<pid>?search=<search>")
def game_list(pid=0, search="", no_results=10):
    try:
        if request.args.get("pid", None) is not None:
            pid = request.args.get("pid", None)
        if request.args.get("search", None) is not None:
            if request.args.get("search", None) != "":
                search = request.args.get("search", None).replace(" ", "+")
        if type(pid) == str:
            pid = int(pid)
        games = game_get_selection(pid, search=search)
        current_page = get_current_page(pid, no_results)
        access_log(request.remote_addr, get_user(), "/games/pid=" + str(pid) + "?search=" + search + " (Games List)")
        search = search.replace("+", " ")
        return render_template("games/game_list.html", page_name="All Games", c_version=version, game_list=games[0], no_pages=games[1], no_results=no_results, pid=pid, current_page=current_page, total_results=games[2], tag_search=search)
    except:
        try:
            games = game_get_selection(0, search)
            access_log(request.remote_addr, get_user(), "/games/pid=" + str(pid) + "?search=" + search + " (Games List)", failed=True, default=True)
            error_log(request.remote_addr, get_user(), "An error occurred while trying to show the selected game page", theException=traceback.format_exc())
            current_page = get_current_page(pid, no_results)
            return render_template("games/game_list.html", page_name="All Games", c_version=version, game_list=games[0], no_pages=games[1], no_results=no_results, pid=pid, current_page=current_page, total_results=games[2])
        except:
            access_log(request.remote_addr, get_user(), "/games/pid=" + str(pid) + "?search=" + search + " (Games List)", failed=True, default=True)
            error_log(request.remote_addr, get_user(), "An error occurred while trying to show the default game page. Are there no games?", theException=traceback.format_exc())
            return render_template("games/game_list.html", page_name="All Games", c_version=version)
    
#Individual Game Page
@app.route("/games/game_id=<game_id>")
def game_page(game_id=0):
    try:
        game_data = game_get_single(game_id)
        game_title = "No Game?"
        if game_data is not None:
            game_title = game_data["game_title"]
        access_log(request.remote_addr, get_user(), "/games/game_id=" + str(game_id) + " (Individual Game)")
        approval = game_get_approved(game_id)
        approval_date = game_get_approval_date(game_id)
        denial = game_get_denied(game_id)
        denial_reason = game_get_denial_reason(game_id)
        if denial is False:
            if game_check_release_date(game_id, game_data["game_rdate"]) is True:
                game_data = game_get_single(game_id)
        developer_links = game_get_devpub_links(game_id)
        publisher_links = game_get_devpub_links(game_id, is_devpub=True)
        tag_links = game_get_tag_links(game_id)
        return render_template("games/individual_game.html", page_name=game_title, game_data=game_data, is_approved=approval, denied=denial, denial_desc=denial_reason, aDate=approval_date, developers=developer_links, publishers=publisher_links, tags=tag_links, c_version=version)
    except Exception as e:
        error_log(request.remote_addr, get_user(), "An error occurred when trying to load an invididual game page", traceback.format_exc())
        access_log(request.remote_addr, get_user(), "/games/game_id=" + str(game_id) + " (Individual Game)", failed=True)
        abort(404)

#Add Game Page
@app.route("/games/add/")
def game_add_new():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/games/add/ (Add New Game)")
        return render_template("games/game_add.html", page_name="Add New Game", c_version=version)
    else:
        access_log(request.remote_addr, get_user(), "/games/add/ (Add New Game)", failed=True, no_auth=True)
        return redirect("/users/login/")
#Validate new game
@app.route("/games/add/validate", methods=["POST"])
def game_add_new_validate():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/games/add/validate/ (New Game Validation)")
        game_data = request.get_data()
        game_data = game_data.decode()
        game_data = ast.literal_eval(game_data)
        try:
            if test_datetime(game_data["game_rdate"]) is True:
                if game_check_exists(game_data["game_title"]) is False:
                    if game_create_new(game_data, current_user.id) is True:
                        new_game_log(request.remote_addr, get_user(), game_data["game_title"])
                        return "success"
                    else:
                        error_log(request.remote_addr, get_user(), "An error occurred while trying to create a new game")
                        new_game_log(request.remote_addr, get_user(), game_data["game_title"], failed=True)
                        return "servererror"
                else:
                    error_log(request.remote_addr, get_user(), "New game already exissts")
                    new_game_log(request.remote_addr, get_user(), game_data["game_title"], failed=True)
                    return "gameexists"
            else:
                error_log(request.remote_addr, get_user(), "Game release date is an invalid date")
                new_game_log(request.remote_addr, get_user(), game_data["game_title"], failed=True)
                return "invaliddate"
        except Exception as e:
            new_game_log(request.remote_addr, get_user(), new_game_name=game_data["game_title"], failed=True)
            error_log(request.remote_addr, get_user(), "There was an error while trying to add a new game", theException=traceback.format_exc())
            return "servererror"
    else:
        access_log(request.remote_addr, get_user(), "/games/add/validate/ (New Game Validation)", failed=True, no_auth=True)
        new_game_log(request.remote_addr, get_user(), failed=True)
        return "servererror"
    
#Validate Changing of Game Developers
@app.route("/games/devpubs/change/", methods=["POST"])
def game_change_devpubs():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/games/devpubs/change/ (Change Devpubs)")
        devpub_data = request.get_data()
        devpub_data = devpub_data.decode()
        devpub_data = ast.literal_eval(devpub_data)
        devpub_data["change_isPub"] = to_bool(devpub_data["change_isPub"], is_no=False)
        devpub_data["change_old_developers"] = game_get_developers(devpub_data["change_game_id"], devpub_data["change_isPub"])
        noexistent_tags = ""
        for developer in devpub_data["change_new_developers"]:
            developer = developer.replace(" ", "")
            if devpub_check_exists(developer, is_pub=devpub_data["change_isPub"]) is False:
                if len(noexistent_tags) < 1:
                    noexistent_tags = developer
                else:
                    noexistent_tags = noexistent_tags + "+" + developer
        if len(noexistent_tags) > 0:
            developer_update_game_log(request.remote_addr, get_user(), game_get_name(devpub_data["change_game_id"]), failed=True, tag_not_exist=True)
            return "tagnotexist|" + noexistent_tags
        else:
            update_status = game_update_devpubs(devpub_data, current_user.id, devpub_get_id_function=devpub_get_id, is_publisher=devpub_data["change_isPub"])
            if update_status[2] is True:
                game_name = game_get_name(devpub_data["change_game_id"])
                developer_update_game_log(request.remote_addr, get_user(), game_name, added=update_status[0], removed=update_status[1])
                return "success"
            else:
                developer_update_game_log(request.remote_addr, get_user(), game_get_name(devpub_data["change_game_id"]), failed=True, added=update_status[0], removed=update_status[1])
                return "servererror"
    else:
        access_log(request.remote_addr, get_user(), "/games/devpubs/change/ (Change Devpubs)", failed=True, no_auth=True)
        return "nouser"
    
#Validate Changing of Game Tags
@app.route("/games/tags/change/", methods=["POST"])
def game_change_tags():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/games/tags/change/ (Change Game Tag)")
        tag_data = request.get_data()
        tag_data = tag_data.decode()
        tag_data = ast.literal_eval(tag_data)
        tag_data["change_old_tags"] = game_get_tags(tag_data["change_game_id"])
        noexistent_tags = ""
        for tag in tag_data["change_new_tags"]:
            tag = tag.replace(" ", "")
            if tag_check_exists(tag) is False:
                if len(noexistent_tags) < 1:
                    noexistent_tags = tag
                else:
                    noexistent_tags = noexistent_tags + "+" + tag
        if len(noexistent_tags) > 0:
            tag_update_game_log(request.remote_addr, get_user(), game_get_name(tag_data["change_game_id"]), failed=True, tag_not_exist=True)
            return "tagnotexist|" + noexistent_tags
        else:
            update_status = game_update_tags(tag_data, current_user.id, tag_get_id_function=tag_get_id)
            if update_status[2] is True:
                game_name = game_get_name(tag_data["change_game_id"])
                tag_update_game_log(request.remote_addr, get_user(), game_name, added=update_status[0], removed=update_status[1])
                update_create(game_name, changed=update_status[3])
                update_add_game_link(tag_data["change_game_id"], update_get_id(game_name), current_user.id)
                return "success"
            else:
                tag_update_game_log(request.remote_addr, get_user(), game_get_name(tag_data["change_game_id"]), failed=True, added=update_status[0], removed=update_status[1])
                return "servererror"
    else:
        access_log(request.remote_addr, get_user(), "/games/tags/change/ (Change Game Tag)", failed=True, no_auth=True)
        return "nouser"
    
#Tags
@app.route("/tags/")
@app.route("/tags/pid=<pid>")
@app.route("/tags/pid=<pid>?search=<search>")
def tag_list(pid=0, no_results=10, search=None):
    try:
        if request.args.get("pid", None) is not None:
            pid = request.args.get("pid", None)
        if request.args.get("search", None) is not None:
            if request.args.get("search", None) != "" and request.args.get("search", None).isspace() is False:
                search = request.args.get("search", None)
        if type(pid) == str:
            pid = int(pid)
        tags = tag_get_selection(pid, search=search)
        current_page = get_current_page(pid, no_results)
        access_log(request.remote_addr, get_user(), "/tags/pid=" + str(pid) + "?search=" + str(search) + " (Tag List)")
        return render_template("tags/tag_list.html", page_name="All Tags", c_version=version, tags_list=tags[0], no_pages=tags[1], no_results=no_results, pid=pid, current_page=current_page, total_results=tags[2], tag_search=search)
    except:
        try:
            tags = tag_get_selection(0)
            access_log(request.remote_addr, get_user(), "/tags/pid=" + str(pid) + " (Tag List)", failed=True, default=True)
            error_log(request.remote_addr, get_user(), "An error occurred while trying to show the selected tag page", theException=traceback.format_exc())
            current_page = get_current_page(pid, no_results)
            return render_template("tags/tag_list.html", page_name="All Tags", c_version=version, devpub_list=tags[0], no_pages=tags[1], no_results=no_results, pid=pid, current_page=current_page, total_results=tags[2])
        except:
            access_log(request.remote_addr, get_user(), "/tags/pid=" + str(pid) + " (Tag List)", failed=True, default=True)
            error_log(request.remote_addr, get_user(), "An error occurred while trying to show the default tag page. Are there no tags?", theException=traceback.format_exc())
            return render_template("tags/tag_list.html", page_name="All Tags", c_version=version)
        
#Individual Tag Page
@app.route("/tags/tag_id=<tag_id>")
def tag_page(tag_id=0):
    try:
        tag_data = tag_get_individual(tag_id)
        tag_name = "No Tag?"
        if tag_data is not None:
            tag_name = tag_data["tag_name"]
        access_log(request.remote_addr, get_user(), "/tags/tag_id=" + str(tag_id) + " (Individual Tag)")
        approval = tag_get_approved(tag_id)
        approval_date = tag_get_approval_date(tag_id)
        denial = tag_get_denial(tag_id)
        denial_reason = tag_get_denial_reason(tag_id)
        games = tag_get_games(tag_id)
        return render_template("tags/individual_tag.html", page_name=tag_name, tag_data=tag_data, is_approved=approval, denied=denial, denial_desc=denial_reason, aDate=approval_date, game_links=games, c_version=version)
    except Exception as e:
        error_log(request.remote_addr, get_user(), "An error occurred when trying to load an invididual tag page", traceback.format_exc())
        access_log(request.remote_addr, get_user(), "/tags/tag_id=" + str(tag_id) + " (Individual Tag)", failed=True)
        abort(404)

#Add Tag
@app.route("/tags/add/")
def tag_add():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/tags/add/ (Add Tag)")
        return render_template("tags/tag_add.html", page_name="Add New Tag", c_version=version)
    else:
        access_log(request.remote_addr, get_user(), "/tags/add/ (Add Tag)", no_auth=True, failed=True)
        return redirect("/users/login/")
    
#Tag Validate
@app.route("/tags/add/validate/", methods=["POST"])
def tag_add_validate():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/tags/add/validate/ (Add Tag Validate)")
        tag_data = request.get_data()
        tag_data = tag_data.decode()
        tag_data = ast.literal_eval(tag_data)
        try:
            tag_data["tag_name"] = tag_data["tag_name"].lower()
            if tag_check_exists(tag_data["tag_name"], tag_data["tag_type"]) is False:
                if tag_add_new(tag_data, current_user.id) is True:
                    new_tag_log(request.remote_addr, get_user(), tag_data["tag_name"])
                    return "success"
                else:
                    error_log(request.remote_addr, get_user(), "An error occurred while trying to add a new tag")
                    new_tag_log(request.remote_addr, get_user(), tag_data["tag_name"], failed=True)
                    return "servererror"
            else:
                error_log(request.remote_addr, get_user(), "The new tag already exists")
                new_tag_log(request.remote_addr, get_user(), tag_data["tag_name"], failed=True)
                return "tagexists"
        except Exception as e:
            new_tag_log(request.remote_addr, get_user(), tag_data["tag_name"], failed=True)
            error_log(request.remote_addr, get_user(), "There was an error while attempting to create a new tag", theException=traceback.format_exc())
            return "servererror"
    else:
        access_log(request.remote_addr, get_user(), "/tags/add/validate/ (Add Tag Validate)", failed=True, no_auth=True)
        return redirect("/users/login/")

#Change Tag Type
@app.route("/tags/type/change/", methods=["POST"])
def tag_change_type():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/tags/type/change/ (Change Tag Type)")
        type_data = request.get_data()
        type_data = type_data.decode()
        type_data = ast.literal_eval(type_data)
        type_data["type_tag_name"] = tag_get_name(type_data["type_tag_id"])
        if tag_type_change(type_data) is True:
            tag_type_change_log(request.remote_addr, get_user(), type_data["type_tag_name"], type_data["type_newtype"])
            return "success"
        else:
            tag_type_change_log(request.remote_addr, get_user(), type_data["type_tag_name"], type_data["type_newtype"], failed=True)
            return "servererror"
    else:
        access_log(request.remote_addr, get_user(), "/tags/type/change/ (Change Tag Type)", failed=True, no_auth=True)
        return redirect("/login/")

#Get Closest Tag
@app.route("/tags/search/closest/", methods=["POST"])
def tag_get_closest():
    try:
        if current_user.is_authenticated:
            access_log(request.remote_addr, get_user(), "/tags/search/closest/ (Get Closest Tag)")
            tag = request.get_data()
            tag = tag.decode()
            closest_tag = tag_get_similar(tag)
            if closest_tag is not None:
                return str(closest_tag)
            else:
                return "-999notag"
    except:
        return "-999notag"    

#Developers & Publishers (Devpubs)
#Developer List 
@app.route("/developers/")
@app.route("/developers/pid=<pid>")
@app.route("/developers/pid=<pid>?search=<search>")
def developer_list(pid=0, no_results=10, search=""):
    try:
        if request.args.get("pid", None) is not None:
            pid = request.args.get("pid", None)
        if request.args.get("search", None) is not None:
            if request.args.get("search", None) != "" and request.args.get("search", None).isspace() is False:
                search = request.args.get("search", None)
        if type(pid) == str:
            pid = int(pid)
        devpubs = devpub_get_selection(pid, search=search)
        current_page = get_current_page(pid, no_results)
        access_log(request.remote_addr, get_user(), "/developers/pid=" + str(pid) + "?search=" + str(search) + " (Developers List)")
        return render_template("devpubs/developer_list.html", page_name="All Developers", c_version=version, devpub_list=devpubs[0], no_pages=devpubs[1], no_results=no_results, pid=pid, current_page=current_page, total_results=devpubs[2], tag_search=search)
    except Exception as e:
        try:
            devpubs = devpub_get_selection(0)
            access_log(request.remote_addr, get_user(), "/developers/pid=" + str(pid) + " (Developers List)", failed=True, default=True)
            error_log(request.remote_addr, get_user(), "An error occurred while trying to show the selected developer page", theException=traceback.format_exc())
            current_page = get_current_page(pid, no_results)
            return render_template("devpubs/developer_list.html", page_name="All Developers", c_version=version, devpub_list=devpubs[0], no_pages=devpubs[1], no_results=no_results, pid=pid, current_page=current_page, total_results=devpubs[2])
        except:
            access_log(request.remote_addr, get_user(), "/developers/pid=" + str(pid) + " (Developers List)", failed=True, default=True)
            error_log(request.remote_addr, get_user(), "An error occurred while trying to show the default developer page. Are there no developers?", theException=traceback.format_exc())
            return render_template("devpubs/developer_list.html", page_name="All Developers", c_version=version)
        
#Publisher List 
@app.route("/publishers/")
@app.route("/publishers/pid=<pid>")
@app.route("/publishers/pid=<pid>?search=<search>")
def publisher_list(pid=0, no_results=10, search=""):
    try:
        if request.args.get("pid", None) is not None:
            pid = request.args.get("pid", None)
        if request.args.get("search", None) is not None:
            if request.args.get("search", None) != "" and request.args.get("search", None).isspace() is False:
                search = request.args.get("search", None)
        if type(pid) == str:
            pid = int(pid)
        devpubs = devpub_get_selection(pid, is_pub=True, search=search)
        current_page = get_current_page(pid, no_results)
        access_log(request.remote_addr, get_user(), "/publishers/pid=" + str(pid) + "?search=" + str(search) + " (publishers List)")
        return render_template("devpubs/publisher_list.html", page_name="All publishers", c_version=version, devpub_list=devpubs[0], no_pages=devpubs[1], no_results=no_results, pid=pid, current_page=current_page, total_results=devpubs[2], tag_search=search)
    except:
        try:
            devpubs = devpub_get_selection(pid, is_pub=True)
            access_log(request.remote_addr, get_user(), "/publishers/pid=" + str(pid) + " (publishers List)", failed=True, default=True)
            error_log(request.remote_addr, get_user(), "An error occurred while trying to show the selected publishers page", theException=traceback.format_exc())
            current_page = get_current_page(pid, no_results)
            return render_template("devpubs/publisher_list.html", page_name="All publishers", c_version=version, devpub_list=devpubs[0], no_pages=devpubs[1], no_results=no_results, pid=pid, current_page=current_page, total_results=devpubs[2])
        except:
            access_log(request.remote_addr, get_user(), "/publishers/pid=" + str(pid) + " (publishers List)", failed=True, default=True)
            error_log(request.remote_addr, get_user(), "An error occurred while trying to show the default publishers page. Are there no publishers?", theException=traceback.format_exc())
            return render_template("devpubs/publisher_list.html", page_name="All Developers", c_version=version)

#Individual Devpub
@app.route("/devpubs/devpub_id=<devpub_id>")
def devpub_page(devpub_id=0):
    try:
        devpub_data = devpub_get_individual(devpub_id)
        developer_name = "No Developer?"
        if devpub_data is not None:
            developer_name = devpub_data["developer_name"]
        access_log(request.remote_addr, get_user(), "/devpubs/devpub_id=" + str(devpub_id) + " (Individual Devpub)")
        approval = devpub_get_approved(devpub_id)
        approval_date = devpub_get_approval_date(devpub_id)
        denial = devpub_get_denial(devpub_id)
        denial_reason = devpub_get_denial_reason(devpub_id)
        games = devpub_get_games(devpub_id)
        return render_template("devpubs/individual_devpub.html", page_name=developer_name, devpub_data=devpub_data, is_approved=approval, denied=denial, denial_desc=denial_reason, aDate=approval_date, game_links=games, c_version=version)
    except Exception as e:
        error_log(request.remote_addr, get_user(), "An error occurred when trying to load an invididual devpub page", traceback.format_exc())
        access_log(request.remote_addr, get_user(), "/devpubs/devpubs=" + str(devpub_id) + " (Individual Devpub)", failed=True)
        abort(404)

#Add Devpub
@app.route("/devpubs/add/")
def devpub_add():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/devpubs/add/ (Add Devpub)")
        return render_template("devpubs/devpub_add.html", page_name="Add New Developer/Publisher", c_version=version)
    else:
        access_log(request.remote_addr, get_user(), "/devpubs/add/ (Add Devpub)", no_auth=True, failed=True)
        return redirect("/users/login/")
#Devpub Validate
@app.route("/devpubs/add/validate/", methods=["POST"])
def debpub_add_validate():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/devpubs/add/validate/ (Add Devpub Validate)")
        devpub_data = request.get_data()
        devpub_data = devpub_data.decode()
        devpub_data = ast.literal_eval(devpub_data)
        try:
            if test_datetime(devpub_data["developer_foundDate"]) is False:
                return "invalidfounding"
            if devpub_data["developer_defunctDate"].isspace() is False and devpub_data["developer_defunctDate"] != "" and devpub_data["developer_defunctDate"] != "NDATE":
                if test_datetime(devpub_data["developer_defunctDate"]) is False:
                    return "invaliddefunct"
            else:
                devpub_data["developer_defunctDate"] = None
            if devpub_check_exists(devpub_data["developer_name"], devpub_data["developer_isPub"]) is False:
                if devpub_add_new(devpub_data, current_user.id) is True:
                    new_developer_log(request.remote_addr, get_user(), devpub_data["developer_name"])
                    return "success"
                else:
                    error_log(request.remote_addr, get_user(), "An error occurred while trying to add a new developer")
                    new_developer_log(request.remote_addr, get_user(), devpub_data["developer_name"], failed=True)
                    return "servererror"
            else:
                error_log(request.remote_addr, get_user(), "The new developer already exists")
                new_developer_log(request.remote_addr, get_user(), devpub_data["developer_name"], failed=True)
                return "developerexists"
        except Exception as e:
            new_developer_log(request.remote_addr, get_user(), devpub_data["developer_name"], failed=True)
            error_log(request.remote_addr, get_user(), "There was an error while attempting to create a new developer", theException=traceback.format_exc())
            return "servererror"
    else:
        access_log(request.remote_addr, get_user(), "/devpubs/add/validate/ (Add Devpub Validate)", failed=True, no_auth=True)
        return redirect("/users/login/")

'''User Routes'''
#Account PAge
@app.route("/users/account/")
def user_account():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/users/account/ (Account Page)")
        user_data = user_single_get_all(current_user.id)
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
                if user_login_passcheck(userdata):
                    admin_stat = user_check_admin(userdata["user_name"])
                    login_user(User(user_get_id(userdata["user_name"]), userdata["user_name"], admin_stat[0], admin_stat[1]))
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
        
#Update Username
@app.route("/users/modify/username/", methods=["POST"])
def user_change_username():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/users/modify/username/ (Modify Username)")
        new_username = request.get_data()
        new_username = new_username.decode()
        new_username = ast.literal_eval(new_username)
        if current_user.username != new_username["user_name"]:
            if user_check_exists(new_username["user_name"]) is False:
                old_username = get_user()
                if user_modify_username(current_user.id, new_username["user_name"]) is True:
                    modify_user_log(request.remote_addr, old_username, new_username["user_name"], is_username=True)
                    return "success"
                else:
                    modify_user_log(request.remote_addr, get_user(), new_username["user_name"], is_username=True, failed=True)
                    return "servererror"
            else:
                modify_user_log(request.remote_addr, get_user(), new_username["user_name"], is_username=True, failed=True)
                return "userexists"
        else:
            modify_user_log(request.remote_addr, get_user(), new_username["user_name"], is_username=True, failed=True)
            return "samename"
    else:
        return "servererror"
    
#Update Email
@app.route("/users/modify/email/", methods=["POST"])
def user_change_email():
    if current_user.is_authenticated:
        access_log(request.remote_addr, get_user(), "/users/modify/email/ (Modify Email)")
        new_email = request.get_data()
        new_email = new_email.decode()
        new_email = ast.literal_eval(new_email)
        old_email = user_get_email(current_user.id)
        if old_email != new_email["user_email"]:
            if user_modify_email(current_user.id, new_email["user_email"]) is True:
                modify_user_log(request.remote_addr, get_user(), new_email["user_email"], is_email=True)
                return "success"
            else:
                modify_user_log(request.remote_addr, get_user(), new_email["user_email"], is_email=True, failed=True)
                return "servererror"
        else:
            modify_user_log(request.remote_addr, get_user(), new_email["user_email"], is_email=True, failed=True)
            return "sameemail"
    else:
        return "servererror"

#Delete Account    
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
    
'''Mod Routes'''
#Main
@app.route("/mod/")
def mod_main():
    if current_user.is_authenticated:
        if current_user.is_mod:
            access_log(request.remote_addr, get_user(), "/mod/ (Mod: Main)")
            return render_template("mod/mod_main.html", page_name="Mod: Main", c_version=version)
        else:
            access_log(request.remote_addr, get_user(), "/mod/ (Mod: Main)", failed=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/mod/ (Mod: Main)", failed=True)
        abort(404)

#Developer Approvals
@app.route("/mod/approvals/games/")
def mod_approval_games():
    if current_user.is_authenticated:
        if current_user.is_mod:
            games = game_get_unapproved()
            access_log(request.remote_addr, get_user(), "/mod/approvals/games/ (Mod: Game Approvals)")
            return render_template("mod/mod_approvals_games.html", page_name="Mod: Game Approvals", c_version=version, game_data=games)
        else:
            abort(404)
    else:
        abort(404)
#Validate
@app.route("/mod/approvals/games/game_id=<game_id>")
def mod_approval_games_validate(game_id=0):
    if current_user.is_authenticated:
        if current_user.is_mod:
            access_log(request.remote_addr, get_user(), "/mod/approvals/games/game_id=" + str(game_id) + " (Mod: Game Approvals Validate)")
            if game_get_approved(game_id) is False:
                if game_approve_user_link(game_id) is True:
                    game_approve_log(request.remote_addr, get_user(), game_get_name(game_id))
                else:
                    error_log(request.remote_addr, get_user(), "An error occurred while trying to approve a game")
                    game_approve_log(request.remote_addr, get_user(), game_get_name(game_id), failed=True)
            else:
                error_log(request.remote_addr, get_user(), "The game is already approved")
                game_approve_log(request.remote_addr, get_user(), game_get_name(game_id), failed=True, already_approved=True)
            return redirect("/games/game_id=" + str(game_id))
        else:
            access_log(request.remote_addr, get_user(), "/mod/approvals/games/game_id=" + str(game_id) + " (Mod: Game Approvals Validate)", failed=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/mod/approvals/games/game_id=" + str(game_id) + " (Mod: Game Approvals Validate)", failed=True, no_auth=True)
        abort(404)
#Deny
@app.route("/mod/approvals/games/deny/", methods=["POST"])
def mod_approval_games_deny():
    if current_user.is_authenticated:
        if current_user.is_mod:
            access_log(request.remote_addr, get_user(), "mod/approvals/games/deny/ (Mod: Game Approvals Deny)")
            deny_data = request.get_data()
            deny_data = deny_data.decode()
            deny_data = ast.literal_eval(deny_data)
            deny_data["denial_game_title"] = game_get_name(deny_data["denial_game_id"])
            try:
                if game_get_denied(deny_data["denial_game_id"]) is False:
                    if game_deny_user_link(deny_data) is True:
                        game_approve_log(request.remote_addr, get_user(), deny_data["denial_game_title"], denied=True)
                        return "success"
                    else:
                        error_log(request.remote_addr, get_user(), "An error occurred while trying to deny a game")
                        game_approve_log(request.remote_addr, get_user(), deny_data["denial_game_title"], denied=True, failed=True)
                        return "servererror"
                else:
                    error_log(request.remote_addr, get_user(), "The game is already denied")
                    game_approve_log(request.remote_addr, get_user(), deny_data["denial_game_title"], failed=True, already_approved=True, denied=True)
                    return "alreadydenied"
            except Exception as e:
                error_log(request.remote_addr, get_user(), "An error occurred while trying to deny a game", theException=traceback.format_exc())
                game_approve_log(request.remote_addr, get_user(), deny_data["denial_game_title"], failed=True, denied=True)
                return "servererror"
        else:
            access_log(request.remote_addr, get_user(), "mod/approvals/games/deny/ (Mod: Game Approvals Deny)", failed=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "mod/approvals/games/deny/ (Mod: Game Approvals Deny)", failed=True, no_auth=True)
        abort(404)

#Developer Approvals
@app.route("/mod/approvals/devpubs/")
def mod_approval_devpubs():
    if current_user.is_authenticated:
        if current_user.is_mod:
            devpubs = devpub_get_unapproved()
            access_log(request.remote_addr, get_user(), "/mod/approvals/devpubs/ (Mod: Devpub Approvals)")
            return render_template("mod/mod_approvals_developers.html", page_name="Mod: Devpub Approvals", c_version=version, devpub_data=devpubs)
        else:
            abort(404)
    else:
        abort(404)
#Validate
@app.route("/mod/approvals/devpubs/developer_id=<developer_id>")
def mod_approval_devpub_validate(developer_id=0):
    if current_user.is_authenticated:
        if current_user.is_mod:
            access_log(request.remote_addr, get_user(), "/mod/approvals/devpubs/developer_id=" + str(developer_id) + " (Mod: Devpub Approvals Validate)")
            if devpub_get_approved(developer_id) is False:
                if devpub_approve_user_link(developer_id) is True:
                    developer_approve_log(request.remote_addr, get_user(), devpub_get_name(developer_id))
                else:
                    error_log(request.remote_addr, get_user(), "An error occurred while trying to approve a devpub")
                    developer_approve_log(request.remote_addr, get_user(), devpub_get_name(developer_id), failed=True)
            else:
                error_log(request.remote_addr, get_user(), "The devpub is already approved")
                developer_approve_log(request.remote_addr, get_user(), devpub_get_name(developer_id), failed=True, already_approved=True)
            return redirect("/devpubs/devpub_id=" + str(developer_id))
        else:
            access_log(request.remote_addr, get_user(), "/mod/approvals/devpubs/developer_id=" + str(developer_id) + " (Mod: Devpub Approvals Validate)", failed=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/mod/approvals/devpubs/developer_id=" + str(developer_id) + " (Mod: Devpub Approvals Validate)", failed=True, no_auth=True)
        abort(404)
#Deny
@app.route("/mod/approvals/devpubs/deny/", methods=["POST"])
def mod_approval_devpub_deny():
    if current_user.is_authenticated:
        if current_user.is_mod:
            access_log(request.remote_addr, get_user(), "mod/approvals/devpubs/deny/ (Mod: Devpubs Approvals Deny)")
            deny_data = request.get_data()
            deny_data = deny_data.decode()
            deny_data = ast.literal_eval(deny_data)
            deny_data["denial_developer_title"] = devpub_get_name(deny_data["denial_developer_id"])
            try:
                if devpub_get_denial(deny_data["denial_developer_id"]) is False:
                    if devpub_deny_user_link(deny_data) is True:
                        developer_approve_log(request.remote_addr, get_user(), deny_data["denial_developer_title"], denied=True)
                        return "success"
                    else:
                        error_log(request.remote_addr, get_user(), "An error occurred while trying to deny a devpub")
                        developer_approve_log(request.remote_addr, get_user(), deny_data["denial_developer_title"], denied=True, failed=True)
                        return "servererror"
                else:
                    error_log(request.remote_addr, get_user(), "The devpub is already denied")
                    developer_approve_log(request.remote_addr, get_user(), deny_data["denial_developer_title"], failed=True, already_approved=True, denied=True)
                    return "alreadydenied"
            except Exception as e:
                error_log(request.remote_addr, get_user(), "An error occurred while trying to deny a devpub", theException=traceback.format_exc())
                developer_approve_log(request.remote_addr, get_user(), deny_data["denial_developer_title"], failed=True, denied=True)
                return "servererror"
        else:
            access_log(request.remote_addr, get_user(), "mod/approvals/devpubs/deny/ (Mod: Devpubs Approvals Deny)", failed=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "mod/approvals/devpubs/deny/ (Mod: Devpubs Approvals Deny)", failed=True, no_auth=True)
        abort(404)

#Tag Approvals
@app.route("/mod/approvals/tags/")
def mod_approval_tags():
    if current_user.is_authenticated:
        if current_user.is_mod:
            tags = tag_get_unapproved()
            access_log(request.remote_addr, get_user(), "/mod/approvals/tags/ (Mod: Tag Approvals)")
            return render_template("mod/mod_approvals_tags.html", page_name="Mod: Tag Approvals", c_version=version, tag_data=tags)
        else:
            abort(404)
    else:
        abort(404)
#Validate
@app.route("/mod/approvals/tags/tag_id=<tag_id>")
def mod_approval_tag_validate(tag_id=0):
    if current_user.is_authenticated:
        if current_user.is_mod:
            access_log(request.remote_addr, get_user(), "/mod/approvals/tags/tag_id=" + str(tag_id) + " (Mod: Tag Approvals Validate)")
            if tag_get_approved(tag_id) is False:
                if tag_approve_user_link(tag_id) is True:
                    tag_approve_log(request.remote_addr, get_user(), tag_get_name(tag_id))
                else:
                    error_log(request.remote_addr, get_user(), "An error occurred while trying to approve a tag")
                    tag_approve_log(request.remote_addr, get_user(), tag_get_name(tag_id), failed=True)
            else:
                error_log(request.remote_addr, get_user(), "The tag is already approved")
                tag_approve_log(request.remote_addr, get_user(), tag_get_name(tag_id), failed=True, already_approved=True)
            return redirect("/tags/tag_id=" + str(tag_id))
        else:
            access_log(request.remote_addr, get_user(), "/mod/approvals/tags/developer_id=" + str(tag_id) + " (Mod: Tag Approvals Validate)", failed=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/mod/approvals/tags/developer_id=" + str(tag_id) + " (Mod: Tag Approvals Validate)", failed=True, no_auth=True)
        abort(404)
#Deny
@app.route("/mod/approvals/tags/deny/", methods=["POST"])
def mod_approval_tag_deny():
    if current_user.is_authenticated:
        if current_user.is_mod:
            access_log(request.remote_addr, get_user(), "mod/approvals/tags/deny/ (Mod: Tag Approvals Deny)")
            tag_data = request.get_data()
            tag_data = tag_data.decode()
            tag_data = ast.literal_eval(tag_data)
            tag_data["denial_tag_name"] = tag_get_name(tag_data["denial_tag_id"])
            try:
                if tag_get_denial(tag_data["denial_tag_id"]) is False:
                    if tag_deny_user_link(tag_data) is True:
                        tag_approve_log(request.remote_addr, get_user(), tag_data["denial_tag_name"], denied=True)
                        return "success"
                    else:
                        error_log(request.remote_addr, get_user(), "An error occurred while trying to deny a tag")
                        tag_approve_log(request.remote_addr, get_user(), tag_data["denial_tag_name"], denied=True, failed=True)
                        return "servererror"
                else:
                    error_log(request.remote_addr, get_user(), "The tag is already denied")
                    tag_approve_log(request.remote_addr, get_user(), tag_data["denial_tag_name"], failed=True, already_approved=True, denied=True)
                    return "alreadydenied"
            except Exception as e:
                error_log(request.remote_addr, get_user(), "An error occurred while trying to deny a tag", theException=traceback.format_exc())
                tag_approve_log(request.remote_addr, get_user(), tag_data["denial_tag_name"], failed=True, denied=True)
                return "servererror"
        else:
            access_log(request.remote_addr, get_user(), "mod/approvals/tags/deny/ (Mod: Tag Approvals Deny)", failed=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "mod/approvals/tags/deny/ (Mod: Tag Approvals Deny)", failed=True, no_auth=True)
        abort(404)

#Update Routes
#Get updates
@app.route("/updates/get/", methods=["POST"])
def update_get():
    try:
        access_log(request.remote_addr, get_user(), "/updates/get/ (Get Updates)")
        retrieve_name = request.get_data()
        retrieve_name = retrieve_name.decode()
        retrieve_name = ast.literal_eval(retrieve_name)
        return str(update_get_all_versions(int(retrieve_name["update_id"]), u_type=retrieve_name["update_type"]))
    except Exception as e:
        return "servererror"
    
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

#User Management
@app.route("/admin/management/users/")
def admin_user_management():
    if current_user.is_authenticated:
        if current_user.is_admin:
            access_log(request.remote_addr, get_user(), "/admin/management/users/ (Admin: User Management)", admin=True)
            return render_template("admin/admin_user_management.html", page_name="Admin: User Management", c_version=version, userdata=user_get_all())
        else:
            access_log(request.remote_addr, get_user(), "/admin/management/users/ (Admin: User Management)", failed=True, admin=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/admin/management/users/ (Admin: User Management)", failed=True, admin=True, no_auth=True)
        abort(404)
#Swap Admin Status
@app.route("/admin/management/users/swap_admin/user_id=<user_id>")
def admin_swap_admin_status(user_id=None):
    if current_user.is_authenticated:
        if current_user.is_admin:
            access_log(request.remote_addr, get_user(), "/admin/management/users/swap_admin/user_id=" + user_id + " (Admin: Swap Admin Status)", admin=True)
            admin_swap_stat(user_id)
            admin_swap_log(request.remote_addr, get_user(), swappedTo=user_check_admin(get_user())[1])
            if str(current_user.id) != user_id:
                return redirect("/admin/management/users/")
            else:
                return redirect("/")
        else:
            access_log(request.remote_addr, get_user(), "/admin/management/users/swap_admin/user_id=" + user_id + " (Admin: Swap Admin Status)", admin=True, failed=True, no_auth=True)
            abort(404)
            admin_swap_log(request.remote_addr, get_user(), failed=True)
    else:
        access_log(request.remote_addr, get_user(), "/admin/management/users/swap_admin/user_id=" + user_id + " (Admin: Swap Admin Status)", admin=True, failed=True, no_auth=True)
        admin_swap_log(request.remote_addr, get_user(), failed=True)
        abort(404)
#Swap Mod Status
@app.route("/admin/management/users/swap_mod/user_id=<user_id>")
def admin_swap_mod_status(user_id=None):
    if current_user.is_authenticated:
        if current_user.is_admin:
            access_log(request.remote_addr, get_user(), "/admin/management/users/swap_mod/user_id=" + user_id + " (Admin: Swap Mod Status)", admin=True)
            admin_swap_stat(user_id, swap_mod=True)
            admin_swap_log(request.remote_addr, get_user(), swappedTo=user_check_admin(get_user())[0], isMod=True)
            return redirect("/admin/management/users/")
        else:
            access_log(request.remote_addr, get_user(), "/admin/management/users/swap_mod/user_id=" + user_id + " (Admin: Swap Mod Status)", admin=True, failed=True, no_auth=True)
            admin_swap_log(request.remote_addr, get_user(), failed=True, isMod=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/admin/management/users/swap_mod/user_id=" + user_id + " (Admin: Swap Mod Status)", admin=True, failed=True, no_auth=True)
        admin_swap_log(request.remote_addr, get_user(), failed=True, isMod=True)
        abort(404)
#Delete User
@app.route("/admin/management/users/delete/user_id=<user_id>")
def admin_user_delete(user_id):
    if current_user.is_authenticated:
        if current_user.is_admin:
            access_log(request.remote_addr, get_user(), "/admin/management/users/delete/user_id=" + str(user_id) + " (Admin: User Delete)", admin=True)
            user_delete(user_id)
            if user_id == str(current_user.id):
                login_log(request.remote_addr, get_user(), logout=True, admin=True, auto=True)
                logout_user()
                return redirect("/")
            else:
                return redirect("/admin/management/users/")
        else:
            access_log(request.remote_addr, get_user(), "/admin/management/users/delete/user_id=" + str(user_id) + " (Admin: User Delete)", admin=True, failed=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/admin/management/users/delete/user_id=" + str(user_id) + " (Admin: User Delete)", admin=True, failed=True, no_auth=True)
        abort(404)

#Database Management
@app.route("/admin/management/databasae/")
def admin_database_manage():
    if current_user.is_authenticated:
        if current_user.is_admin:
            access_log(request.remote_addr, get_user(), "/admin/management/databasae/ (Admin: Database Management)", admin=True)
            return render_template("admin/admin_database_management.html", page_name="Admin: Database Management", c_version=version)
        else:
            access_log(request.remote_addr, get_user(), "/admin/management/databasae/ (Admin: Database Management)", admin=True, failed=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/admin/management/databasae/ (Admin: Database Management)", admin=True, failed=True, no_auth=True)
        abort(404)
#Dump Database
@app.route("/admin/management/database/dump/")
def admin_database_dump():
    if current_user.is_authenticated:
        if current_user.is_admin:
            if deployed is False:
                access_log(request.remote_addr, get_user(), "/admin/management/database/dump/ (Dump Database Data)", admin=True)
                dump_status = admin_dump_database()
                if dump_status[0] is True:
                    return render_template("notification.html", page_name="Admin: Database Dump", notification_title="Database has been dumped", notification="The database's data has been dumped to db_backup.dump.", return_message="Return to database management", dir_to_use="admin_database_manage")
                else:
                    error_log(request.remote_addr, get_user(), "There was an error while trying to dump database data", theException=dump_status[1], admin=True)
                    return render_template("notification.html", page_name="Admin: Database Dump", notification_title="Database dump failed", notification="The following error occurred while trying to dump database data:\n" + str(dump_status[1]), return_message="Return to database management", dir_to_use="admin_database_manage")
            else:
                access_log(request.remote_addr, get_user(), "/admin/management/database/dump/ (Dump Database Data)", admin=True, failed=True, no_auth=True)
                error_log(request.remote_addr, get_user(), "The database is in a container. Python cannot use mysqldump on a container.", admin=True)
                return render_template("notification.html", page_name="Admin: Database Dump", notification_title="Database is in a container", notification="The database is in a Docker container. Python cannot run mysqldump on a container. Please run mysqldump in the container's terminal.", return_message="Return to database management", dir_to_use="admin_database_manage")
        else:
            access_log(request.remote_addr, get_user(), "/admin/management/database/dump/ (Dump Database Data)", admin=True, failed=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/admin/management/database/dump/ (Dump Database Data)", admin=True, failed=True, no_auth=True)
        abort(404)
#Load Data From CSV
@app.route("/admin/management/database/load_csv/")
def admin_load_csv():
    if current_user.is_authenticated:
        if current_user.is_admin:
            access_log(request.remote_addr, get_user(), "/admin/management/database/load_csv/ (Admin: Load From CSV)", admin=True)
            return render_template("confirmation.html", page_name="Are you sure?", message="Are you sure you want to load from CSV? This may take a long time and the server will hang until it is done.", dir_to_use="admin_load_csv_confirmed", dir_to_return="admin_database_manage", yes_message="Yes, load the CSV", no_message="No, return to database management", c_version=version)
        else:
            access_log(request.remote_addr, get_user(), "/admin/management/database/load_csv/ (Admin: Load From CSV)", admin=True, failed=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/admin/management/database/load_csv/ (Admin: Load From CSV)", admin=True, failed=True, no_auth=True)
        abort(404)
#Confirmed
@app.route("/admin/management/database/load_csv/confirmed/")
def admin_load_csv_confirmed():
    if current_user.is_authenticated:
        if current_user.is_admin:
            access_log(request.remote_addr, get_user(), "/admin/management/database/load_csv/confirmed/ (Admin: Load From CSV Confirmed)", admin=True)
            read_scraped_data(current_user.id)
            return redirect("/admin/")
        else:
            access_log(request.remote_addr, get_user(), "/admin/management/database/load_csv/confirmed/ (Admin: Load From CSV Confirmed)", admin=True, failed=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/admin/management/database/load_csv/confirmed/ (Admin: Load From CSV Confirmed)", admin=True, failed=True, no_auth=True)
        abort(404)

#Delete all data
@app.route("/admin/management/database/reload/")
def admin_database_reload_validation():
    if current_user.is_authenticated:
        if current_user.is_admin:
            access_log(request.remote_addr, get_user(), "/admin/management/database/reload/ (Admin: Reload Database)", admin=True)
            return render_template("confirmation.html", page_name="Are you sure?", message="Are you sure you want to delete all data from the database?\nNote: The database will be dumped first.", dir_to_use="admin_database_reload_confirmed", dir_to_return="admin_database_manage", yes_message="Yes, delete the data from the database", no_message="No, return to database management", c_version=version)
        else:
            access_log(request.remote_addr, get_user(), "/admin/management/database/reload/ (Admin: Reload Database)", admin=True, failed=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/admin/management/database/reload/ (Admin: Reload Database)", admin=True, failed=True, no_auth=True)
        abort(404)
@app.route("/admin/management/database/reload/confirmed/")
def admin_database_reload_confirmed():
    if current_user.is_authenticated:
        if current_user.is_admin:
            access_log(request.remote_addr, get_user(), "/admin/management/database/reload/confirmed/ (Admin: Reload Database Confirmed)", admin=True)
            admin_database_dump()
            admin_database_reload()
            old_user = get_user()
            logout_user()
            login_log(request.remote_addr, old_user, logout=True, auto=True, admin=True)
            return redirect("/")
        else:
            access_log(request.remote_addr, get_user(), "/admin/management/database/reload/confirmed/ (Admin: Reload Database Confirmed)", admin=True, failed=True, no_auth=True)
            abort(404)
    else:
        access_log(request.remote_addr, get_user(), "/admin/management/database/reload/confirmed/ (Admin: Reload Database Confirmed)", admin=True, failed=True, no_auth=True)
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
#For simplicity, if the website encounters a 405 error, it will redirect and show as a 404 instead.

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