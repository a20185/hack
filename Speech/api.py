import speech_recognition as sr
from flask import Flask, request

app = Flask(__name__)


def speech2text(filePath, lang="zh-cn", api="bing"):
    r = sr.Recognizer()
    with sr.AudioFile(filePath) as source:
        audio = r.record(source)

    BING_KEY = "fc6d59b192804002bd0396ba65a778c3"
    try:
        if api == "bing":
            rsp = r.recognize_bing(audio, key=BING_KEY, language=lang)
        elif api == "google":
            rsp = r.recognize_google(audio, language=lang)
        return rsp
    except sr.UnknownValueError:
        print(("Error: Microsoft Bing Voice Recognition could not"
               "understand audio"))
    except sr.RequestError as e:
        print("Error: Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))


@app.route('/')
def index():
    return 'Hello world'


@app.route('/speech', methods=['POST'])
def resolve():
    if 'file' not in request.files:
        return 'None'
    else:
        f = request.files['file']
        f.save('audio.mp3')
        text = speech2text('audio.mp3', lang='zh-cn', api='google')
        return text


if __name__ == "__main__":
    # print(speech2text("1.mp3", api="google"))
    # print(speech2text("1.mp3", api="bing"))
    app.run(host='0.0.0.0', port=8000, debug=True)
