# Export the Best Model to ONNX Format

This notebook provides a step-by-step tutorial for exporting a selected model from the MLflow model registry to ONNX format. The converted model is saved within the inference Python module to support the development of a new Python application and the creation of an inference Docker image, which is then published to the designated container registry. 

> **Note**: This process has already been completed. However, users may need to repeat it with their own candidate models.

## Install dependencies


```python
pip install tf2onnx onnxmltools onnxruntime onnx mlflow tensorflow
```

## Import dependencies


```python
import json
import os
import mlflow
import tensorflow as tf
import tf2onnx
import keras

```

## Save Model in ONNX Format

In the cells below, the user will download the best model artifact from the MLflow model registry and then save it in the ONNX format.

> **Note:** You may need to decrease the `desired_test_accuracy` to find active runs in the MLflow model registry.



```python
params = {
    "MLFLOW_TRACKING_URI": "http://localhost:5000/",
    "experiment_id": "EuroSAT_classification",
    
}
desired_test_accuracy = 0.85
```


```python
# Search for best run
active_runs = (
    mlflow.search_runs(
        experiment_names=[params["experiment_id"]],
        filter_string=f"metrics.test_accuracy > {desired_test_accuracy}",
        search_all_experiments=True,
    )
    .sort_values(by=["metrics.test_accuracy", "metrics.test_precision"], ascending=False)
    .reset_index()
    .loc[0]
)
run_id = active_runs["run_id"]
print(f"Selected run_id: {run_id}")

# Download just the .keras file
model_uri = f"runs:/{run_id}/model/model.keras/data/model.keras"
keras_path = mlflow.artifacts.download_artifacts(artifact_uri=model_uri)
print(f"Downloaded Keras file path: {keras_path}")

# Load the Keras v3 model
keras_model = keras.models.load_model(keras_path)

# Define input signature
input_signature = [tf.TensorSpec([None, 64, 64, 12], tf.float32, name="input")]

@tf.function(input_signature=input_signature)
def model_func(x):
    return keras_model(x)

# Convert to ONNX
onnx_model, _ = tf2onnx.convert.from_function(
    model_func,
    input_signature=input_signature,
    opset=13,
    output_path="model.onnx"
)

print("✅ Successfully saved model.onnx")

```
