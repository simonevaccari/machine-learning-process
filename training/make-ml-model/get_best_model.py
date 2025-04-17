import os
import json
import mlflow
import mlflow.pyfunc
import tensorflow as tf
import tf2onnx
import onnx

# Configuration
params = {
    "s2_item": "https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items/S2B_10SFH_20230613_0_L2A",
    "MLFLOW_TRACKING_URI": "http://127.0.0.1:5000",
    "experiment_name": "EuroSAT_classification",
    "experiment_id": "EuroSAT_classification",
    "onnx_output_path": "./model2.onnx"
}

import mlflow
import mlflow.tensorflow
import tensorflow as tf
import tf2onnx
import json

# Search for the best run
active_runs = (
    mlflow.search_runs(
        experiment_names=[params["experiment_id"]],
        # Select the best one with highest f1_score and test accuracy
        filter_string="metrics.test_recall > 0.75",
        search_all_experiments=True,
    )
    .sort_values(
        by=["metrics.test_accuracy", "metrics.test_precision"],
        ascending=False,
    )
    .reset_index()
    .loc[0]
)

artifact_path = json.loads(active_runs["tags.mlflow.log-model.history"])[0][
    "artifact_path"
]
best_model_path = active_runs.artifact_uri + f"/{artifact_path}"
print()
# Load the TensorFlow model from MLflow
tf_model = mlflow.tensorflow.load_model(model_uri=best_model_path)
# Convert the TensorFlow model to ONNX format
onnx_model, _ = tf2onnx.convert.from_keras(tf_model)

# Specify the path to save the ONNX model
onnx_path = "./model.onnx"

# Save the ONNX model
with open(onnx_path, "wb") as f:
    f.write(onnx_model.SerializeToString())

print(f"ONNX model saved successfully to: {onnx_path}")
