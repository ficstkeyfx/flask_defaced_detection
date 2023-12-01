from efficientnet.tfkeras import EfficientNetB0
from tensorflow.keras.models import Sequential
from tensorflow.keras import layers as L
import matplotlib.pyplot as plt
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
                model.load_weights(f'models/weights_{_model}_{mode}.h5')
                print(model.summary())
                return model
    
    def load_image(self, filename):
        pass
            
    
    def detect(self, filename):
        if(self.mode == "image"):
            image = self.load_image(filename)
            self.model.predict(image)
        pass
    
