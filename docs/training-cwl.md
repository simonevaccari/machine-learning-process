# Training Module & CWL Runner

This Application Package provides a CWL document containing a top-level workflow with a singleCommandLineToolstep that executes the training pipeline. It also supports **parallel execution**, allowing users to specify multiple sets of hyperparameter or training configurations. This makes it suitable for large-scale experiments and hyperparameter tuning on platforms like a Minikube cluster.

To execute the training workflow, users can choose between [cwltool](https://github.com/common-workflow-language/cwltool) and [Calrissian](https://github.com/Duke-GCB/calrissian) as their CWL runners.

# Inputs:

| Parameter              | Type     | Description |
|------------------------|----------|-------------|
| MLFLOW_TRACKING_URI    | string      | An environment variable for the MLFLOW_TRACKING_URI |
| stac_reference         | string   | URL pointing to a STAC catalog. The model reads GeoParquet annotations from the collection's assets. |
| BATCH_SIZE             | int[]    | Number of batches |
| CLASSES                | int      | Number of land cover classes to classify. |
| DECAY                  | float[]  | Decay value used in training. |
| EPOCHS                 | int[]    | Number of epochs |
| EPSILON                | float[]  | Epsilon value (model hyperparameter) |
| LEARNING_RATE          | float[]  | Initial learning rate for the optimizer. |
| LOSS                   | string[] | Loss function for training. Options: `binary_crossentropy`, `cosine_similarity`, `mean_absolute_error`, `mean_squared_logarithmic_error`, `squared_hinge`. |
| MEMENTUM               | float[]  | Momentum parameter used in optimizers |
| OPTIMIZER              | string[] | Optimization algorithm. Options: `Adam`, `SGD`, `RMSprop`. |
| REGULARIZER            | string[] | Regularization technique to avoid overfitting. Options: `l1l2`, `l1`, `l2`, `None`. |
| SAMPLES_PER_CLASS      | int      | Number of samples to use for training per class. |


## How to execute the application-package?
Before running the application with a CWL runner, make sure to download and use the latest version of the CWL document:
```
cd /workspace/machine-learning-process/training/app-package
VERSION="0.0.4"
curl -L -o "tile-sat-training.cwl" \
  "https://github.com/eoap/machine-learning-process/releases/download/${VERSION}/tile-sat-training.${VERSION}.cwl"

```


### **Run the Application package**:
There are two methods to execute the application:

- Executing the tile-based-training using cwltool in a terminal:

   ```
    cwltool --podman --debug --parallel tile-sat-training.cwl#tile-sat-training params.yaml
   ```
    


- Executing the tile-based classification using calrissian in a terminal:

   ```
    calrissian --debug --stdout /calrissian/out.json --stderr /calrissian/stderr.log --usage-report /calrissian/report.json --parallel --max-ram 10G --max-cores 2 --tmp-outdir-prefix /calrissian/tmp/ --outdir /calrissian/results/ --tool-logs-basepath /calrissian/logs tile-sat-training.cwl#tile-sat-training params.yaml
   ```
   > You can monitor the pod creation using command below:
   >
   >   `kubectl get pods` 


## How the CWL document designed:
The CWL file can be triggered using `cwltool` or `calrissian`. The user provides a `params.yml` file that passes all inputs needed by the CWL file to execute the module. The CWL file is designed to execute the module based on the structure below:

![Training Workflow](imgs/training.png)


> **`[]`** in the image above indicates that the user may pass a list of parameters to the application package.


## Troubleshooting

The user might encounter to memory issues during the execution with CWL Runners. This can be addressing by reducing the `ramMax` parameter in the cwl file.