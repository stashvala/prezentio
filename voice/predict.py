import numpy as np
import pickle

from sklearn.linear_model import LogisticRegression
import os.path
import pyautogui as pag


class Predicition:
    def __init__(self):
        if os.path.exists("model.pickle"):
            with open("model.pickle", 'rb') as pickle_file:
                self.data = pickle.load(pickle_file)
                for key, value in self.data.items():
                    self.data[key] = [x for x in value if len(x) > 3]
                print(self.data)
        else:
            self.data = {}

        self.all_columns = [item for sublist in self.data.values() for item in sublist]
        self.model = None
        self.current_slide = 0

    def set_model(self):
        if self.current_slide + 1 == len(self.data):
            print('end')
            return

        x_result = []
        y_result = []

        # use only current and next slide for classification
        x_result.append([True if x in self.data[self.current_slide] else False for x in self.get_current_columns()])
        x_result.append([True if x in self.data[self.current_slide + 1] else False for x in self.get_current_columns()])
        y_result.append(self.current_slide)
        y_result.append(self.current_slide + 1)

        self.model = LogisticRegression()
        self.model.fit(np.array(x_result), y_result)

    def update_data(self, new_words):
        if self.current_slide in self.data:
            self.data[self.current_slide] += new_words
        else:
            self.data[self.current_slide] = new_words

        with open("model.pickle", 'wb') as pickle_file:
            pickle.dump(self.data, pickle_file)

        self.current_slide += 1

    def predict(self, x_values):
        if self.model is None:
            raise Exception("First set the model!")
        value = self.model.predict_proba([True if x in x_values else False for x in self.get_current_columns()])
        print(value)
        if value[0][1] > 0.59:
            self.current_slide += 1
            if self.current_slide == len(self.data):
                print('finished')
                return
            self.set_model()
            print("Transition from ", self.current_slide - 1, " to", self.current_slide)
            pag.press('right')

    def get_current_columns(self):
        return self.data[self.current_slide] + self.data[self.current_slide + 1]
