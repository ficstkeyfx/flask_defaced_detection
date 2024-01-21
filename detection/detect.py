from efficientnet.tfkeras import EfficientNetB0
from tensorflow.keras.models import Sequential
from tensorflow.keras import layers as L
import matplotlib.pyplot as plt
import numpy as np
from skimage import transform
import pickle
class Detection:
    IMG_SIZE = 224

    def __init__(self, mode="image", model="efficientnet"):
        self.mode = mode
        self.cur_model = model
        self.model = self.load_model_image(mode, model)
        self.tokenizer = self.load_tokenizer()
        self.model_text = self.load_model_text("text", "bilstm")
    # ----------------------------------------------------------------
    # Image model
        
    def load_model_image(self, mode, _model):
        if(mode == "image"):
            if(_model == "efficientnet"):
                efn = EfficientNetB0(
                    include_top=False, 
                    weights='noisy-student', 
                    pooling='avg', 
                    input_shape=(self.IMG_SIZE, self.IMG_SIZE, 3))
                model = Sequential()
                model.add(efn)
                model.add(L.BatchNormalization())
                model.add(L.Dense(128, activation='softmax'))
                model.add(L.BatchNormalization())
                model.add(L.Dense(2, activation='softmax'))
                model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
                model.load_weights(f'detection/models/weights_{_model}_{mode}.h5')
                print(model.summary())
                return model
        elif mode == "text":
            pass
        elif mode == "fusion":
            pass
    
    # ----------------------------------------------------------------
    # Text model
    def load_tokenizer(self):
        with open('detection/models/tokenizer.pickle', 'rb') as handle:
            tokenizer = pickle.load(handle)
            return tokenizer
    
    def load_model_text(self, mode, _model):
        if(mode == "image"):
            pass
        elif mode == "text":
            if(_model == "bilstm"):
                # vocab_size = len(self.tokenizer.word_index) + 1
                vocab_size = 2829034
                model = Sequential()
                model.add(L.Embedding(input_dim=vocab_size,
                                    output_dim=64, 
                                    input_length=128))
                model.add(L.SpatialDropout1D(0.2))
                model.add(L.Bidirectional(L.LSTM(64, activation="softmax", return_sequences=False)))
                model.add(L.Dense(2, activation='softmax'))
                model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
                model.load_weights(f'detection/models/text-{_model}.h5') 
                print(model.summary())   
                return model
        elif mode == "fusion":
            pass
    # ----------------------------------------------------------------
    # Load file
    def load_image(self, filename):
        img = plt.imread(filename)
        resized_image = transform.resize(img, (224, 224, 3), anti_aliasing=True)
        resized_image = np.expand_dims(resized_image, axis=0)
        return resized_image

    def load_txt(self, filename):
        with open(filename, 'r') as f:
            text = f.read()
        text = self.tokenizer.texts_to_sequences(text)[0]
        text = np.expand_dims(text, axis=0)
        return text
    
    # ----------------------------------------------------------------
    # Detect
    def detect(self, filename, mode):
        if(mode == "image"):
            image = self.load_image(filename)
            y_prob = self.model.predict(image)
            y_pred = np.argmax(y_prob, axis=1)
            return y_pred[0]
        elif mode == "text":
            text = self.load_txt(filename)
            y_prob = self.model_text.predict(text)
            y_pred = np.argmax(y_prob, axis=1)
            return y_pred[0]
        elif mode == "fusion":
            filename_img, filename_txt = filename[0], filename[1]
            image = self.load_image(filename_img)
            y_prob_img = self.model.predict(image)
            y_pred_img = np.argmax(y_prob_img, axis=1)
            text = self.load_txt(filename_txt)
            y_prob_txt = self.model_text.predict(text)
            y_pred_txt = np.argmax(y_prob_txt, axis=1)
            y_prob = (y_prob_img + y_prob_txt)/2
            y_pred = np.argmax(y_prob, axis=1)
            return y_pred_img, y_pred_txt, y_pred[0]
    
if(__name__=="__main__"):
    detect = Detection()
    print(detect.detect("D:\\data\\dataset\\image\\benign\\0a076f5bf_https___girlsdateforfree.com.png", "image"))
    print(detect.detect("D:\\data\\dataset\\text\\benign\\0a076f5bf_https___girlsdateforfree.com.txt", "text"))
    print(detect.detect(["D:\\data\\dataset\\image\\benign\\0a076f5bf_https___girlsdateforfree.com.png","D:\\data\\dataset\\text\\benign\\0a076f5bf_https___girlsdateforfree.com.txt"], "fusion"))
    # detect.detect("D:\\data\\dataset\\image\\deface\\\\535998e0d3284adcb736e2ade1f9e591d7953e0ede3ad2c704c3ae50789947c8.png", "image")