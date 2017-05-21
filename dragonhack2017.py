import speech_recognition as sr
import json
import time

import predict

TRAINING = False

prediction = predict.Predicition()

data = None
with open('Dragonhack2017-6b5e3dc8f13c.json') as data_file:
    data = json.load(data_file)

r = sr.Recognizer()
r.pause_threshold = 0.1
r.phrase_threshold = 3
r.non_speaking_duration = 0.1

m = sr.Microphone(sample_rate=16000)

with m as source:
    r.adjust_for_ambient_noise(source, duration=10)
print("Set minimum energy threshold to {}".format(r.energy_threshold))


def predict_callback(recognizer, audio):
    try:
        print('recognizing')
        value = r.recognize_google_cloud(audio, credentials_json=json.dumps(data),
                                         preferred_phrases=prediction.get_current_columns())
        print(value)
        ans = []
        split = value.split(" ")
        for word in split:
            strip = word.strip()
            if len(strip) > 3:
                ans.append(strip)
        prediction.predict(ans)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from recognition service; {0}".format(e))


def train_callback(recognizer, audio):
    global new_words
    try:
        print('recognizing')
        value = r.recognize_google_cloud(audio, credentials_json=json.dumps(data),
                                         preferred_phrases=prediction.get_current_columns())
        print(value)
        split = value.split(" ")
        for word in split:
            strip = word.strip()
            if len(strip) > 3:
                new_words.append(strip)
    except sr.UnknownValueError:
        print("Could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from recognition service; {0}".format(e))


if TRAINING:
    new_words = []
else:
    prediction.set_model()

r.listen_in_background(m, train_callback if TRAINING else predict_callback)

while True:
    if TRAINING:
        input("Press any key to go to next slide")
        prediction.update_data(new_words)
        new_words = []
    else:
        time.sleep(0.01)
