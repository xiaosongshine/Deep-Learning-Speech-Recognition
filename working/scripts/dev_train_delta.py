import os
import sys
import librosa
import tflearn
import wave
import pickle
import tensorflow as tf
import librosa.display
import IPython.display
import numpy as np
import speech_data
from pydub import AudioSegment as audio



# now put all of the mfccs into an array
data = '/home/cc/working/data/devclean_seg/'
os.chdir(data)
speakers = speech_data.get_speakers(os.getcwd())
audio_files = os.listdir(os.getcwd())
mfccs = []
Y = []
for f in audio_files:
  Y.append(speech_data.one_hot_from_item(speech_data.speaker(f), speakers))
  y, sr = librosa.load(f)
  mfccs.append(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13))
#with open ('devclean_mfccs.pickle', 'rb') as fp:
#    mfcs = pickle.load(fp)
delta_mfccs = []
for m in mfccs:
  delta_mfccs.append(librosa.feature.delta(m))
os.chdir('/home/cc/working/data/devclean_mfccs/')
with open('devclean_mfccs_delta.pickle', 'wb') as fp:
    pickle.dump(mfccs, fp)

net = tflearn.input_data(shape=[None, 13, 44]) 
net = tflearn.fully_connected(net, 64)
net = tflearn.dropout(net, 0.6)
net = tflearn.fully_connected(net, len(speakers), activation='softmax')
net = tflearn.regression(net, optimizer='adam', loss='categorical_crossentropy')

model = tflearn.DNN(net)
model.load('/home/cc/working/models/devclean/devclean_train.tflearn')
model.fit(delta_mfccs, Y, n_epoch=2000, show_metric=True, snapshot_step=100)

#os.chdir('/home/cc/working/models/devclean/')
#model.save('devclean_train_delta.tflearn')

os.chdir('/home/cc/working/data/devclean_test/')

test = []
for f1 in os.listdir(os.getcwd()):
  y, sr = librosa.load(f1)
  test.append(librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13))
result=model.predict(test)
c = 0
for f,r in zip(os.listdir(os.getcwd()), result):
  res = speech_data.one_hot_to_item(r, speakers)
  if res in f:
    c = c + 1
print('correct: %s ; total: %s' %(str(c), str(len(test))))
