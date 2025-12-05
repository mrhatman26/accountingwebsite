from misc import get_time

#Access and errors
def access_log(ip, username, wwAccessed, failed=False, admin=False, default=False, no_auth=False):
    log_file = open("static/logs.txt", "at")
    text = get_time()
    if admin is False:
        if failed is False:
            text = text + ": " + ip + " (User: " + username + ") successfully accessed " + wwAccessed
        else:
            if default is False:
                if no_auth is False:
                    text = text + ": " + ip + " (User: " + username + ") FAILED to access " + wwAccessed
                else:
                    text = text + ": " + ip + " (User: " + username + ") FAILED to access " + wwAccessed + " as the user was not authorised"
            else:
                if no_auth is False:
                    text = text + ": " + ip + " (User: " + username + ") FAILED to access " + wwAccessed + " (The default page was returned instead)"
                else:
                    text = text + ": " + ip + " (User: " + username + ") FAILED to access " + wwAccessed + " as the user was not authorised (The default page was returned instead)"
    else:
        if failed is False:
            text = text + " (ADMIN): " + ip + " (User: " + username + ") successfully accessed admin resource " + wwAccessed
        else:
            if default is False:
                if no_auth is False:
                    text = text + " (ADMIN): " + ip + " (User: " + username + ") FAILED to access admin resource" + wwAccessed
                else:
                    text = text + " (ADMIN): " + ip + " (User: " + username + ") FAILED to access admin resource" + wwAccessed + " as the user was not logged in."
            else:
                if no_auth is False:
                    text = text + " (ADMIN): " + ip + " (User: " + username + ") FAILED to access admin resource" + wwAccessed + " (The default page was returned instead)"
                else:
                    text = text + " (ADMIN): " + ip + " (User: " + username + ") FAILED to access admin resource" + wwAccessed + " as the user was not logged in (The default page was returned instead)"
    log_file.write(text)
    log_file.close()

def error_log(ip, username, wFailed, theException=None, admin=False):
    log_file = open("static/logs.txt", "at")
    text = get_time()
    if admin is False:
        if theException is None:
            text = text + ": " + ip + " (User: " + username + ") encountered the following error: " + wFailed + "\nNo exception information available."
        else:
            text = text + ": " + ip + " (User: " + username + ") encountered the following error: " + wFailed + "\nException:\n" + str(theException)
    else:
        if theException is None:
            text = text + " (ADMIN): " + ip + " (User: " + username + ") encountered the following error: " + wFailed + "\nNo exception information available."
        else:
            text = text + " (ADMIN): " + ip + " (User: " + username + ") encountered the following error: " + wFailed + "\nException:\n" + str(theException)
    log_file.write(text)
    log_file.close()

#Users
def new_user_log(ip, newUser, failed=False, admin=False):
    log_file = open("static/logs.txt", "at")
    text = get_time()
    if admin is False:
        if failed is False:
            text = text + ": " + ip + " successfully created a new account with the username of " + str(newUser)
        else:
            text = text + ": " + ip + " FAILED to created a new account with the username of " + str(newUser)
    else:
        if failed is False:
            text = text + " (ADMIN): " + ip + " successfully created a new account with the username of " + str(newUser) + " with admin status applied"
        else:
            text = text + " (ADMIN): " + ip + " FAILED to created a new account with the username of " + str(newUser) + " with admin status applied"
    log_file.write(text)
    log_file.close()

def login_log(ip, username, failed=False, logout=False, admin=False, auto=False):
    log_file = open("static/logs.txt", "at")
    text = get_time()
    if admin is False:
        if failed is False:
            if logout is False:
                text = text + ": " + ip + " successfully logged in as " + username
            else:
                text = text + ": " + ip + " (User: " + username + ") successfully logged out of their account"
        else:
            if logout is False:
                text = text + ": " + ip + " FAILED to log in as " + username
            else:
                text = text + ": " + ip + " (User: " + username + ") FAILED to log out of their account"
    else:
        if failed is False:
            if logout is False:
                text = text + " (ADMIN): " + ip + " successfully logged in as " + username
            else:
                if auto is True:
                    text = text + " (ADMIN): " + ip + " (User: " + username + ") was automatically logged out of their account"
                else:
                    text = text + " (ADMIN): " + ip + " (User: " + username + ") successfully logged out of their account"
        else:
            if logout is False:
                text = text + " (ADMIN): " + ip + " FAILED to log in as " + username
            else:
                text = text + " (ADMIN): " + ip + " (User: " + username + ") FAILED to log out of their account"
    log_file.write(text)
    log_file.close()

def modify_user_log(ip, username, new_value, is_username=False, is_email=False, is_desc=False, failed=False):
    log_file = open("static/logs.txt", "at")
    text = get_time()
    if failed is False:
        if is_username is True:
            text = text + ": " + ip + " (User: " + username + ") successfully changed their username to " + new_value
        if is_email is True:
            text = text + ": " + ip + " (User: " + username + ") successfully changed their email to " + new_value
        if is_desc is True:
            text = text + ": " + ip + " (User: " + username + ") successfully changed their description to " + new_value
    else:
        if is_username is True:
            text = text + ": " + ip + " (User: " + username + ") FAILED to change their username to " + new_value
        if is_email is True:
            text = text + ": " + ip + " (User: " + username + ") FAILED to change their email to " + new_value
        if is_desc is True:
            text = text + ": " + ip + " (User: " + username + ") FAILED to change their description to " + new_value
    log_file.write(text)
    log_file.close()

def admin_swap_log(ip, username, failed=False, isMod=False, swappedTo=False):
    log_file = open("static/logs.txt", "at")
    text = get_time()
    if isMod is False:
        if failed is False:
            text = text + " (ADMIN): " + ip + " (User: " + username + ") successfully swapped admin status to " + str(swappedTo)
        else:
            text = text + " (ADMIN): " + ip + " (User: " + username + ") FAILED to swap admin status"
    else:
        if failed is False:
            text = text + " (ADMIN): " + ip + " (User: " + username + ") successfully swapped moderator status to " + str(swappedTo)
        else:
            text = text + " (ADMIN): " + ip + " (User: " + username + ") FAILED to swap moderator status"
    log_file.write(text)
    log_file.close()

def delete_user_log(ip, username, failed=False, admin=False):
    log_file = open("static/logs.txt", "at")
    text = get_time()
    if admin is False:
        if failed is False:
            text = text + ": " + ip + " successfully deleted the account of " + username
        else:
            text = text + ": " + ip + " FAILED to delete the account of " + username
    else:
        if failed is False:
            text = text + " (ADMIN): " + ip + " successfully deleted the account of " + username
        else:
            text = text + " (ADMIN): " + ip + " FAILED to delete the account of " + username
    log_file.write(text)
    log_file.close()