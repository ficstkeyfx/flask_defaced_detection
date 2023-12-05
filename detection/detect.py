from efficientnet.tfkeras import EfficientNetB0
from tensorflow.keras.models import Sequential
from tensorflow.keras import layers as L
import matplotlib.pyplot as plt
import numpy as np
from skimage import transform
class Detection:
    IMG_SIZE = 224

    def __init__(self, mode="image", model="efficientnet"):
        self.mode = mode
        self.cur_model = model
        self.model = self.load_model(mode, model)
    
    def load_model(self, mode, _model):
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
    
    def load_image(self, filename):
        img = plt.imread(filename)
        resized_image = transform.resize(img, (224, 224, 3), anti_aliasing=True)
        resized_image = np.expand_dims(resized_image, axis=0)
        return resized_image
        
    def detect(self, filename):
        if(self.mode == "image"):
            image = self.load_image(filename)
            y_prob = self.model.predict(image)
            y_pred = np.argmax(y_prob, axis=1)
            return y_pred[0]
    
if(__name__=="__main__"):
    detect = Detection()
    detect.detect("D:\\data\\data\\benign\\image\\0a076f5bf_https___girlsdateforfree.com.png")
    detect.detect("D:\\data\\data\\deface\\image\\535998e0d3284adcb736e2ade1f9e591d7953e0ede3ad2c704c3ae50789947c8.png")