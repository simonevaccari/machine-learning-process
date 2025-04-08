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

    @staticmethod
    def read_images(file_path, label):
        try:
            file_path = file_path.numpy().decode("utf-8")
            data = rasterio_s3_read(file_path)
            data = data / np.amax(data)
            # data = data / 10000.0
            image_data = np.transpose(data, (1, 2, 0))

            ## uncomment this when you download the data
            # image_data = np.transpose(gdal_array.LoadFile(file_path.numpy().decode("utf-8"))/10000.0,(1,2,0))

            return tf.convert_to_tensor(image_data, dtype=tf.float32), tf.convert_to_tensor(label, dtype=tf.float32)
        except Exception as e:
            print("Error:", e)
            return (None, label)

    def test_dataloader(self, file_paths):
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

        dataset = dataset.map(lambda x, y: tf.py_function(self.read_images, [x, y], (tf.float32, tf.float32)))
        dataset.map(
            lambda x, y: tf.py_function(self.read_images, [x, y], (tf.float32, tf.float32)),
            num_parallel_calls=tf.data.AUTOTUNE,
        )
        dataset = dataset.map(lambda x, y: (tf.ensure_shape(x, [64, 64, 13]), tf.ensure_shape(y, [10])))
        dataset = dataset.batch(self.config.params_batch_size).cache().prefetch(tf.data.AUTOTUNE)

        return dataset

    @staticmethod
    def load_model(path: Path):
        return load_model("src/tile_based_training/output/training/trained_model.keras")

    def evaluation(self):
        create_directories([Path("./mlruns")])
        self.model = self.load_model(self.config.path_of_model)
        test_paths = self.config.test_data_paths["url"]
        random.shuffle(test_paths)
        test_dataset = self.test_dataloader(test_paths).shuffle(buffer_size=2 * self.config.params_batch_size).cache()

        self.score = self.model.evaluate(test_dataset)
        y_pred = self.model.predict(test_dataset.map(lambda x, y: x))

        # Extract true labels directly from the test_dataset
        self.y_true = np.array([np.argmax(y.numpy()) for _, y in test_dataset.unbatch()])
        # Extract predicted labels
        self.y_pred_amax = np.argmax(y_pred, axis=1)

        # Calculate confusion matrix
        self.matrix = metrics.confusion_matrix(self.y_true, self.y_pred_amax)

        # Infer MLflow signature
        sample_batch = next(iter(test_dataset.take(1)), None)
        if sample_batch is not None:
            sample_input = sample_batch[0].numpy()  # Extract input images
            sample_output = self.model.predict(sample_input)  # Get predictions
            self.signature = infer_signature(sample_input, sample_output)
        else:
            self.signature = None  # Handle empty dataset case

        self.save_scores()
        return test_dataset, self.matrix

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
