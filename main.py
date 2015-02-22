import os, shutil
import tempfile, urllib.request, json
from flask import Flask, render_template, session

application = app = Flask(__name__)
# change this, of course!
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.debug = True


def newtempdir():
    if 'tempdir' in session:
        try:
            shutil.rmtree(tempdir())
        except:
            pass
    session['tempdir'] = tempfile.mkdtemp()

def tempdir():
    return session['tempdir']

@app.route('/')
def root():
  return render_template('index.html')

@app.route('/<filename>')
def file(filename):
    with open(os.path.join(tempdir(),filename)) as f:
        return f.read()


# Note to self:
# Modifiy these handlers to cache the *method* of use: cloud9 or github
# Then only handle retrieval of the *main* file, rendering index.html
# Then subsequent calls to the /<filename> route will automatically
# Retrieve directly from github or cloud9
@app.route('/cloud9/<user>/<project>')
@app.route('/cloud9/<user>/<project>/<path>')
def gocloud9(user, project, path=""):
    newtempdir()
    url = "https://{0}-{1}.c9.io/{2}".format(project, user, path)
    urllib.request.urlcleanup()
    

@app.route('/github/<user>/<repo>')
@app.route('/github/<user>/<repo>/<path>')
def gogithub(user, repo, path=""):
    mainfile = ""
    newtempdir()
    url = "https://api.github.com/repos/{0}/{1}/contents/{2}".format(user, repo, path)
    token = os.environ['githubtoken']
    urllib.request.urlcleanup()
    request = urllib.request.Request(url)
    request.add_header('Authorization', 'token {0}'.format(token))
    response = urllib.request.urlopen(request)
    #print(response.getheaders())
    jsresponse = json.loads(response.read().decode("utf-8"))
    for f in jsresponse:
        if f['type'] == 'file':
            name = f['name']
            if mainfile == "" and len(name) > 3 and name[-3:] == '.py':
                mainfile = name
            if name in ["main.py", "__main__.py"]:
                mainfile = name
            fileurl = f['download_url']
            request = urllib.request.Request(fileurl)
            request.add_header('Authorization', 'token {0}'.format(token))
            rfile = urllib.request.urlopen(request)
            with open(os.path.join(tempdir(), name), 'w') as f:
                f.write(rfile.read().decode("utf-8"))
    return render_template('index.html', main=mainfile)

if __name__ == "__main__":
    app.run(host=os.environ['IP'],port=int(os.environ['PORT']))
