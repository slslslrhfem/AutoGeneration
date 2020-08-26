import numpy as np
from keras.datasets import imdb
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers.embeddings import Embedding
from keras.preprocessing import sequence
from keras.utils import to_categorical
from keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from keras import regularizers
from sklearn.model_selection import KFold

def RNN_training(classifier,bar_matrix_list3):
    RNNx_train = []
    RNNy_train = []
    RNNx_test = []
    RNNy_test = []
    RNN_kfoldx = []
    RNN_kfoldy = []
    for i in range(len(bar_matrix_list3)):
        nowseq = []
        nowmat = np.array(bar_matrix_list3[i])
        nowbars = classifier.predict(nowmat.reshape(len(nowmat), 24, 24, 1))
        for j, bars in enumerate(nowbars):
            if (j == len(nowbars) - 1):
                if (i > 50):
                    RNNy_test.append(np.argmax(bars))
                else:
                    RNNy_train.append(np.argmax(bars))
                RNN_kfoldy.append(np.argmax(bars))
            else:
                nowseq.append(np.argmax(bars))
        if (i > 50):
            RNNx_test.append(nowseq)
        else:
            RNNx_train.append(nowseq)
        RNN_kfoldx.append(nowseq)
    RNN_kfoldy = to_categorical(np.array(RNN_kfoldy))
    # fix random seed for reproducibility
    np.random.seed(7)
    top_words = 12
    # truncate and pad input sequences
    RNN_kfoldx = sequence.pad_sequences(RNN_kfoldx, maxlen=10)
    model_path = 'RNNresult/' + 'RNN.h5'

    cb_checkpoint = ModelCheckpoint(filepath=model_path, monitor='val_accuracy',
                                    verbose=1, save_best_only=True)
    callbacks = [cb_checkpoint]
    embedding_vecor_length = 32
    timesteps = 12

    model = Sequential()
    model.add(Embedding(top_words, embedding_vecor_length, input_length=10))
    model.add(LSTM(100, return_sequences=True,
                   input_shape=(timesteps, 100)))  # returns a sequence of vectors of dimension 32
    model.add(LSTM(100))  # return a single vector of dimension 32
    model.add(Dropout(0.2))
    model.add(Dense(12, activation='sigmoid', kernel_regularizer=regularizers.l2(0.01)))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    print(model.summary())
    kfold = KFold(n_splits=5, shuffle=True, random_state=7)
    for i in range(3):
        for train, valid in kfold.split(RNN_kfoldx, RNN_kfoldy):
            model.fit(RNN_kfoldx[train], RNN_kfoldy[train], validation_data=(RNN_kfoldx[valid], RNN_kfoldy[valid])
                         , epochs=30, batch_size=64, callbacks=callbacks, class_weight='balanced')
    return model