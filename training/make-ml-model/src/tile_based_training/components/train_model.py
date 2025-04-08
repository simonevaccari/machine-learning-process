import sys
import numpy as np
import tensorflow as tf
import random
from tile_based_training.utils.common import rasterio_s3_read
from tile_based_training import logger


class Training:
    def __init__(self, config):
        self.config = config
        self.model = None  # Ensure model is initialized properly

    def get_base_model(self):
        """Load the base model from the given path."""
        self.model = tf.keras.models.load_model(self.config.base_model_path)
        # if device_name == "/GPU:0":
        #     with tf.device("/GPU:0"):  # Ensure model is loaded on the GPU
        #         self.model = tf.keras.models.load_model(self.config.base_model_path)
        # else:
        #     with tf.device("/CPU:0"):  # Ensure model is loaded on the CPU
        #         self.model = tf.keras.models.load_model(self.config.base_model_path)

    @staticmethod
    def read_images(file_path, label):
        """Reads images, preprocesses, and returns tensors."""
        try:
            file_path = file_path.numpy().decode("utf-8")
            data = rasterio_s3_read(file_path)  # Assuming this is correctly defined elsewhere
            data = data / np.amax(data)  # Normalize
            # data = data / 10000.0 # Normalize
            image_data = np.transpose(data, (1, 2, 0))  # Transpose for proper shape
            return tf.convert_to_tensor(image_data, dtype=tf.float32), tf.convert_to_tensor(label, dtype=tf.float32)

        except Exception as e:
            print("Error:", e)
            sys.exit(1)
            # return tf.zeros((64, 64, 13)), tf.zeros((10,))  # Return default tensor shape

    def train_valid_dataloader(self, file_paths):
        """Creates a TensorFlow dataset with image-label pairs."""
        classes = {
            "AnnualCrop": 0,
            "Forest": 1,
            "HerbaceousVegetation": 2,
            "Highway": 3,
            "Industrial": 4,
            "Pasture": 5,
            "PermanentCrop": 6,
            "Residential": 7,
            "River": 8,
            "SeaLake": 9,
        }

        labels = [tf.one_hot(classes[file_path.split("/")[-2].split("_")[0]], depth=10) for file_path in file_paths]
        dataset = tf.data.Dataset.from_tensor_slices((file_paths, labels))
        dataset = dataset.map(lambda x, y: (tf.strings.as_string(x), y))

        # Optimize dataset performance
        dataset = dataset.map(
            lambda x, y: tf.py_function(self.read_images, [x, y], (tf.float32, tf.float32)),
        )
        dataset = dataset.map(
            lambda x, y: (
                tf.ensure_shape(x, self.config.params_image_size),
                tf.ensure_shape(y, self.config.calsses_number),
            )
        )
        dataset = dataset.batch(self.config.params_batch_size).cache().prefetch(tf.data.AUTOTUNE)

        return dataset

    def train_model(self, device_name):
        """Handles GPU setup, prepares data, and trains the model."""

        # Prepare datasets
        train_paths = self.config.train_data["url"]
        random.shuffle(train_paths)
        train_dataset = self.train_valid_dataloader(train_paths)

        val_paths = self.config.val_data["url"]

        val_dataset = self.train_valid_dataloader(val_paths)
        # for x, y in enumerate(train_dataset):
        #     print(x)
        #     print()
        #     print(y)
        #     break
        # sys.exit(0)
        # Model checkpointing
        checkpoint = tf.keras.callbacks.ModelCheckpoint(
            str(self.config.trained_model_path) + "/trained_model.keras",
            monitor="val_accuracy",
            verbose=1,
            save_best_only=True,
            mode="max",
        )
        # for x, y in train_dataset:
        #     print(x.shape, y.shape)
        # break
        # print("Device name is: ", device_name)
        # tf.debugging.set_log_device_placement(True)

        # print("Is TensorFlow using GPU?", tf.test.is_gpu_available(cuda_only=True, min_cuda_compute_capability=None))
        # print("GPU Devices:", tf.config.list_logical_devices('GPU'))

        # **Train on the correct device**
        # Use dynamically assigned device
        logger.info(f"Device is: {device_name} , Built with CUDA: {tf.test.is_built_with_cuda()}")
        try:
            with tf.device(device_name):
                history = self.model.fit(
                    train_dataset,
                    epochs=self.config.params_epochs,
                    validation_data=val_dataset,
                    callbacks=[checkpoint],
                    verbose=1,
                )
                return history
        except Exception as e:
            print(f"❌ Training failed: {e}")
            sys.exit(1)
