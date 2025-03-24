# Machine-Learning-Process-Training
This folder containing a python application for training a machine learning model on EuroSAT dataset for tile-based classification task.

# Table of content:
- [Installation](#installation)
- [Docker](#docker)
- [Structure of this task](#structure-of-this-task)



## Installation:
For this section, the user can execute the Tile-Based training module using hatch.

**Execution using hatch**:
The user can install and execute the application as below:

```bash
hatch shell prod
source "/workspace/hatch/envs/prod/bin/activate"

export AWS_ACCESS_KEY_ID="fill this"
export AWS_SECRET_ACCESS_KEY="fill this" 
export AWS_DEFAULT_REGION="fill this"
export AWS_REGION="fill this"
export AWS_S3_ENDPOINT="fill this"
export BUCKET_NAME="fill this"
export IAM_URL="fill this" 
export IAM_PASSWORD="fill this" 
export MLFLOW_TRACKING_URI="fill this"


hatch run prod:tile-based-training --stac_endpoint_url https://ai-extensions-stac.terradue.com/collections/Euro_SAT --BATCH_SIZE 4 --CLASSES 10 --DECAY 0.1 --EPOCHS 10 --EPSILON 0.000001 --IMAGE_SIZE 64 --IMAGE_SIZE 64 --IMAGE_SIZE 13 --LEARNING_RATE 0.0001 --LOSS "categorical_crossentropy" --MEMENTUM 0.95 --OPTIMIZER "Adam" --REGULIZER "None" --SAMPLES_PER_CLASS 500 --enable_data_ingestion
```



## Build local docker image

The user can build the docker image using the command below:
```
docker build -t <image_tag> -f Dockerfile .
```


## Structure of this task
1. `src`/ `tile_based_training` /
    - <span style="color:gray">**components**</span> /
        - Containing all components such as data_ingestion.py, prepare_base_model.py, train_model.py , model_evaluation.py, inference.py.
    - <span style="color:gray">**config**</span> /
        - Containing all configuration needed for each component.
    - <span style="color:gray">**utils**</span> /
        - to define helper functions.
    - <span style="color:gray">**pipeline**</span> /
        - to define the order of executing for each component.
    
    > Notice: For more information how above units work please check the notebook under `trials` directory.
2. `output`/: A folder where all intermediate artifacts like references to train and test data, models, etc will be saved here.
3. `config`/ : A folder containing all configuration needed for the application is stored such as paths, name of classes , etc. 
4. `pyproject.toml`: installing all dependencies in hatch environment.

