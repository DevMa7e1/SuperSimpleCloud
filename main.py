from flask import Flask, request, send_file
import os, reedsolo, time

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
autobackup: 0""")
        f.close()



f = open("sample.html")
sample = f.read()
f.close()

f = open("PASSWORD")
password = f.read()
f.close()

f = open("setup.txt")
cffg = f.read().replace(" ", "")
f.close()
configs = {}
for i in cffg.split("\n"):
    configs[i.split(":")[0]] = i.split(":")[1].split(",")

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
    for i in range(len(reeds)):
        print(f"Decoding chunk {i}.", end="\r")
        try:
            corrects.append(rcs.decode(chunks[i]+reeds[i]))
            recovered += 1
        except Exception as e:
            broken += 1
    correct = b""
    for i in corrects:
        correct += i[0]
    print()
    return correct, recovered, broken

def backupFile(file):
    a = open(file, 'rb')
    b = open(file+f".{str(round(time.time()))}.back", 'wb')
    b.write(a.read())
    a.close()
    b.close()

def setupRecoveryFile(file):
    global configs
    z = open(file+".reso", 'wb')
    bstr = b""
    for i in ReedEncode(readChunks(file)):
        bstr += i
    z.write(bstr)
    z.close()
def recoverFile(file):
    global configs
    vars = ReedDecode(readChunks(file+".reso", int(configs["reedsolo"][0])), readChunks(file))
    recovery = vars[0]
    if recovery != "":
        x = open(file, "wb")
        x.write(recovery)
        x.close()
    return vars[1], vars[2]

def getFiles( folder = "files"):
    global password
    files = os.listdir("./static/"+folder)
    retrn = ""
    for i in files:
        if os.path.isfile(f"./static/{folder}/{i}"):
            if i.split('.')[len(i.split("."))-1] != "reso" and i.split('.')[len(i.split("."))-1] != "back":
                retrn += f"<a href='/static/{folder}/{i}?passw={password}' download>"
                retrn += "<h2 style='color: white'>"
            elif i.split('.')[len(i.split("."))-1] == "reso":
                retrn += f"<a href='/SuperSimpleFunctions/recovery/{folder.replace("/", "|")}{i.replace(".reso", '')}?passw={password}'>"
                retrn += "<h2 style='color: lightblue'>"
            elif i.split('.')[len(i.split("."))-1] == "back":
                retrn += f"<a href='/SuperSimpleFunctions/downloadbackup/{folder.replace("/", "|")}{i.replace("/", "|")}?passw={password}' download>"
                retrn += "<h2 style='color: lightgray'>"
        else:
            retrn += f"<a href='/{folder.replace("/", "|")}{i}?passw={password}'>"
            retrn += "<h2 style='color: orange'>"
        retrn += f"{i}</h2>\n"
        retrn += "</a>"
    return retrn

def getFilesButDelete(folder = "files"):
    files = os.listdir("./static/"+folder)
    retrn = ""
    for i in files:
        retrn += f"<a href='/SuperSimpleFunctions/delete/butfr/{folder.replace("/", "|")}|{i}?passw={password}'>"
        retrn += "<h2 style='color: red'>"
        retrn += f"{i}</h2>\n"
        retrn += "</a>"
    return retrn
def getFilesButSetupRecovery(folder = "files"):
    files = os.listdir("./static/"+folder)
    retrn = ""
    for i in files:
        if os.path.isfile(f"./static/{folder}/{i}"):
            retrn += f"<a href='/SuperSimpleFunctions/setuprecovery/butfr/{folder.replace("/", "|")}|{i}?passw={password}'>"
            retrn += "<h2 style='color: lightblue'>"
            retrn += f"{i}</h2>\n"
            retrn += "</a>"
    return retrn
def getFilesButSetupBackup(folder = "files"):
    files = os.listdir("./static/"+folder)
    retrn = ""
    for i in files:
        if os.path.isfile(f"./static/{folder}/{i}"):
            retrn += f"<a href='/SuperSimpleFunctions/backup/butfr/{folder.replace("/", "|")}|{i}?passw={password}'>"
            retrn += "<h2 style='color: yellow'>"
            retrn += f"{i}</h2>\n"
            retrn += "</a>"
    return retrn
def getFilesButRename(folder = "files"):
    files = os.listdir("./static/"+folder)
    retrn = ""
    for i in files:
        if os.path.isfile(f"./static/{folder}/{i}"):
            retrn += f"<a href='/SuperSimpleFunctions/rename/interface/{folder.replace("/", "|")}|{i}?passw={password}'>"
            retrn += "<h2 style='color: white'>"
            retrn += f"{i}</h2>\n"
            retrn += "</a>"
    return retrn

def renameFile(path, path2):
    os.rename(path, path2)

@app.route("/", methods=["GET", "POST"])
def auth():
    f = open('password.html')
    r = f.read()
    f.close()
    return r
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
    path.removesuffix("/")
    if request.method == "GET" and request.args["passw"] == password:
        return f"{sample}<div class='mmmm'><h1>{path.removeprefix("files")}</h1>"+getFiles(path)+f"<a href='/SuperSimpleFunctions/upload/{folder}?passw={password}'><button>Upload here</button></a><a href='/SuperSimpleFunctions/delete/{path.replace("/", "|")}?passw={password}'><button>Delete here</button></a><a href='/SuperSimpleFunctions/setuprecovery/{path.removesuffix("/").replace("/", "|")}?passw={password}'><button>Set up recovery here</button></a><a href='/SuperSimpleFunctions/backup/{path.removesuffix("/").replace("/", "|")}?passw={password}'><button>Make a backup here</button></a><a href='/SuperSimpleFunctions/rename/{path.removesuffix("/").replace("/", "|")}?passw={password}'><button>Rename here</button></a><a href='/SuperSimpleFunctions/mkdir/{path.removesuffix("/").replace("/", "|")}?passw={password}'><button>New folder here</button></a></div>"
    if request.method == 'POST':
        if 'file' not in request.files:
            return "File not sent!"
        file = request.files['file']
        if file.filename == '':
            return "No file selected!"
        if file and request.args["passw"] == password:
            filename = file.filename
            file.save(f"./static/files{path.removeprefix("files")}"+str(filename))
            if(configs["autobackup"][0] == "1"):
                backupFile(f"./static/files{path.removeprefix("files")}"+str(filename))
            if(configs["autorecover"][0] == "1"):
                setupRecoveryFile(f"./static/files{path.removeprefix("files")}"+str(filename))
            return "Yay file uploaded!"
    return "Wrong password i think"

@app.route("/SuperSimpleFunctions/delete/butfr/<path>")
def deletebutfr(path : str):
    if request.args["passw"] == password:
        if os.path.isfile("./static/"+path.replace("|", "/")):
            os.remove("./static/"+path.replace("|", "/"))
        else:
            os.rmdir("./static/"+path.replace("|", "/"))
        return "File succesfully eliminated.<a href='/'><button>Go back to root</button></a>"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/delete/<path>")
def delete(path : str):
    if request.args["passw"] == password:
        path = path.replace("|", "/").removesuffix("/")
        return f"{sample}<h1>What file to delete from {"/"+path.removeprefix("files").removeprefix("/")}?</h1>{getFilesButDelete(path)}"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/setuprecovery/<folder>", methods = ["GET"])
def setupRecovery(folder : str):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix("/")
    if request.method == "GET" and request.args["passw"] == password:
        return f"{sample}<div class='mmmm' width=500><h1>{path.removeprefix("files")}</h1>"+getFilesButSetupRecovery(path)+"</div>"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/setuprecovery/butfr/<folder>", methods = ["GET"])
def recoveryfr(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix("/")
    if request.method == "GET" and request.args["passw"] == password:
        setupRecoveryFile("./static/"+path)
        return "Done👍"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/recovery/<folder>", methods = ["GET"])
def recovery(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix("/")
    if request.method == "GET" and request.args["passw"] == password:
        results = recoverFile("./static/"+path)
        return f"I tried to recover your file! Chunks recovered: {int(results[0])} Broken chunks: {int(results[1])}"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/backup/<folder>", methods = ["GET"])
def backup(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix("/")
    if request.method == "GET" and request.args["passw"] == password:
        return sample+"<div class='mmmm' width=500><h1>"+getFilesButSetupBackup(path)+"</div>"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/backup/butfr/<folder>", methods = ["GET"])
def backupfr(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix("/")
    if request.method == "GET" and request.args["passw"] == password:
        backupFile("./static/"+path)
        return "Backup successful👍"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/downloadbackup/<folder>", methods = ["GET"])
def downbackup(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix("/")
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
    path = path.removesuffix("/")
    if request.method == "GET" and request.args["passw"] == password:
        return sample+"<div class='mmmm' width=500><h1>"+getFilesButRename(path)+"</div>"
    return "Wrong password i think"
@app.route("/SuperSimpleFunctions/rename/interface/<folder>", methods = ["GET"])
def renamee(folder):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path = path.removesuffix("/")
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
    path = "./static/"+path.removesuffix("/")
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
    path = path.removesuffix("/")
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
    path = path.removesuffix("/")
    if request.method == "GET" and request.args["passw"] == password:
        os.mkdir("./static/"+path+"/"+request.args["name"])
        return "New folder created👍"
    return "Wrong password i think"
app.run("0.0.0.0", 12345, debug=True)