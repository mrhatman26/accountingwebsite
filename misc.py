def pause(message=None):
    if message is None:
        input("(Press ENTER to continue)")
    else:
        input(message)

def fprint(value):
    print(value, flush=True)