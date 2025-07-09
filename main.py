from flask import Flask, flash, request, redirect, url_for
import os

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = "./static/files/"

if __name__ == "__main__":
    if not os.path.exists("./static"):
        os.mkdir("static")
        os.mkdir("static/files")

f = open("sample.html")
sample = f.read()
f.close()

def getFiles(folder = "files"):
    files = os.listdir("./static/"+folder)
    retrn = ""
    for i in files:
        if os.path.isfile(f"./static/{folder}/{i}"):
            retrn += f"<a href='/static/{folder}/{i}' download>"
            retrn += "<h2 style='color: white'>"
        else:
            retrn += f"<a href='/{folder}|{i}'>"
            retrn += "<h2 style='color: orange'>"
        retrn += f"{i}</h2>\n"
        retrn += "</a>"
    return retrn

def getFilesButDelete(folder = "files"):
    files = os.listdir("./static/"+folder)
    retrn = ""
    for i in files:
        retrn += f"<a href='/delete/butfr/{folder.replace("/", "|")}|{i}'>"
        retrn += "<h2 style='color: red'>"
        retrn += f"{i}</h2>\n"
        retrn += "</a>"
    return retrn

@app.route("/", methods=["GET", "POST"])
def online():
    return f"{sample}<h1>Your cloud is online! This is root: /</h1>" + getFiles() + "<a href='/SuperSimpleFunctions/upload/files'><button>Upload here</button></a><a href='/delete/files'><button>Delete here</button></a>"
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

    request.open('post', '/"""+path+"""');
    request.timeout = 45000;
    request.send(formdata);
}
</script>
</head>
<form id="form1">
    <input id="file1" type="file" />
    <div class="progress-wrapper">
        <div id="progress-bar-file1" class="progress"></div>
    </div>
    <button type="button" onclick="postFile()">Upload File</button>
</form>
<a href='/'><button>Go back to root</button>
</html>
"""
@app.route("/<folder>", methods = ["GET", "POST"])
def navigate(folder : str):
    path = ""
    for i in folder.split("|"):
        path += i + "/"
    path.removesuffix("/")
    if request.method == "GET":
        return f"{sample}<h1>{path.removeprefix("files")}</h1>"+getFiles(path)+f"<a href='/delete/{path.replace("/", "|")}'><a href='/SuperSimpleFunctions/upload/{folder}'><button>Upload here</button></a><a href='/delete/{path.replace("/", "|")}'><button>Delete here</button></a>"
    else: # request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return "File not sent!"
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return "No file selected!"
        if file:
            filename = file.filename
            file.save(f"./static/files{path.removeprefix("files")}"+str(filename))
            return "Yay file uploaded!"
    return "idk? go ask the dev or smth..."

@app.route("/delete/butfr/<path>")
def deletebutfr(path : str):
    os.remove("./static/"+path.replace("|", "/"))
    return "File succesfully eliminated.<a href='/'><button>Go back to root</button></a>"
@app.route("/delete/<path>")
def delete(path : str):
    path = path.replace("|", "/").removesuffix("/")
    return f"{sample}<h1>What file to delete from {"/"+path.removeprefix("files").removeprefix("/")}?</h1>{getFilesButDelete(path)}"


app.run("0.0.0.0", 12345, debug=True)