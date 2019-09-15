import json
import sys

import numpy as np
from keras import Sequential
from keras.layers import Embedding, LSTM, Dense
from keras_preprocessing import sequence
from keras_preprocessing.text import Tokenizer


def read_file():
    input_filename = sys.argv[1]
    with open(input_filename, 'r', encoding='utf8') as r:
        m = json.load(r)
    maxlen = 80
    max_features = 20_000
    batch_size = 32

    t = Tokenizer(num_words=max_features, oov_token='OOH')
    np.random.seed(123)
    indices = np.arange(0, len(m))
    np.random.shuffle(indices)
    m = np.array(m)[indices].tolist()
    c = int(len(m) * 0.9)
    train = m[:c]
    test = m[c:]
    train_texts = [a['article_content'] for a in train]
    test_texts = [a['article_content'] for a in test]
    t.fit_on_texts(train_texts)

    train_sequences = t.texts_to_sequences(train_texts)
    test_sequences = t.texts_to_sequences(test_texts)

    x_train = sequence.pad_sequences(train_sequences, maxlen=maxlen)
    x_test = sequence.pad_sequences(test_sequences, maxlen=maxlen)
    print('x_train shape:', x_train.shape)
    print('x_test shape:', x_test.shape)

    # targets
    median_up_down = np.median([int(a['vote_up']) / int(a['vote_down']) for a in train])
    train_targets = [int(a['vote_up']) / int(a['vote_down']) > median_up_down for a in train]
    test_targets = [int(a['vote_up']) / int(a['vote_down']) > median_up_down for a in test]

    y_train = np.array(train_targets, dtype=np.int)
    y_test = np.array(test_targets, dtype=np.int)

    print('Build model...')
    model = Sequential()
    model.add(Embedding(max_features, 128))
    model.add(LSTM(128, dropout=0.2, recurrent_dropout=0.2))
    model.add(Dense(1, activation='sigmoid'))

    # try using different optimizers and different optimizer configs
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])

    print('Train...')
    model.fit(x_train, y_train,
              batch_size=batch_size,
              epochs=15,
              validation_data=(x_test, y_test))
    score, acc = model.evaluate(x_test, y_test, batch_size=batch_size)
    print('Test score:', score)
    print('Test accuracy:', acc)


if __name__ == '__main__':
    read_file()
