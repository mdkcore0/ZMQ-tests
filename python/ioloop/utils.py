import datetime

def log(sign, ident, message, append=""):
    now = datetime.datetime.now().time()
    msg = "[%s] %s %s %s" % (now, ident, sign, message)

    if append != "":
        msg = "%s | %s" % (msg, append)

    print msg
