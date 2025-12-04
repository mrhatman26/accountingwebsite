import datetime as dt
version_file_dir = "./static/version.txt"

def get_version():
    version_file = open(version_file_dir, "w")
    version = version_file.readline()
    version_file.close()
    if version is not None:
        if version != "" and version.isspace() is False:
            return version
        else:
            return "(NO VERSION)"
    else:
        return "(NO VERSION)"
    
def update_version():
    version = dt.datetime.now()
    version = "(" + str(version.strftime(("%Y%m%d.%H%M%S"))) + ")"
    version_file = open(version_file_dir, "w")
    version_file.write(version)
    version_file.close()
    return version