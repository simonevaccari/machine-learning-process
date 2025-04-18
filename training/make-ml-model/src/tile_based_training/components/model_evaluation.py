from sklearn import metrics
import mlflow
import os
import numpy as np
import tensorflow as tf
from pathlib import Path
from mlflow.keras import log_model
from matplotlib import pyplot as plt
from tile_based_training.config.configuration import EvaluationConfig
from tile_based_training.utils.common import *
import seaborn as sns

# from src.pipeline.stage_03_model_training import history
from keras.models import load_model
from mlflow.models import infer_signature


class Evaluation:
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.model = None
        self.class_names = [
            "AnnualCrop", "Forest", "HerbaceousVegetation", "Highway",
            "Industrial", "Pasture", "PermanentCrop", "Residential",
            "River", "SeaLake"
        ]
        self.label_lookup = {name: idx for idx, name in enumerate(self.class_names)}

    @staticmethod
    def load_model(path: Path):
        return load_model("src/tile_based_training/output/training/trained_model.keras")



    def _load_data_as_arrays(self, urls):
        images = []
        labels = []

        for url in urls:
            image, label = self._process_data(url)
            images.append(image)
            labels.append(label)

        images = np.stack(images)  # shape: (N, 64, 64, 12)
        labels = tf.stack(labels).numpy()  # shape: (N, 10)
        return images, labels
    
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


    def evaluation(self):
        create_directories([Path("./mlruns")])
        self.model = self.load_model(self.config.path_of_model)

        test_paths = self.config.test_data_paths["url"]
        random.shuffle(test_paths)

        x_test, y_test = self._load_data_as_arrays(test_paths)

        self.score = self.model.evaluate(x_test, y_test)  
        y_pred = self.model.predict(x_test)

        self.y_true = np.argmax(y_test, axis=1)  
        self.y_pred_amax = np.argmax(y_pred, axis=1)

        self.matrix = metrics.confusion_matrix(self.y_true, self.y_pred_amax)

        sample_input = x_test[0:1]  # ✅ keep batch dim
        sample_output = self.model.predict(sample_input)
        self.signature = infer_signature(sample_input, sample_output)
        self.save_scores()
        return (x_test, y_test), self.matrix


    def save_scores(self):
        scores = {
            "new_experiment": {
                "loss": self.score[0],
                "test_accuracy": self.score[1],
                "test_precision": self.score[2],
                "test_recall": self.score[3],
                "confusion_Matrix": self.matrix.tolist(),
            }
        }
        print(
            {
                "new_experiment": {
                    "test_loss": self.score[0],
                    "test_accuracy": self.score[1],
                    "test_precision": self.score[2],
                    "test_recall": self.score[3],
                }
            }
        )

    def plot_confusion_matrix(self):
        class_names = np.unique(self.y_true)
        sns.set(font_scale=1.2)  # Adjust font size for better readability
        fig, ax = plt.subplots()
        # Create a heatmap
        sns.heatmap(
            self.matrix,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=class_names,
            yticklabels=class_names,
        )

        # Add labels and title
        plt.xlabel("Predicted")
        plt.ylabel("True")
        plt.title("Confusion Matrix")

        # Show the plot
        plt.show()
        return fig

    def log_into_mlflow(self):
        logger.info(f"MLFLOW_TRACKING_URI: {os.environ.get('MLFLOW_TRACKING_URI')}")
        mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI"))
        tracking_url_type_store = urlparse(os.environ.get("MLFLOW_TRACKING_URI")).scheme
        confusion_matrix_figure = self.plot_confusion_matrix()
        mlflow.set_experiment("EuroSAT_classification")
        with mlflow.start_run():

            mlflow.tensorflow.autolog()
            mlflow.log_params(self.config.all_params)
            mlflow.log_figure(confusion_matrix_figure, artifact_file="Confusion_Matrix.png")
            mlflow.log_metrics(
                {
                    "loss": self.score[0],
                    "test_accuracy": self.score[1],
                    "test_precision": self.score[2],
                    "test_recall": self.score[3],
                }
            )

            # Explicit dependencies for model reloading

            # Model registry does not work with file store
            if tracking_url_type_store != "file":
                # Register the model
                # There are other ways to use the Model Registry, which depends on the use case,
                # please refer to the doc for more information:
                # https://mlflow.org/docs/latest/model-registry.html#api-workflow

                log_model(
                    model=self.model,
                    artifact_path="model/model.keras",
                    signature=self.signature,
                    registered_model_name=f"CNN",
                    # pip_requirements=pip_requirements,
                )

            else:
                log_model(
                    model=self.model,
                    artifact_path="model/model.keras",
                    signature=self.signature,
                    registered_model_name=f"CNN",
                    # pip_requirements=pip_requirements,
                )







    # @staticmethod
    # def read_images(file_path, label):
    #     try:
    #         file_path = file_path.numpy().decode("utf-8")
    #         data = rasterio_read(file_path)
    #         #data = data / np.amax(data)
    #         data = data / 10000.0
    #         image_data = np.transpose(data, (1, 2, 0))
    #         return tf.convert_to_tensor(image_data, dtype=tf.float32), tf.convert_to_tensor(label, dtype=tf.float32)
    #     except Exception as e:
    #         print("Error:", e)
    #         return (None, label)


    # def test_dataloader(self, file_paths):
    #     classes = {
    #         "AnnualCrop": 0,
    #         "Forest": 1,
    #         "HerbaceousVegetation": 2,
    #         "Highway": 3,
    #         "Industrial": 4,
    #         "Pasture": 5,
    #         "PermanentCrop": 6,
    #         "Residential": 7,
    #         "River": 8,
    #         "SeaLake": 9,
    #     }
    #     labels = [tf.one_hot(classes[file_path.split("/")[-2].split("_")[0]], depth=10) for file_path in file_paths]

    #     dataset = tf.data.Dataset.from_tensor_slices((file_paths, labels))

    #     dataset = dataset.map(lambda x, y: tf.py_function(self.read_images, [x, y], (tf.float32, tf.float32)))
    #     dataset.map(
    #         lambda x, y: tf.py_function(self.read_images, [x, y], (tf.float32, tf.float32)),
    #         num_parallel_calls=tf.data.AUTOTUNE,
    #     )
    #     dataset = dataset.map(lambda x, y: (tf.ensure_shape(x, [64, 64, 13]), tf.ensure_shape(y, [10])))
    #     dataset = dataset.batch(self.config.params_batch_size).cache().prefetch(tf.data.AUTOTUNE)

    #     return dataset