from flask import Flask, request, send_file, redirect
import os, reedsolo, time, hashlib
from Crypto.Cipher import AES

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = "./static/files/"

if __name__ == "__main__":
    if not os.path.exists("./static"):
        os.mkdir("static")
        os.mkdir("static/files")
        f = open("PASSWORD", 'w')
        f.write("password")
        f.close()
        f = open("setup.txt", 'w')
        f.write("""reedsolo: 32
autorecover: 1
autobackup: 0
backuplocation: .
recoverlocation: .""")
        x = open("first", 'w')
        x.write("Finish first setup!")
        x.close()
        f.close()



f = open("sample.html")
sample = f.read()
f.close()
configs = {}
password = "password"

def loadConfig():
    global configs, password
    f = open("setup.txt")
    cffg = f.read().replace(" ", "").removesuffix("\n")
    f.close()
    configs = {}
    for i in cffg.split("\n"):
        configs[i.split(":")[0]] = i.split(":")[1].split(",")
    f = open("PASSWORD")
    password = f.read()
    f.close()
loadConfig()

def padKey(key : str, salt = os.urandom(8)):
    return hashlib.pbkdf2_hmac("sha-512", key.encode(), salt, 1000000, 16), salt
def AESEncrypt(data : bytes, key : str):
    hash, salt = padKey(key)
    aes = AES.new(hash, AES.MODE_EAX)
    gibb, tag = aes.encrypt_and_digest(data)
    return gibb, tag, aes.nonce, salt
def AESDecrypt(gibb : bytes, key : str, nonce, tag, salt):
    hash, salt = padKey(key, salt)
    aes = AES.new(hash, AES.MODE_EAX, nonce=nonce)
    return aes.decrypt_and_verify(gibb, tag)
def fileAESEncrypt(file, key):
    f = open(file, 'rb')
    r = AESEncrypt(f.read(), key)
    f.close()
    f = open(file+".naes", 'wb')
    f.write(r[3]+r[2]+r[1]+r[0])
    f.close()
def fileAESDecrypt(file, key):
    f = open(file+".naes", 'rb')
    salt = f.read(8)
    nonce = f.read(16)
    tag = f.read(16)
    gibb = f.read()
    r = AESDecrypt(gibb, key, nonce, tag, salt)
    f.close()
    f = open("./static/temp", 'wb')
    f.write(r)
    f.close()
    return send_file("./static/temp", download_name=file.split("/")[len(file.split("/"))-1], as_attachment=True)

def readChunks(file, chunk_size=255-int(configs["reedsolo"][0])):
    global configs
    f = open(file, 'rb')
    chunks = []
    i = 0
    while True:
        chunk = f.read(chunk_size)
        print(f"Reading chunk {str(i)} of file {file}", end="\r")
        i += 1
        if not chunk:
            break
        chunks.append(chunk)
    f.close()
    print()
    return chunks
def ReedEncode(chunks):
    global configs
    rcs = reedsolo.RSCodec(int(configs["reedsolo"][0]))
    reeds = []
    i = 0
    for chunk in chunks:
        print(f"Encoding chunk {i}.", end="\r")
        i += 1
        reeds.append(rcs.encode(chunk)[len(chunk):])
    print()
    return reeds
def ReedDecode(reeds, chunks):
    global configs
    rcs = reedsolo.RSCodec(int(configs["reedsolo"][0]))
    corrects = []
    recovered = 0
    broken = 0
    correct = b""
    for i in range(len(reeds)):
        print(f"Decoding chunk {i}.", end="\r")
        try:
            correct += rcs.decode(chunks[i]+reeds[i])[0]
            recovered += 1
        except Exception as e:
            broken += 1
            correct += chunks[i]
    print()
    return correct, recovered, broken

def backupFile(file):
    global configs
    if configs["backuplocation"][0] == ".":
        a = open(file, 'rb')
        b = open(file+f".{str(round(time.time()))}.back", 'wb')
        b.write(a.read())
        a.close()
        b.close()
    else:
        a = open(file, 'rb')
        path = configs['backuplocation'][0]+'/'+file.split('/')[len(file.split('/'))-1]+f".{str(round(time.time()))}.back"
        b = open(path, 'wb')
        b.write(a.read())
        a.close()
        b.close()
        try:
            x = open('DBnR', 'x')
            x.close()
        except:
            pass
        x = open('DBnR', 'a')
        x.write(f"\n{file} -> {path}")
        x.close()
def setupRecoveryFile(file):
    global configs
    if configs["recoverlocation"][0] == ".":
        z = open(file+".reso", 'wb')
        bstr = b""
        j = 0
        for i in ReedEncode(readChunks(file)):
            print(f"Saving chunk {str(j)} of file {file}.", end="\r")
            j += 1
            bstr += i
        z.write(bstr)
        z.close()
        print()
    else:
        z = open(configs["recoverlocation"][0]+"/"+file.split("/")[len(file.split("/"))-1]+".reso", 'wb')
        bstr = b""
        j = 0
        for i in ReedEncode(readChunks(file)):
            print(f"Saving chunk {str(j)} of file {file}.", end="\r")
            j += 1
            bstr += i
        z.write(bstr)
        z.close()
        try:
            x = open('DBnR', 'x')
            x.close()
        except:
            pass
        x = open('DBnR', 'a')
        x.write(f"\n{file} -> {configs['recoverlocation'][0]+'/'+file.split('/')[len(file.split('/'))-1]+'.reso'}")
        x.close()
        print()
def recoverFile(file):
    global configs
    if configs["recoverlocation"][0] == ".":
        vars = ReedDecode(readChunks(file+".reso", int(configs["reedsolo"][0])), readChunks(file))
        recovery = vars[0]
        if recovery != "":
            x = open(file, "wb")
            x.write(recovery)
            x.close()
        return vars[1], vars[2]
    else:
        x = open("DBnR")
        r = x.read().removeprefix("\n").removesuffix("\n").split("\n")
        x.close()
        register = {}
        for item in r:
            register[item.split(" -> ")[0]] = item.split(" -> ")[1]
        vars = ReedDecode(readChunks(file, int(configs["reedsolo"][0])), readChunks(list(register.keys())[list(register.values()).index(file)]))
        recovery = vars[0]
        if recovery != "":
            x = open(file, "wb")
            x.write(recovery)
            x.close()
        return vars[1], vars[2]

def getFiles( folder = "files", add = "./static/"):
    global password
    files = os.listdir(add+folder)
    fold = add+folder
    retrn = ""
    for i in files:
        if os.path.isfile(f"{fold}/{i}"):
            if i.split('.')[len(i.split("."))-1] != "reso" and i.split('.')[len(i.split("."))-1] != "back" and i.split('.')[len(i.split("."))-1] != "naes":
                retrn += f"<a href='/static/{folder}/{i}?passw={password}' download>"
                retrn += "<h2 style='color: white'>"
                retrn += f"{i}</h2>\n"
            elif i.split('.')[len(i.split("."))-1] == "naes":
                retrn += f"<a href='/SuperSimpleFunctions/AES/decrypt_interface/{folder.replace('/', '|')}{i.replace('/', '|').replace('.naes', '')}?passw={password}'>"
                retrn += "<h2 style='color: lime'>"
                retrn += f"{i.replace('.naes', '')}</h2>\n"
            elif i.split('.')[len(i.split("."))-1] == "reso":
                retrn += f"<a href='/SuperSimpleFunctions/recovery/{folder.replace('/', '|')}{i.replace('.reso', '')}?passw={password}'>"
                retrn += "<h2 style='color: lightblue'>"
                retrn += f"{i.replace('.reso', '')}</h2>\n"
            elif i.split('.')[len(i.split("."))-1] == "back":
                retrn += f"<a href='/SuperSimpleFunctions/downloadbackup/{folder.replace('/', '|')}{i.replace('/', '|')}?passw={password}' download>"
                retrn += "<h2 style='color: lightgray'>"
                retrn += f"{i.replace('.back', '')}</h2>\n"
            
        else:
            retrn += f"<a href='/{folder.replace('/', '|')}{i}?passw={password}'>"
            retrn += f"<h2 style='color: orange'>{i}</h2>"
        
        retrn += "</a>"
    return retrn
def getFilesButDBnR(folder):
    global password
    files = os.listdir(folder)
    fold = folder
    retrn = ""
    for i in files:
        if os.path.isfile(f"{fold}/{i}"):
            if i.split('.')[len(i.split("."))-1] == "reso":
                retrn += f"<a href='/SuperSimpleFunctions/DBnR/recovery/{i.replace('/', '|')}?passw={password}'>"
                retrn += "<h2 style='color: lightblue'>"
                retrn += f"{i.replace('.reso', '')}</h2>\n"
            elif i.split('.')[len(i.split("."))-1] == "back":
                retrn += f"<a href='/SuperSimpleFunctions/DBnR/backup/{i.replace('/', '|')}?passw={password}'>"
                retrn += "<h2 style='color: lightgray'>"
                retrn += f"{i.replace('.back', '')}</h2>\n"
        retrn += "</a>"
    return retrn

def getFilesButDelete(folder = "files"):
    files = os.listdir("./static/"+folder)
    retrn = ""
    for i in files:
        retrn += f"<a href='/SuperSimpleFunctions/delete/butfr/{folder.replace('/', '|')}|{i}?passw={password}'>"
        retrn += "<h2 style='color: red'>"
        retrn += f"{i}</h2>\n"
        retrn += "</a>"
    return retrn
def getFilesButSetupRecovery(folder = "files"):
    files = os.listdir("./static/"+folder)
    retrn = ""
    for i in files:
        if os.path.isfile(f"./static/{folder}/{i}"):
            retrn += f"<a href='/SuperSimpleFunctions/setuprecovery/butfr/{folder.replace('/', '|')}|{i}?passw={password}'>"
            retrn += "<h2 style='color: lightblue'>"
            retrn += f"{i}</h2>\n"
            retrn += "</a>"
    return retrn
def getFilesButSetupBackup(folder = "files"):
    files = os.listdir("./static/"+folder)
    retrn = ""
    for i in files:
        if os.path.isfile(f"./static/{folder}/{i}"):
            retrn += f"<a href='/SuperSimpleFunctions/backup/butfr/{folder.replace('/', '|')}|{i}?passw={password}'>"
            retrn += "<h2 style='color: yellow'>"
            retrn += f"{i}</h2>\n"
            retrn += "</a>"
    return retrn
def getFilesButRename(folder = "files"):
    files = os.listdir("./static/"+folder)
    retrn = ""
    for i in files:
        if os.path.isfile(f"./static/{folder}/{i}"):
            retrn += f"<a href='/SuperSimpleFunctions/rename/interface/{folder.replace('/', '|')}|{i}?passw={password}'>"
            retrn += "<h2 style='color: white'>"
            retrn += f"{i}</h2>\n"
            retrn += "</a>"
    return retrn
def getFilesButEncrypt(folder = "files"):
    files = os.listdir("./static/"+folder)
    retrn = ""
    for i in files:
        if os.path.isfile(f"./static/{folder}/{i}"):
            retrn += f"<a href='/SuperSimpleFunctions/AES/encrypt_interface/{folder.replace('/', '|')}|{i}?passw={password}'>"
            retrn += "<h2 style='color: green'>"
            retrn += f"{i}</h2>\n"
            retrn += "</a>"
    return retrn

def renameFile(path, path2):
    os.rename(path, path2)

@app.route("/", methods=["GET", "POST"])
def auth():
    if not os.path.exists("first"):
        f = open('password.html')
        r = f.read()
        f.close()
        return r
    else:
        f = open("first-setup.html")
        r = f.read()
        f.close()
        return r
@app.route("/first-setup")
def first():
    if os.path.exists("first"):
        autor = request.args["recovery"] == "on"
        autob = request.args["backup"] == "on"
        rpath = request.args["recoveryl"]
        bpath = request.args["backupl"]
        passwor = request.args["passw"]
        nysm = request.args["nysm"]
        ar = 0
        ab = 0
        if autor == True:
            ar = "1"
        if autob == True:
            ab = "1"
        f = open("setup.txt", 'w')
        f.write(f"""reedsolo: {nysm}
autorecover: {ar}
autobackup: {ab}
backuplocation: {bpath}
recoverlocation: {rpath}""")
        f.close()
        f = open("PASSWORD", 'w')
        f.write(passwor)
        f.close()
        os.remove("first")
        loadConfig()
        return redirect("/")
    else:
        return "No no no you have already done the first setup silly!"
@app.route("/settingup")
def settingup():
    if password == request.args["passw"]:
        if len(request.args) > 1:
            try:
                autor = request.args["recovery"]
                ar = "1"
            except:
                ar = "0"
            try:
                autob = request.args["backup"] == "on"
                ab = "1"
            except:
                ab = "0"
            rpath = request.args["recoveryl"]
            bpath = request.args["backupl"]
            passwor = request.args["npassw"]
            nysm = request.args["nysm"]
            f = open("setup.txt", 'w')
            f.write(f"""reedsolo: {nysm}
autorecover: {ar}
autobackup: {ab}
backuplocation: {bpath}
recoverlocation: {rpath}""")
            f.close()
            f = open("PASSWORD", 'w')
            f.write(passwor)
            f.close()
            loadConfig()
            return redirect("/")
        else:
            f = open("settings.html")
            r = f.read()
            f.close()
            return r
    else:
        return "Wrong password maybe?"

@app.route("/SuperSimpleFunctions/upload/<path>")
def upload(path : str):
    return """
<!DOCTYPE html>
<head>
<meta charset="UTF-8">
<style>
.progress-wrapper {
    width:100%;
}
.progress-wrapper .progress {
    background-color:lime;
    width:0%;
    padding:5px 0px 5px 0px;
}
input, button{
	font-size: 45px;
}
button{
    background-color: lightblue;
    border-radius: 25px;
}
</style>
<script>
function postFile() {
    var formdata = new FormData();

    formdata.append('file', document.getElementById('file1').files[0]);

    var request = new XMLHttpRequest();

    request.upload.addEventListener('progress', function (e) {
        var file1Size = document.getElementById('file1').files[0].size;
        console.log(file1Size);

        if (e.loaded <= file1Size) {
            var percent = Math.round(e.loaded / file1Size * 100);
            document.getElementById('progress-bar-file1').style.width = percent + '%';
            document.getElementById('progress-bar-file1').innerHTML = percent + '%';
        } 

        if(e.loaded == e.total){
            document.getElementById('progress-bar-file1').style.width = '100%';
            document.getElementById('progress-bar-file1').innerHTML = 'Yay uploaded!';
        }
    });   

    request.open('post', '/"""+path+"?passw="+password+"""');
    request.timeout = 45000;
    request.send(formdata);
}
</script>
</head>
<div style='border-width: 5px;border-style: solid;border-radius: 30px;background: cornflowerblue;height: 352px;width: 550px;'>
<br>
<form id="form1">
    <input id="file1" type="file" />
    <div class="progress-wrapper">
        <div id="progress-bar-file1" class="progress"></div>
    </div>
    <br>
    <button type="button" onclick="postFile()">Upload File</button>
</form>
<br><br><br><br><br><br>
<a href='/'><button>Go back to root</button></div>
</html>
"""
@app.route("/<folder>", methods = ["GET", "POST"])
def navigate(folder : str):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        magic_variable = ""
        if configs["backuplocation"][0] != "." or configs["recoverlocation"][0] != ".":
            magic_variable = f"<a href='/SuperSimpleFunctions/DBnR?passw={password}'><button>View backups and/or recovery files</button></a>"
        return f"{sample}<div class='mmmm'><h1>{path.removeprefix('files')}</h1>"+getFiles(path)+f"<a href='/SuperSimpleFunctions/upload/{folder}?passw={password}'><button>Upload here</button></a><a href='/SuperSimpleFunctions/delete/{path.replace('/', '|')}?passw={password}'><button>Delete here</button></a><a href='/SuperSimpleFunctions/setuprecovery/{path.removesuffix('/').replace('/', '|')}?passw={password}'><button>Set up recovery here</button></a><a href='/SuperSimpleFunctions/backup/{path.removesuffix('/').replace('/', '|')}?passw={password}'><button>Make a backup here</button></a><a href='/SuperSimpleFunctions/rename/{path.removesuffix('/').replace('/', '|')}?passw={password}'><button>Rename here</button></a><a href='/SuperSimpleFunctions/mkdir/{path.removesuffix('/').replace('/', '|')}?passw={password}'><button>New folder here</button></a><a href='/SuperSimpleFunctions/AES/interface/{path.removesuffix('/').replace('/', '|')}?passw={password}'><button>Encrypt here</button></a>{magic_variable}<a href=/settingup?passw={password}><button class='material-symbols-outlined' style='font-size: 30px'>settings</button></a></div>"
    if request.method == 'POST':
        if 'file' not in request.files:
            return "File not sent!"
        file = request.files['file']
        if file.filename == '':
            return "No file selected!"
        if file and request.args["passw"] == password:
            filename = file.filename
            file.save(f"./static/files{path.removeprefix('files')}"+str(filename))
            if(configs["autobackup"][0] == "1"):
                backupFile(f"./static/files{path.removeprefix('files')}"+str(filename))
            if(configs["autorecover"][0] == "1"):
                setupRecoveryFile(f"./static/files{path.removeprefix('files')}"+str(filename))
            return "Yay file uploaded!"
    return "Wrong password i think"

@app.route("/SuperSimpleFunctions/delete/butfr/<path>")
def deletebutfr(path : str):
    if request.args["passw"] == password:
        if os.path.isfile("./static/"+path.replace('|', '/')):
            os.remove("./static/"+path.replace('|', '/'))
        else:
            os.rmdir("./static/"+path.replace('|', '/'))
        return "File succesfully eliminated.<a href='/'><button>Go back to root</button></a>"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/delete/<path>")
def delete(path : str):
    if request.args["passw"] == password:
        path = path.replace('|', '/').removesuffix('/')
        return f"{sample}<div class='mmmm' width=500><h1>What file to delete from {'/'+path.removeprefix('files').removeprefix('/')}?</h1>{getFilesButDelete(path)}</div>"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/setuprecovery/<folder>", methods = ["GET"])
def setupRecovery(folder : str):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        return f"{sample}<div class='mmmm' width=500><h1>What file to setup recovery for from {'/'+path.removeprefix('files').removeprefix('/')}?</h1>{getFilesButSetupRecovery(path)}</div>"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/setuprecovery/butfr/<folder>", methods = ["GET"])
def recoveryfr(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        setupRecoveryFile("./static/"+path)
        return "Done👍"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/recovery/<folder>", methods = ["GET"])
def recovery(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        results = recoverFile("./static/"+path)
        return f"I tried to recover your file! Chunks recovered: {int(results[0])} Broken chunks: {int(results[1])}"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/backup/<folder>", methods = ["GET"])
def backup(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        return f"{sample}<div class='mmmm' width=500><h1>What file to backup from {'/'+path.removeprefix('files').removeprefix('/')}?</h1>{getFilesButSetupBackup(path)}</div>"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/backup/butfr/<folder>", methods = ["GET"])
def backupfr(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        backupFile("./static/"+path)
        return "Backup successful👍"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/downloadbackup/<folder>", methods = ["GET"])
def downbackup(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    i = path.split("/")[len(path.split("/"))-1]
    if request.method == "GET" and request.args["passw"] == password:
        if len(i.split(".")[:len(i.split("."))-2]) < 2:
            return send_file("./static/"+path, download_name=i.split(".")[:len(i.split("."))-2][0], as_attachment=True)
        else:
            return send_file("./static/"+path, download_name=i.split(".")[:len(i.split("."))-2][0]+"."+i.split(".")[:len(i.split("."))-2][1], as_attachment=True)
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/rename/<folder>", methods = ["GET"])
def renam(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        return f"{sample}<div class='mmmm' width=500><h1>What file to rename from {'/'+path.removeprefix('files').removeprefix('/')}?</h1>{getFilesButRename(path)}</div>"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/rename/interface/<folder>", methods = ["GET"])
def renamee(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    i = path.split("/")[len(path.split("/"))-1]
    if request.method == "GET" and request.args["passw"] == password:
        return """<!DOCTYPE html>
<html><head>
<style>
    input, label{
        font-size: 30px;
        font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
    }
    .psswd{
        border-width: 5px;
        border-style: solid;
        border-radius: 30px;
        width: 450px;
        background-color: cornflowerblue;
    }
</style>
</head>
<body>
<div class="psswd">
    <br>
<form action="/SuperSimpleFunctions/rename/fr/"""+folder+"""?passw=password">
  <label for="passw">New file name:</label><br>
  <input type="text" id="name" name="name" value=""><br><br>
  <label for="passw">Password to the cloud:</label><br>
  <input type="password" id="passw" name="passw" value=""><br><br>
  <input type="submit" value="Ok">
</form><br></div>
</body>
</html>"""
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/rename/fr/<folder>", methods = ["GET"])
def renamefr(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = "./static/"+path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        newpath = ""
        for j in path.split("/")[:len(path.split("/"))-1]:
            newpath += j + "/"
        renameFile(path, newpath+request.args["name"])
        return "Renamed👍"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/mkdir/<folder>", methods = ["GET"])
def mkdir(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        return """<!DOCTYPE html>
<html><head>
<style>
    input, label{
        font-size: 30px;
        font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
    }
    .psswd{
        border-width: 5px;
        border-style: solid;
        border-radius: 30px;
        width: 450px;
        background-color: cornflowerblue;
    }
</style>
</head>
<body>
<div class="psswd">
    <br>
<form action="/SuperSimpleFunctions/mkdir/fr/"""+folder+"""">
  <label for="passw">Folder name:</label><br>
  <input type="text" id="name" name="name" value=""><br><br>
  <label for="passw">Password to the cloud:</label><br>
  <input type="password" id="passw" name="passw" value=""><br><br>
  <input type="submit" value="Ok">
</form><br></div>
</body>
</html>"""
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/mkdir/fr/<folder>", methods = ["GET"])
def mkdirfr(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        os.mkdir("./static/"+path+"/"+request.args["name"])
        return "New folder created👍"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/AES/interface/<folder>", methods = ["GET"])
def aesinterface(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        return f"{sample}<div class='mmmm' width=500><h1>What file to encrypt from {'/'+path.removeprefix('files').removeprefix('/')}?</h1>{getFilesButEncrypt(path)}</div>"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/AES/encrypt_interface/<folder>", methods = ["GET"])
def aesencrypt(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        return """<!DOCTYPE html>
<html><head>
<style>
    input, label{
        font-size: 30px;
        font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
    }
    .psswd{
        border-width: 5px;
        border-style: solid;
        border-radius: 30px;
        width: 450px;
        background-color: cornflowerblue;
    }
</style>
</head>
<body>
<div class="psswd">
    <br>
<form action="/SuperSimpleFunctions/AES/encrypt/"""+folder+"""">
  <label for="passw">Encryption password:</label><br>
  <input type="password" id="key" name="key" value="" maxlength="16"><br><br>
  <label for="passw">Password to the cloud:</label><br>
  <input type="password" id="passw" name="passw" value=""><br><br>
  <input type="submit" value="Ok">
</form><br></div>
</body>
</html>"""
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/AES/encrypt/<folder>", methods = ["GET"])
def aesencrypty(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        fileAESEncrypt("./static/"+path, request.args["key"])
        return "File encrypted👍"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/AES/decrypt_interface/<folder>", methods = ["GET"])
def aesdecrypt(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        return """<!DOCTYPE html>
<html><head>
<style>
    input, label{
        font-size: 30px;
        font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
    }
    .psswd{
        border-width: 5px;
        border-style: solid;
        border-radius: 30px;
        width: 450px;
        background-color: cornflowerblue;
    }
</style>
</head>
<body>
<div class="psswd">
    <br>
<form action="/SuperSimpleFunctions/AES/decrypt/"""+folder+"""">
  <label for="passw">Encryption password:</label><br>
  <input type="password" id="key" name="key" value="" maxlength="16"><br><br>
  <label for="passw">Password to the cloud:</label><br>
  <input type="password" id="passw" name="passw" value=""><br><br>
  <input type="submit" value="Ok">
</form><br></div>
</body>
</html>"""
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/AES/decrypt/<folder>", methods = ["GET"])
def aesdecrypty(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix('/')
    if request.method == "GET" and request.args["passw"] == password:
        return fileAESDecrypt("./static/"+path, request.args["key"])
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/DBnR", methods = ["GET"])
def dbnr():
    global configs
    if request.method == "GET" and request.args["passw"] == password:
        if configs["backuplocation"] != "." or configs["recoverlocation"] != ".":
            return f"{sample}<div class='mmmm' width=500><h1>Which one?</h1><a href='/SuperSimpleFunctions/DBnR/b?passw={password}'><button>Backups</button></a><br><a href='/SuperSimpleFunctions/DBnR/r?passw={password}'><button>Recovery</button></a></div>"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/DBnR/b", methods = ["GET"])
def dbnrb():
    global configs
    if request.method == "GET" and request.args["passw"] == password:
        if configs["backuplocation"][0] != ".":
            return f"{sample}<div class='mmmm' width=500><h1>Backups</h1>{getFilesButDBnR(configs['backuplocation'][0])}</div>"
        else:
            return redirect(f"/SuperSimpleFunctions/DBnR?passw={password}")
    else:
        return "Wrong password i think"
@app.route("/SuperSimpleFunctions/DBnR/r", methods = ["GET"])
def dbnrr():
    global configs
    if request.method == "GET" and request.args["passw"] == password:
        if configs["recoverlocation"][0] != ".":
            return f"{sample}<div class='mmmm' width=500><h1>Backups</h1>{getFilesButDBnR(configs['recoverlocation'][0])}</div>"
        else:
            return redirect(f"/SuperSimpleFunctions/DBnR?passw={password}")
    else:
        return "Wrong password i think"
@app.route("/SuperSimpleFunctions/DBnR/backup/<folder>", methods = ["GET"])
def dbnrbackups(folder):
    global configs
    if request.method == "GET" and request.args["passw"] == password:
        if configs["backuplocation"][0] != ".":
            x = open("DBnR")
            r = x.read().removeprefix("\n").removesuffix("\n").split("\n")
            x.close()
            register = {}
            for item in r:
                register[item.split(" -> ")[0]] = item.split(" -> ")[1]
            name = list(register.keys())[list(register.values()).index(configs["backuplocation"][0]+"/"+folder)]
            return send_file(configs["backuplocation"][0]+"/"+folder, as_attachment=True, download_name=name.split("/")[len(name.split("/"))-1])
        else:
            return redirect(f"/SuperSimpleFunctions/DBnR?passw={password}")
    else:
        return "Wrong password i think"
@app.route("/SuperSimpleFunctions/DBnR/recovery/<folder>", methods = ["GET"])
def dbnrrecovery(folder):
    global configs
    if request.method == "GET" and request.args["passw"] == password:
        if configs["backuplocation"][0] != ".":
            x = open("DBnR")
            r = x.read().removeprefix("\n").removesuffix("\n").split("\n")
            x.close()
            register = {}
            for item in r:
                register[item.split(" -> ")[0]] = item.split(" -> ")[1]
            ok, notok = recoverFile(configs["recoverlocation"][0]+"/"+folder)
            return f"File recovered! Ok chunks: {ok}, Broken chunks {notok}."
        else:
            return redirect(f"/SuperSimpleFunctions/DBnR?passw={password}")
    else:
        return "Wrong password i think"
app.run("0.0.0.0", 12345, debug=True)