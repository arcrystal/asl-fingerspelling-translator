from flask import Flask, render_template, Response
from translator import Translator

app = Flask(__name__)
translator = Translator()

@app.route('/')
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/aboutus")
def about_us():
    return render_template('about_us.html')

@app.route("/ourwork")
def our_work():
    return render_template('our_work.html')

@app.route("/translate")
def translate():
    return Response(translator.translate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
