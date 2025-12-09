import mysql.connector, hashlib
from db_config import *
from misc import fprint, pause
from global_vars import deployed

def string_hash(text):
    text = text.encode('utf-8')
    hash = hashlib.sha256()
    hash.update(text)
    return hash.hexdigest()

#Checks
def user_check_exists(username):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    try:
        cursor.execute("SELECT user_id FROM table_users WHERE user_name = %s", (str(username),))
        fetch = cursor.fetchall()
        cursor.close()
        database.close()
        if len(fetch) > 0:
            return True
        else:
            return False
    except:
        cursor.close()
        database.close()
        return False
    
def user_check_reconfirm(user_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    try:
        user = []
        cursor.execute("SELECT user_id, user_name, user_isAdmin FROM table_users WHERE user_id = %s", (str(user_id),))
        fetch = cursor.fetchall()
        cursor.close()
        database.close()
        if len(fetch) > 0:
            for item in fetch:
                user.append(item[0])
                user.append(item[1])
                user.append(item[2])
            return user
        else:
            return []
    except Exception as e:
        cursor.close()
        database.close()
        return []
    
def user_check_pass(userdata):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    try:
        cursor.execute("SELECT user_pass FROM table_users WHERE user_name = %s", (str(userdata["user_name"]),))
        fetch = cursor.fetchall()[0][0]
        cursor.close()
        database.close()
        if string_hash(userdata["user_password"]) == fetch:
            return True
        else:
            return False
    except:
        cursor.close()
        database.close()
        return False
    
def user_check_admin(user_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    try:
        cursor.execute("SELECT user_isAdmin FROM table_users WHERE user_name = %s", (str(user_id),))
        fetch = cursor.fetchall()[0][0]
        cursor.close()
        database.close()
        return bool(fetch)
    except:
        cursor.close()
        database.close()
        return False
    
#Get
def user_get_id(username):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    try:
        cursor.execute("SELECT user_id FROM table_users WHERE user_name = %s", (str(username),))
        fetch = cursor.fetchall()[0][0]
        cursor.close()
        database.close()
        return fetch
    except:
        cursor.close()
        database.close()
        return None
    
def user_get_username(user_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    try:
        cursor.execute("SELECT user_name FROM table_users WHERE user_name = %s", (str(user_id),))
        fetch = cursor.fetchall()[0][0]
        cursor.close()
        database.close()
        return fetch
    except:
        cursor.close()
        database.close()
        return None
    
def user_get_data(user_id):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    try:
        user_data = {}
        cursor.execute("SELECT user_id, user_name, user_email, user_setting_monthly, user_setting_del_prev, user_setting_def_p_use, user_setting_auto_month, user_setting_auto_next_date FROM table_users WHERE user_id = %s", (str(user_id),))
        fetch = cursor.fetchall()
        cursor.close()
        database.close()
        if len(fetch) > 0:
            fetch = fetch[0]
            user_data = {
                "user_id": fetch[0],
                "user_name": fetch[1],
                "user_email": fetch[2],
                "user_setting_monthly": fetch[3],
                "user_setting_del_prev": fetch[4],
                "user_setting_def_p_use": fetch[5],
                "user_setting_auto_month": fetch[6],
                "user_setting_auto_next_date": fetch[7],
            }
            return user_data
        else:
            return None
    except:
        cursor.close()
        database.close()
        return None
    
#Add/Modify
def user_add_new(new_userdata):
    database = mysql.connector.connect(**get_db_config(deployed))
    cursor = database.cursor()
    try:
        new_userdata["user_password"] = string_hash(new_userdata["user_password"])
        cursor.execute("INSERT INTO table_users (user_name, user_pass, user_email) VALUES (%s, %s, %s)", (new_userdata["user_name"], new_userdata["user_password"], new_userdata["user_email"],))
        database.commit()
        cursor.close()
        database.close()
        return True
    except:
        cursor.close()
        database.close()
        return False