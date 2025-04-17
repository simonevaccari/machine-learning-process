import sys
import numpy as np
import tensorflow as tf
import random
from tqdm import tqdm
from tile_based_training.utils.common import rasterio_read, augmentation
from tile_based_training import logger


# class Training:
#     def __init__(self, config):
#         self.config = config
#         self.model = None  # Ensure model is initialized properly

#     def get_base_model(self):
#         """Load the base model from the given path."""
#         self.model = tf.keras.models.load_model(self.config.base_model_path)
    

#     @staticmethod
#     def read_images(file_path, label):
#         """Reads images, preprocesses, and returns tensors."""
#         try:
#             file_path = file_path.numpy().decode("utf-8")
#             data = rasterio_read(file_path)  
#             data = augmentation(data)
            
#             image_data = np.transpose(data, (1, 2, 0))  # Transpose for proper shape
#             print("Image shape:", image_data.shape)  # Or use logger

#             return tf.convert_to_tensor(image_data, dtype=tf.float32), tf.convert_to_tensor(label, dtype=tf.float32)

#         except Exception as e:
#             print("Image shape:", image_data.shape)
#             sys.exit(1)
#             # return tf.zeros((64, 64, 13)), tf.zeros((10,))  # Return default tensor shape

#     def train_valid_dataloader(self, file_paths):
#         """Creates a TensorFlow dataset with image-label pairs."""
#         classes = {
#             "AnnualCrop": 0,
#             "Forest": 1,
#             "HerbaceousVegetation": 2,
#             "Highway": 3,
#             "Industrial": 4,
#             "Pasture": 5,
#             "PermanentCrop": 6,
#             "Residential": 7,
#             "River": 8,
#             "SeaLake": 9,
#         }

#         labels = [tf.one_hot(classes[file_path.split("/")[-2].split("_")[0]], depth=10) for file_path in file_paths]
#         dataset = tf.data.Dataset.from_tensor_slices((file_paths, labels))
#         dataset = dataset.map(lambda x, y: (tf.strings.as_string(x), y))

#         # Optimize dataset performance
#         dataset = dataset.map(
#             lambda x, y: tf.py_function(self.read_images, [x, y], (tf.float32, tf.float32)),
#         )
#         dataset = dataset.map(
#             lambda x, y: (
#                 tf.ensure_shape(x, [64, 64, 12]),
#                 tf.ensure_shape(y, self.config.classes_number),
#             )
#         )
#         dataset = dataset.batch(self.config.params_batch_size).cache().prefetch(tf.data.AUTOTUNE)

#         return dataset

#     def train_model(self, device_name):
#         """Handles GPU setup, prepares data, and trains the model."""
#         # Prepare datasets
#         train_paths = self.config.train_data["url"]
#         random.shuffle(train_paths)
#         train_dataset = self.train_valid_dataloader(train_paths)

#         val_paths = self.config.val_data["url"]

#         val_dataset = self.train_valid_dataloader(val_paths)
        
#         # Model checkpointing
#         checkpoint = tf.keras.callbacks.ModelCheckpoint(
#             str(self.config.trained_model_path) + "/trained_model.keras",
#             monitor="val_accuracy",
#             verbose=1,
#             save_best_only=True,
#             mode="max",
#         )

#         # **Train on the correct device**
#         # Use dynamically assigned device
#         logger.info(f"Device is: {device_name} , Built with CUDA: {tf.test.is_built_with_cuda()}")
#         try:
#             with tf.device(device_name):
#                 history = self.model.fit(
#                     train_dataset,
#                     epochs=self.config.params_epochs,
#                     validation_data=val_dataset,
#                     callbacks=[checkpoint],
#                     verbose=1,
#                 )
#                 return history
#         except Exception as e:
#             print(f"❌ Training failed: {e}")
#             sys.exit(1)








import numpy as np
import tensorflow as tf
import random
import logging

logger = logging.getLogger(__name__)

class Training:
    def __init__(self, config):
        self.config = config
        self.model = None

        self.class_names = [
            "AnnualCrop", "Forest", "HerbaceousVegetation", "Highway",
            "Industrial", "Pasture", "PermanentCrop", "Residential",
            "River", "SeaLake"
        ]
        self.label_lookup = {name: idx for idx, name in enumerate(self.class_names)}

    def get_base_model(self):
        self.model = tf.keras.models.load_model(self.config.base_model_path)

    def fetch_image(self, url):
        image = rasterio_read(str(url))  # e.g., (12, 64, 64)
        image = augmentation(image)  # Apply augmentations
        image = np.transpose(image, (1, 2, 0))  # to (64, 64, 12)
        return image.astype(np.float32)

    def _process_data(self, url):
        image = self.fetch_image(url)
        label_str = url.split("/")[-2]
        label_id = self.label_lookup[label_str]
        label = tf.one_hot(label_id, depth=10)
        return image, label

    def ___getitem__(self, index):
        url = self.config.train_data["url"][index]
        return self._process_data(url)

    def _load_data_as_arrays(self, urls):
        images = []
        labels = []

        for url in tqdm(urls, total=len(urls), desc="Loading data"):
            image, label = self._process_data(url)
            images.append(image)
            labels.append(label)

        images = np.stack(images)  # shape: (N, 64, 64, 12)
        labels = tf.stack(labels).numpy()  # shape: (N, 10)

        return images, labels

    def train_model(self, device_name):
        train_paths = self.config.train_data["url"]
        val_paths = self.config.val_data["url"]

        random.shuffle(train_paths)

        x_train, y_train = self._load_data_as_arrays(train_paths)
        x_val, y_val = self._load_data_as_arrays(val_paths)

        checkpoint = tf.keras.callbacks.ModelCheckpoint(
            filepath=str(self.config.trained_model_path) + "/trained_model.keras",
            monitor="val_accuracy",
            save_best_only=True,
            mode="max",
            verbose=1
        )

        logger.info(f"Device is: {device_name}, Built with CUDA: {tf.test.is_built_with_cuda()}")

        self.model.fit(
            x_train,
            y_train,
            validation_data=(x_val, y_val),
            epochs=self.config.params_epochs,
            callbacks=[checkpoint],
            verbose=1
        )
        try:
            del x_train, y_train, x_val, y_val
            tf.keras.backend.clear_session()
            logger.info("Training completed and session cleared.")

        except Exception as e:
            logger.error(f"Error during deletion: {e}")






    def process(self, url):
        image, label = tf.py_function(
            func=self._process_data,
            inp=[url],
            Tout=(tf.float32, tf.float32)
        )
        image.set_shape([64, 64, 12])
        label.set_shape([10])
        return image, label

    def train_valid_dataloader(self, file_paths):
        file_paths = tf.constant(file_paths)
        dataset = tf.data.Dataset.from_tensor_slices(file_paths)
        dataset = dataset.map(self.process, num_parallel_calls=tf.data.AUTOTUNE)
        dataset = dataset.batch(self.config.params_batch_size)
        dataset = dataset.cache().prefetch(tf.data.AUTOTUNE)
        return dataset