from flask import Flask, request
import os, reedsolo

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
        f.write("reedsolo: 20,.")
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

def setupRecoveryFile(file):
    global configs
    rcs = reedsolo.RSCodec(int(configs["reedsolo"][0]))
    x = open(file, "rb")
    y = x.read()
    x.close()
    z = open(file+".reso", 'wb')
    z.write(rcs.encode(y)[len(y):])
    z.close()
def recoverFile(file):
    global configs
    rcs = reedsolo.RSCodec(100)
    x = open(file, "rb")
    z = open(file+".reso", 'rb')
    y = z.read()
    recovery = rcs.decode(x.read()+y)[0]
    x.close()
    x = open(file, "wb")
    x.write(recovery)

def getFiles( folder = "files"):
    global password
    files = os.listdir("./static/"+folder)
    retrn = ""
    for i in files:
        if os.path.isfile(f"./static/{folder}/{i}"):
            if i.split('.')[len(i.split("."))-1] != "reso":
                retrn += f"<a href='/static/{folder}/{i}?passw={password}' download>"
            else:
                retrn += f"<a href='/SuperSimpleFunctions/recovery/{folder.replace("/", "|")}{i.replace(".reso", '')}?passw={password}'>"
            retrn += "<h2 style='color: white'>"
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
        return f"{sample}<div class='mmmm'><h1>{path.removeprefix("files")}</h1>"+getFiles(path)+f"<a href='/SuperSimpleFunctions/upload/{folder}?passw={password}'><button>Upload here</button></a><a href='/SuperSimpleFunctions/delete/{path.replace("/", "|")}?passw={password}'><button>Delete here</button></a><a href='/SuperSimpleFunctions/setuprecovery/{path.removesuffix("/").replace("/", "|")}?passw={password}'><button>Set up recovery here</button></a></div>"
    if request.method == 'POST':
        if 'file' not in request.files:
            return "File not sent!"
        file = request.files['file']
        if file.filename == '':
            return "No file selected!"
        if file and request.args["passw"] == password:
            filename = file.filename
            file.save(f"./static/files{path.removeprefix("files")}"+str(filename))
            return "Yay file uploaded!"
    return "Wrong password i think"

@app.route("/SuperSimpleFunctions/delete/butfr/<path>")
def deletebutfr(path : str):
    if request.args["passw"] == password:
        os.remove("./static/"+path.replace("|", "/"))
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
        recoverFile("./static/"+path)
        return "Hope your file's fine! File recovered!"
    return "...nothing... File not recovered... sadly. Please check server logs for more details!"


app.run("0.0.0.0", 12345, debug=True)