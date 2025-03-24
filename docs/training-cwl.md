# Training Module & CWL Runner

The users have the option to execute their training remotely on a remote machine, which becomes their preferred choice for conducting long-running experiments. 
 The user will be able to train a simple training job and track evaluation metrics, model's hyper-parameters, application inputs, and artifacts using mlflow. He/She should build a docker image from the application package which is explained in [training-container](./training-container.md) and push to a dedicated image registry (in this case we use github container registry). Then, The user develop a cwl document with containing a top layer workflow with a CommandLineTool step which is responsible for executing the training pipeline. For executing the application package, the user have the options to use whether [cwltool](https://github.com/common-workflow-language/cwltool) or [calrissian](https://github.com/Duke-GCB/calrissian).


## How to execute the application-package?
Before executing the application package with a CWL runner, the user must first update the [params.yaml](./params.yaml) including the inputs below:

with the correct credentials as well as updating the latest docker image reference in the cwl file as below:
```
stac_endpoint_url: https://ai-extensions-stac.terradue.com/collections/Euro_SAT
BATCH_SIZE: 4
EPOCHS: 3
LEARNING_RATE: 0.0001
DECAY: 0.1  ### float
EPSILON: 0.000002
MEMENTUM: 0.95
# choose one of binary_crossentropy/cosine_similarity/mean_absolute_error/mean_squared_logarithmic_error
# squared_hinge
LOSS: categorical_crossentropy  
# choose one of  l1,l2,None
REGULIZER: None
# try Adam/SGD/RMSprop
OPTIMIZER: Adam
###############################################################
###############################################################
# Dataset
SAMPLES_PER_CLASS: 10
CLASSES: 10
IMAGE_SIZE: [64, 64, 13]
enable_data_ingestion: True

```
and some environment variable must be set:

```
# Environment variables
# AWS
AWS_S3_ENDPOINT: #AWS_S3_ENDPOINT 
AWS_REGION: fr-par # AWS_REGION 
AWS_DEFAULT_REGION: fr-par #AWS_DEFAULT_REGION 
AWS_ACCESS_KEY_ID:  #AWS_ACCESS_KEY_ID 
AWS_SECRET_ACCESS_KEY:  # AWS_SECRET_ACCESS_KEY 
BUCKET_NAME: ai-ext-bucket-dev # BUCKET_NAME ai-ext-bucket-dev
##############################################################
##############################################################
# STAC
IAM_URL:  # IAM_URL
IAM_PASSWORD:  #IAM_PASSWORD
MLFLOW_TRACKING_URI: http://my-mlflow:5000
```
The latest version of cwl document can be fetched as below:

```
cd training/app-package
VERSION="0.0.2"
curl -L -o "tile-sat-training.${VERSION}.cwl" \
  "https://github.com/parham-membari-terradue/machine-learning-process-new/releases/download/${VERSION}/tile-sat-training.${VERSION}.cwl"

```


### **Run the Application package**:
There are two methods to execute the application:

- Executing the tile-based-training using cwltool in a terminal:

    ```
    cwltool --podman --debug tile-sat-training.cwl#tile-sat-training params.yml
    ```
    


- Executing the tile-based classification using calrissian in a terminal:

    ```
    calrissian --debug --stdout /calrissian/out.json --stderr /calrissian/stderr.log --usage-report /calrissian/report.json --max-ram 10G --max-cores 2 --tmp-outdir-prefix /calrissian/tmp/ --outdir /calrissian/results/ --tool-logs-basepath /calrissian/logs tile-sat-training.cwl#tile-sat-training params.yaml
    ```

   

## Additional Resources
Please see below for additional resources and tutorials for developing Earth Observation (EO) Application Packages using the CWL:
* [Application Package and CWL as a solution for EO portability](https://eoap.github.io/cwl-eoap/)
* [A simple EO Application Package for getting started](https://eoap.github.io/quickwin/)
* [Mastering EO Application Packaging with CWL](https://eoap.github.io/mastering-app-package/)
* [Inference with the EO Application Package](https://eoap.github.io/inference-eoap/)