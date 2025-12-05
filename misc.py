import datetime as dt

def pause(message=None):
    if message is None:
        input("(Press ENTER to continue)")
    else:
        input(message)

def fprint(value):
    print(value, flush=True)

def get_time(no_brackets=False):
    current_time = dt.datetime.now()
    if no_brackets is False:
        return str("\n[" + current_time.strftime("%Y.%m.%d at %H:%M:%S") + "]")
    else:
        return str(current_time.strftime("%Y.%m.%d at %H:%M:%S"))