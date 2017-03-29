from sklearn import svm
from sklearn import cross_validation
from sklearn.externals import joblib
from PIL import Image
import os
import numpy as np


class ImgRecognizer:
    def __init__(self):
        self.training_data = []
        self.target_values = []
        self.svc = svm.SVC(gamma=0.001, kernel='linear', C=100)
        self.downscale_res = (32, 32)

    def _load(self, path, target_value):
        training_imgs = os.listdir(path)
        for f in training_imgs:
            img = Image.open(path+'/'+f)
            img = img.resize(self.downscale_res, Image.BILINEAR)
            self.training_data.append(np.array(img.getdata()).flatten())
            self.target_values.append(target_value)

    def load(self):
        self._load('Images/Training/Stage 01 - Mobs', 1)
        self._load('Images/Training/Stage 02 - Mobs', 1)
        self._load('Images/Training/Player/', 2)
        self._load('Images/Training/Empty', 0)

    def train(self):
        if os.path.isfile('svc.dat'):
            self.svc = joblib.load('svc.dat')
        else:
            self.load()
            np_data = np.array(self.training_data)
            print (np.array(self.training_data))
            np_values = np.array(self.target_values)
            self.svc.fit(np_data, np_values)
            joblib.dump(self.svc, 'svc.dat', compress=9)

    def test(self):
        np_train_data = np.array(self.training_data)
        np_values = np.array(self.target_values)
        data, test_data, train_target, test_target = cross_validation.train_test_split(np_train_data, np_values,
                                                                                       test_size=0.4, random_state=0)
        self.svc.fit(data, train_target)
        print self.svc.score(test_data, test_target)

    def predict(self, img):
        resized_img = img.resize(self.downscale_res, Image.BILINEAR)
        np_img = (np.array(resized_img.getdata()).flatten())
        np_img = np.array(np_img).reshape(1,-1)
        return int(self.svc.predict(np_img))








