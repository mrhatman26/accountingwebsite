from global_vars import local_password
def get_db_config(deployed):
    db_config = {}
    if deployed: #Deployed as in: Deployed in a Docker container.
        db_config = {
            'user': 'root',
            'password': 'boundingthroughtime',
            'host': 'localhost',
            'port': 1234,
            'database': 'moneydatabase'
        }
    else: #Not in a Docker container; running locally.
        db_config = {
            'user': 'root',
            'password': local_password,
            'host': 'localhost',
            'port': 3306,
            'database': 'moneydatabase'
        }
    return db_config