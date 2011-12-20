#part-handler

import base64

def list_types():
    return(["application/octet-stream"])

def handle_part(data,ctype,filename,payload):
    if ctype == "__end__" or ctype == "__begin__": return
    if ctype == "application/octet-stream":
        stream = "%s/%s" % ('/var/lib/cloud/instance/scripts',filename)
        f = open(stream, 'wb')
        # double decode because of https://bugs.launchpad.net/cloud-init/+bug/874342
        f.write(base64.b64decode(base64.b64decode(payload)))
        f.close()
        return
