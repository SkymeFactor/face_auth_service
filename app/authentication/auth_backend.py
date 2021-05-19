import tensorflow as tf
import cv2
import numpy as np

from io import BytesIO
from .iauth import IAuth

class AuthBackend(IAuth):
    def __init__(self, path='../.weights/'):
        self.gpu_init()
        self.model = tf.keras.models.load_model(path, compile=False)
        self.model.trainable = False

        # Compile manually
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
            loss=tf.keras.losses.SparseCategoricalCrossentropy(),
            metrics=['accuracy'],
            steps_per_execution=10
        )

    def gpu_init(self, log_device_placement=False):
        tf.config.set_visible_devices([], 'GPU')
        gpus = tf.config.list_physical_devices('GPU')
        try:
            [tf.config.experimental.set_memory_growth(gpu, True) for gpu in gpus]
        except RuntimeError as e:
            print("Couldn't configure gpu memory growth: ", e)
        tf.debugging.set_log_device_placement(log_device_placement)
    

    def compare(self, image_1: BytesIO, image_2: BytesIO):
        input = self.prepare_images(image_1, image_2)

        output = self.model.predict(input[np.newaxis, :, : , np.newaxis])

        return True if np.argmax(output) == 1 else False


    def prepare_images(self, image_1: BytesIO, image_2: BytesIO):
        file_bytes = np.asarray(bytearray(image_1.read()), dtype=np.uint8)
        im1 = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
        im1 = cv2.resize(im1, (160, 160), cv2.INTER_CUBIC)
        file_bytes = np.asarray(bytearray(image_2.read()), dtype=np.uint8)
        im2 = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
        im2 = cv2.resize(im2, (160, 160), cv2.INTER_CUBIC)

        concat = cv2.hconcat([im1, im2])

        return concat
