# Describe a trained machine learning model

This Notebook leverages the capabilities of STAC to provide a comprehensive and standardized description of a trained ML model. This is done with a STAC Item file that encapsulates the relevant metadata (e.g. model name and version, description of the model architecture and training process, specifications of input and output data formats, etc.). 

This Notebook can be used for the following requirements:

* Import Libraries (e.g. `pystac`, `boto3`)
* Option to either create a STAC Item with `pystac`, or to upload an existing STAC Item into the Notebook. The STAC Item will contain all related ML model specific properties, related STAC extensions and hyperparameter.
* Create interlinked STAC Item, Catalog and Collection, and the STAC folder structure 

**Objective**:
By the end of this Notebook, the user will have published a STAC Item, Collection and Catalog into the STAC endpoint, and tested its search functionalities via query parameters. 

**Table of Content**:

1) Import Libraries
2) Create STAC Item, Catalog and Collection

## 1) Import Libraries


```python
from datetime import datetime
import os
import json
import requests
from pathlib import Path
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from tqdm import tqdm

import pystac
from pystac import read_file
from pystac.extensions.version import ItemVersionExtension
from pystac.extensions.eo import EOExtension
from pystac_client import Client
from pystac.stac_io import DefaultStacIO, StacIO
from pystac.extensions.eo import Band, EOExtension
from pystac.extensions.file import FileExtension


from loguru import logger
from urllib.parse import urljoin, urlparse

import boto3
import botocore

from utils import (
    UserSettings,
    StarsCopyWrapper,
    read_url,
    ingest_items,
    get_headers,
    CustomStacIO,
    getTemporalExtent,
    getGeom,
)
```

## 2) Create STAC Item, Catalog and Collection


```python
# Create folder structure
CATALOG_DIR = "ML_Catalog"
COLLECTION_NAME = "ML-Models_EO"
ITEM_ID = "Tile-based-ML-Models"
SUB_DIR = os.path.join(CATALOG_DIR, COLLECTION_NAME)
```

### STAC Item
**NOTE**: Please execute either section **2.1) Create STAC Item** or section **2.2) Upload STAC Item** below according to the following: 
* execute section **2.1) Create STAC Item** if you want to create a STAC Item from scratch using `pystac` within this Notebook; or 
* execute section **2.2) Upload STAC Item** if you have already created a STAC Item (i.e. a `.json`/`.geojson` file) and want to upload it into this Notebook

#### 2.1) Create STAC Item


```python
# Define BBOX of the Item
bbox = [-121.87680832296513, 36.93063805399626, -120.06532070709298, 38.84330548198025]

item = pystac.Item(
    id=ITEM_ID,
    bbox=bbox,
    geometry=getGeom(bbox),
    datetime=datetime.now(),
    properties={},
)
item
```






<style>
.pystac-summary {
    cursor: pointer;
    display: list-item;
    list-style: revert;
    margin-bottom: 0 !important;

    .pystac-l {
        padding-left: 0.5em;
        color: rgb(64, 128, 128);
        font-style: italic;
    }
}
.pystac-row {
    overflow-wrap: break-word;
    padding-left: .825em;

    .pystac-k {
        display: inline-block;
        margin: 0px 0.5em 0px 0px;
    }
    .pystac-v {
        color: rgb(186, 33, 33);
    }
}
.pystac-k {
    color: rgb(0, 128, 0);
    font-weight: 700;
}
</style>
<div class="jp-RenderedJSON jp-mod-trusted jp-OutputArea-output">
    <div class="container" style="line-height: normal;">
        <ul style="padding: 0px; margin: 0px; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"Feature"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">stac_version</span>
            <span class="pystac-v">"1.1.0"</span>
        </li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">stac_extensions</span><span class="pystac-l">[] 0 items</span></summary>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">id</span>
            <span class="pystac-v">"Tile-based-ML-Models"</span>
        </li>





        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">geometry</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"Polygon"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">coordinates</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">0</span><span class="pystac-l">[] 5 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">0</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">1</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-120.06532070709298</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">2</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-120.06532070709298</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">38.84330548198025</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">3</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">38.84330548198025</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">4</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

    </details></li>


    </ul>

    </details></li>


    </ul>

    </details></li>


    </ul>
        </details></li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">bbox</span><span class="pystac-l">[] 4 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">-120.06532070709298</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">3</span>
            <span class="pystac-v">38.84330548198025</span>
        </li>



    </ul>

    </details></li>




        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">properties</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">datetime</span>
            <span class="pystac-v">"2025-04-04T12:30:39.002998Z"</span>
        </li>



    </ul>
        </details></li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">links</span><span class="pystac-l">[] 0 items</span></summary>

    </details></li>




        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">assets</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">

    </ul>
        </details></li>



        </ul>
    </div>
</div>



### Adding Item properties
In the following section, the user will provide the Item's properties for creation of STAC Item.


```python
# Add standard properties
item.properties["start_datetime"] = "2023-06-13T00:00:00Z"
item.properties["end_datetime"] = "2023-06-18T23:59:59Z"
item.properties["description"] = (
    """Tile based classifier using CNNs for land cover classification. 
    The model is trained on the Sentinel-2 dataset and is capable of classifying 
    land cover types such as water, forest, urban, and agriculture. 
    The model is designed to work with Sentinel-2 imagery and can be used for """
)

item
```






<style>
.pystac-summary {
    cursor: pointer;
    display: list-item;
    list-style: revert;
    margin-bottom: 0 !important;

    .pystac-l {
        padding-left: 0.5em;
        color: rgb(64, 128, 128);
        font-style: italic;
    }
}
.pystac-row {
    overflow-wrap: break-word;
    padding-left: .825em;

    .pystac-k {
        display: inline-block;
        margin: 0px 0.5em 0px 0px;
    }
    .pystac-v {
        color: rgb(186, 33, 33);
    }
}
.pystac-k {
    color: rgb(0, 128, 0);
    font-weight: 700;
}
</style>
<div class="jp-RenderedJSON jp-mod-trusted jp-OutputArea-output">
    <div class="container" style="line-height: normal;">
        <ul style="padding: 0px; margin: 0px; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"Feature"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">stac_version</span>
            <span class="pystac-v">"1.1.0"</span>
        </li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">stac_extensions</span><span class="pystac-l">[] 0 items</span></summary>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">id</span>
            <span class="pystac-v">"Tile-based-ML-Models"</span>
        </li>





        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">geometry</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"Polygon"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">coordinates</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">0</span><span class="pystac-l">[] 5 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">0</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">1</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-120.06532070709298</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">2</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-120.06532070709298</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">38.84330548198025</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">3</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">38.84330548198025</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">4</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

    </details></li>


    </ul>

    </details></li>


    </ul>

    </details></li>


    </ul>
        </details></li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">bbox</span><span class="pystac-l">[] 4 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">-120.06532070709298</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">3</span>
            <span class="pystac-v">38.84330548198025</span>
        </li>



    </ul>

    </details></li>




        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">properties</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">datetime</span>
            <span class="pystac-v">"2025-04-04T12:30:39.002998Z"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">start_datetime</span>
            <span class="pystac-v">"2023-06-13T00:00:00Z"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">end_datetime</span>
            <span class="pystac-v">"2023-06-18T23:59:59Z"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Tile based classifier using CNNs for land cover classification. 
    The model is trained on the Sentinel-2 dataset and is capable of classifying 
    land cover types such as water, forest, urban, and agriculture. 
    The model is designed to work with Sentinel-2 imagery and can be used for "</span>
        </li>



    </ul>
        </details></li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">links</span><span class="pystac-l">[] 0 items</span></summary>

    </details></li>




        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">assets</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">

    </ul>
        </details></li>



        </ul>
    </div>
</div>




```python
# Add "ml-model" properties
item.properties["ml-model:type"] = "ml-model"
item.properties["ml-model:learning_approach"] = "supervised"
item.properties["ml-model:prediction_type"] = "classification"
item.properties["ml-model:architecture"] = "ResNet-18"
item.properties["ml-model:training-processor-type"] = "cpu"
item.properties["ml-model:training-os"] = "linux"
```


```python
# Add "mlm-ext" properties
item.properties["mlm:name"] = "Tile-Based Classifier"
item.properties["mlm:architecture"] = "RandomForestClassifier"
item.properties["mlm:framework"] = "tensorflow"
item.properties["mlm:framework_version"] = "1.4.2"
item.properties["mlm:tasks"] = ["classification"]
item.properties["mlm:compiled"] = False
item.properties["mlm:accelerator"] = "amd64"
item.properties["mlm:accelerator_constrained"] = False

# Add hyperparameters
item.properties["mlm:hyperparameters"] = {
    "learning_rate": 0.001,  # Example value
    "batch_size": 32,  # Example value
    "number_of_epochs": 50,  # Example value
    "optimizer": "adam",  # Example value
    "momentum": 0.9,  # Example value
    "dropout_rate": 0.5,  # Example value
    "number_of_convolutional_layers": 3,  # Example value
    "filter_size": "3x3",  # Example value
    "number_of_filters": 64,  # Example value
    "activation_function": "relu",  # Example value
    "pooling_layers": "max",  # Example value
    "learning_rate_scheduler": "step_decay",  # Example value
    "l2_regularization": 1e-4,  # Example value
}

item.properties
```




    {'datetime': '2025-04-04T12:30:39.002998Z',
     'start_datetime': '2023-06-13T00:00:00Z',
     'end_datetime': '2023-06-18T23:59:59Z',
     'description': 'Tile based classifier using CNNs for land cover classification. \n    The model is trained on the Sentinel-2 dataset and is capable of classifying \n    land cover types such as water, forest, urban, and agriculture. \n    The model is designed to work with Sentinel-2 imagery and can be used for ',
     'ml-model:type': 'ml-model',
     'ml-model:learning_approach': 'supervised',
     'ml-model:prediction_type': 'classification',
     'ml-model:architecture': 'ResNet-18',
     'ml-model:training-processor-type': 'cpu',
     'ml-model:training-os': 'linux',
     'mlm:name': 'Tile-Based Classifier',
     'mlm:architecture': 'RandomForestClassifier',
     'mlm:framework': 'tensorflow',
     'mlm:framework_version': '1.4.2',
     'mlm:tasks': ['classification'],
     'mlm:compiled': False,
     'mlm:accelerator': 'amd64',
     'mlm:accelerator_constrained': False,
     'mlm:hyperparameters': {'learning_rate': 0.001,
      'batch_size': 32,
      'number_of_epochs': 50,
      'optimizer': 'adam',
      'momentum': 0.9,
      'dropout_rate': 0.5,
      'number_of_convolutional_layers': 3,
      'filter_size': '3x3',
      'number_of_filters': 64,
      'activation_function': 'relu',
      'pooling_layers': 'max',
      'learning_rate_scheduler': 'step_decay',
      'l2_regularization': 0.0001}}



### Model inputs

The properties of model inputs can be populated in the cell below


```python
# Add input and output to the properties
item.properties["mlm:input"] = [
    {
        "name": "EO Data",
        "bands": [
            "B01",
            "B02",
            "B03",
            "B04",
            "B05",
            "B06",
            "B07",
            "B08",
            "B8A",
            "B09",
            "B10",
            "B11",
            "B12",
        ],
        "input": {
            "shape": [-1, 3, 64, 64],
            "dim_order": ["batch", "channel", "height", "width"],
            "data_type": "float32",
        },
        "norm_type": "z-score",
    }
]
```

### Model outputs


```python
class_map = {
    "Annual Crop": 0,
    "Forest": 1,
    "Herbaceous Vegetation": 2,
    "Highway": 3,
    "Industrial Buildings": 4,
    "Pasture": 5,
    "Permanent Crop": 6,
    "Residential Buildings": 7,
    "River": 8,
    "SeaLake": 9,
}

color_map = {
    0: (34, 139, 34, 255),  # AnnualCrop: Forest Green
    1: (0, 100, 0, 255),  # Forest: Dark Green
    2: (144, 238, 144, 255),  # HerbaceousVegetation: Light Green
    3: (128, 128, 128, 255),  # Highway: Gray
    4: (169, 169, 169, 255),  # Industrial: Dark Gray
    5: (85, 107, 47, 255),  # Pasture: Olive Green
    6: (60, 179, 113, 255),  # PermanentCrop: Medium Sea Green
    7: (139, 69, 19, 255),  # Residential: Saddle Brown
    8: (30, 144, 255, 255),  # River: Dodger Blue
    9: (0, 0, 255, 255),  # SeaLake: Blue
}

tmp_dict = []

for class_name, id in class_map.items():
    color = color_map[id]
    # Convert RGB to hex (without the alpha value)
    hex_color = "#{:02X}{:02X}{:02X}".format(color[0], color[1], color[2])
    
    tmp_dict.append({
        "name": class_name,
        "value": id,
        "description": f"{class_name} tile",
        "color_hint": hex_color.lower()[1:]  # Remove the "#" and convert to lowercase
    })
item.properties["mlm:output"] = [
    {
        "name": "CLASSIFICATION",
        "tasks": ["segmentation", "semantic-segmentation"],
        "result": {
            "shape": [-1, 10980, 10980],
            "dim_order": ["batch", "height", "width"],
            "data_type": "uint8",
        },
        "post_processing_function": None,
        "classification:classes": tmp_dict
    }
]

item
```






<style>
.pystac-summary {
    cursor: pointer;
    display: list-item;
    list-style: revert;
    margin-bottom: 0 !important;

    .pystac-l {
        padding-left: 0.5em;
        color: rgb(64, 128, 128);
        font-style: italic;
    }
}
.pystac-row {
    overflow-wrap: break-word;
    padding-left: .825em;

    .pystac-k {
        display: inline-block;
        margin: 0px 0.5em 0px 0px;
    }
    .pystac-v {
        color: rgb(186, 33, 33);
    }
}
.pystac-k {
    color: rgb(0, 128, 0);
    font-weight: 700;
}
</style>
<div class="jp-RenderedJSON jp-mod-trusted jp-OutputArea-output">
    <div class="container" style="line-height: normal;">
        <ul style="padding: 0px; margin: 0px; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"Feature"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">stac_version</span>
            <span class="pystac-v">"1.1.0"</span>
        </li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">stac_extensions</span><span class="pystac-l">[] 0 items</span></summary>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">id</span>
            <span class="pystac-v">"Tile-based-ML-Models"</span>
        </li>





        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">geometry</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"Polygon"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">coordinates</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">0</span><span class="pystac-l">[] 5 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">0</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">1</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-120.06532070709298</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">2</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-120.06532070709298</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">38.84330548198025</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">3</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">38.84330548198025</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">4</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

    </details></li>


    </ul>

    </details></li>


    </ul>

    </details></li>


    </ul>
        </details></li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">bbox</span><span class="pystac-l">[] 4 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">-120.06532070709298</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">3</span>
            <span class="pystac-v">38.84330548198025</span>
        </li>



    </ul>

    </details></li>




        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">properties</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">datetime</span>
            <span class="pystac-v">"2025-04-04T12:30:39.002998Z"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">start_datetime</span>
            <span class="pystac-v">"2023-06-13T00:00:00Z"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">end_datetime</span>
            <span class="pystac-v">"2023-06-18T23:59:59Z"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Tile based classifier using CNNs for land cover classification. 
    The model is trained on the Sentinel-2 dataset and is capable of classifying 
    land cover types such as water, forest, urban, and agriculture. 
    The model is designed to work with Sentinel-2 imagery and can be used for "</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">ml-model:type</span>
            <span class="pystac-v">"ml-model"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">ml-model:learning_approach</span>
            <span class="pystac-v">"supervised"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">ml-model:prediction_type</span>
            <span class="pystac-v">"classification"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">ml-model:architecture</span>
            <span class="pystac-v">"ResNet-18"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">ml-model:training-processor-type</span>
            <span class="pystac-v">"cpu"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">ml-model:training-os</span>
            <span class="pystac-v">"linux"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">mlm:name</span>
            <span class="pystac-v">"Tile-Based Classifier"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">mlm:architecture</span>
            <span class="pystac-v">"RandomForestClassifier"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">mlm:framework</span>
            <span class="pystac-v">"tensorflow"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">mlm:framework_version</span>
            <span class="pystac-v">"1.4.2"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">mlm:tasks</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"classification"</span>
        </li>



    </ul>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">mlm:compiled</span>
            <span class="pystac-v">False</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">mlm:accelerator</span>
            <span class="pystac-v">"amd64"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">mlm:accelerator_constrained</span>
            <span class="pystac-v">False</span>
        </li>





        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">mlm:hyperparameters</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">learning_rate</span>
            <span class="pystac-v">0.001</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">batch_size</span>
            <span class="pystac-v">32</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">number_of_epochs</span>
            <span class="pystac-v">50</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">optimizer</span>
            <span class="pystac-v">"adam"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">momentum</span>
            <span class="pystac-v">0.9</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">dropout_rate</span>
            <span class="pystac-v">0.5</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">number_of_convolutional_layers</span>
            <span class="pystac-v">3</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">filter_size</span>
            <span class="pystac-v">"3x3"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">number_of_filters</span>
            <span class="pystac-v">64</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">activation_function</span>
            <span class="pystac-v">"relu"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">pooling_layers</span>
            <span class="pystac-v">"max"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">learning_rate_scheduler</span>
            <span class="pystac-v">"step_decay"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">l2_regularization</span>
            <span class="pystac-v">0.0001</span>
        </li>



    </ul>
        </details></li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">mlm:input</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">0</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"EO Data"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">bands</span><span class="pystac-l">[] 13 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"B01"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">"B02"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">"B03"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">3</span>
            <span class="pystac-v">"B04"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">4</span>
            <span class="pystac-v">"B05"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">5</span>
            <span class="pystac-v">"B06"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">6</span>
            <span class="pystac-v">"B07"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">7</span>
            <span class="pystac-v">"B08"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">8</span>
            <span class="pystac-v">"B8A"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">9</span>
            <span class="pystac-v">"B09"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">10</span>
            <span class="pystac-v">"B10"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">11</span>
            <span class="pystac-v">"B11"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">12</span>
            <span class="pystac-v">"B12"</span>
        </li>



    </ul>

    </details></li>




        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">input</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">shape</span><span class="pystac-l">[] 4 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-1</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">3</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">64</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">3</span>
            <span class="pystac-v">64</span>
        </li>



    </ul>

    </details></li>



                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">dim_order</span><span class="pystac-l">[] 4 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"batch"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">"channel"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">"height"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">3</span>
            <span class="pystac-v">"width"</span>
        </li>



    </ul>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">data_type</span>
            <span class="pystac-v">"float32"</span>
        </li>



    </ul>
        </details></li>





        <li class="pystac-row">
            <span class="pystac-k">norm_type</span>
            <span class="pystac-v">"z-score"</span>
        </li>



    </ul>
        </details></li>



    </ul>

    </details></li>



                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">mlm:output</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">0</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"CLASSIFICATION"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">tasks</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"segmentation"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">"semantic-segmentation"</span>
        </li>



    </ul>

    </details></li>




        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">result</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">shape</span><span class="pystac-l">[] 3 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-1</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">10980</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">10980</span>
        </li>



    </ul>

    </details></li>



                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">dim_order</span><span class="pystac-l">[] 3 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"batch"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">"height"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">"width"</span>
        </li>



    </ul>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">data_type</span>
            <span class="pystac-v">"uint8"</span>
        </li>



    </ul>
        </details></li>





        <li class="pystac-row">
            <span class="pystac-k">post_processing_function</span>
            <span class="pystac-v">None</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">classification:classes</span><span class="pystac-l">[] 10 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">0</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Annual Crop"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Annual Crop tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"228b22"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">1</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Forest"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">1</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Forest tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"006400"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">2</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Herbaceous Vegetation"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">2</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Herbaceous Vegetation tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"90ee90"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">3</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Highway"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">3</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Highway tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"808080"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">4</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Industrial Buildings"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">4</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Industrial Buildings tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"a9a9a9"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">5</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Pasture"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">5</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Pasture tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"556b2f"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">6</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Permanent Crop"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">6</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Permanent Crop tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"3cb371"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">7</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Residential Buildings"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">7</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Residential Buildings tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"8b4513"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">8</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"River"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">8</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"River tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"1e90ff"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">9</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"SeaLake"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">9</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"SeaLake tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"0000ff"</span>
        </li>



    </ul>
        </details></li>



    </ul>

    </details></li>


    </ul>
        </details></li>



    </ul>

    </details></li>


    </ul>
        </details></li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">links</span><span class="pystac-l">[] 0 items</span></summary>

    </details></li>




        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">assets</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">

    </ul>
        </details></li>



        </ul>
    </div>
</div>



The user will add Raster bands to the Item's properties


```python
# Add "raster:bands" properties
def add_prop_RasterBands(name, cname, nd, dt, bps, res, scale, offset, unit):
    return {
        "name": name,
        "common_name": cname,
        "nodata": nd,
        "data_type": dt,
        "bits_per_sample": bps,
        "spatial_resolution": res,
        "scale": scale,
        "offset": offset,
        "unit": unit,
    }


def add_prop_RasterBands_Expression(name, cname, nd, dt, exp):
    return {
        "name": name,
        "common_name": cname,
        "nodata": nd,
        "data_type": dt,
        "processing:expression": exp,
    }


item.properties["raster:bands"] = [
    add_prop_RasterBands(
        name="B01",
        cname="coastal",
        nd=0,
        dt="float32",
        bps=15,
        res=60,
        scale=0.0001,
        offset=0,
        unit="m",
    ),
    add_prop_RasterBands(
        name="B02",
        cname="blue",
        nd=0,
        dt="float32",
        bps=15,
        res=10,
        scale=0.0001,
        offset=0,
        unit="m",
    ),
    add_prop_RasterBands(
        name="B03",
        cname="green",
        nd=0,
        dt="float32",
        bps=15,
        res=10,
        scale=0.0001,
        offset=0,
        unit="m",
    ),
    add_prop_RasterBands(
        name="B04",
        cname="red",
        nd=0,
        dt="float32",
        bps=15,
        res=10,
        scale=0.0001,
        offset=0,
        unit="m",
    ),
    add_prop_RasterBands(
        name="B08",
        cname="nir",
        nd=0,
        dt="float32",
        bps=15,
        res=10,
        scale=0.0001,
        offset=0,
        unit="m",
    ),
    add_prop_RasterBands(
        name="B8A",
        cname="nir08",
        nd=0,
        dt="float32",
        bps=15,
        res=20,
        scale=0.0001,
        offset=0,
        unit="m",
    ),
    add_prop_RasterBands(
        name="B09",
        cname="nir09",
        nd=0,
        dt="float32",
        bps=15,
        res=60,
        scale=0.0001,
        offset=0,
        unit="m",
    ),
    add_prop_RasterBands(
        name="B11",
        cname="swir16",
        nd=0,
        dt="float32",
        bps=15,
        res=20,
        scale=0.0001,
        offset=0,
        unit="m",
    ),
    add_prop_RasterBands(
        name="B12",
        cname="swir22",
        nd=0,
        dt="float32",
        bps=15,
        res=20,
        scale=0.0001,
        offset=0,
        unit="m",
    ),
]


# Display
item.properties["raster:bands"]
```




    [{'name': 'B01',
      'common_name': 'coastal',
      'nodata': 0,
      'data_type': 'float32',
      'bits_per_sample': 15,
      'spatial_resolution': 60,
      'scale': 0.0001,
      'offset': 0,
      'unit': 'm'},
     {'name': 'B02',
      'common_name': 'blue',
      'nodata': 0,
      'data_type': 'float32',
      'bits_per_sample': 15,
      'spatial_resolution': 10,
      'scale': 0.0001,
      'offset': 0,
      'unit': 'm'},
     {'name': 'B03',
      'common_name': 'green',
      'nodata': 0,
      'data_type': 'float32',
      'bits_per_sample': 15,
      'spatial_resolution': 10,
      'scale': 0.0001,
      'offset': 0,
      'unit': 'm'},
     {'name': 'B04',
      'common_name': 'red',
      'nodata': 0,
      'data_type': 'float32',
      'bits_per_sample': 15,
      'spatial_resolution': 10,
      'scale': 0.0001,
      'offset': 0,
      'unit': 'm'},
     {'name': 'B08',
      'common_name': 'nir',
      'nodata': 0,
      'data_type': 'float32',
      'bits_per_sample': 15,
      'spatial_resolution': 10,
      'scale': 0.0001,
      'offset': 0,
      'unit': 'm'},
     {'name': 'B8A',
      'common_name': 'nir08',
      'nodata': 0,
      'data_type': 'float32',
      'bits_per_sample': 15,
      'spatial_resolution': 20,
      'scale': 0.0001,
      'offset': 0,
      'unit': 'm'},
     {'name': 'B09',
      'common_name': 'nir09',
      'nodata': 0,
      'data_type': 'float32',
      'bits_per_sample': 15,
      'spatial_resolution': 60,
      'scale': 0.0001,
      'offset': 0,
      'unit': 'm'},
     {'name': 'B11',
      'common_name': 'swir16',
      'nodata': 0,
      'data_type': 'float32',
      'bits_per_sample': 15,
      'spatial_resolution': 20,
      'scale': 0.0001,
      'offset': 0,
      'unit': 'm'},
     {'name': 'B12',
      'common_name': 'swir22',
      'nodata': 0,
      'data_type': 'float32',
      'bits_per_sample': 15,
      'spatial_resolution': 20,
      'scale': 0.0001,
      'offset': 0,
      'unit': 'm'}]




```python
# Add Assets - ML Training
app_version = "0.0.2"
asset = pystac.Asset(
    title="Workflow for tile-based training",
    href=f"https://github.com/parham-membari-terradue/machine-learning-process/releases/download/{app_version}/tile-sat-training.{app_version}.cwl",
    media_type="application/cwl+yaml",
    roles=["ml-model:training-runtime", "runtime", "mlm:training-runtime"],
)
item.add_asset("tile-based-training", asset)

# Add Assets - Inference
asset = pystac.Asset(
    title="Workflow for tile-based inference",
    href=f"https://github.com/parham-membari-terradue/machine-learning-process/releases/download/{app_version}/tile-sat-inference.{app_version}.cwl",
    media_type="application/cwl+yaml",
    roles=["ml-model:inference-runtime", "runtime", "mlm:inference-runtime"],
)
item.add_asset("tile-based-inference", asset)

# Add Asset - ML model
asset = pystac.Asset(
    title="ONNX Model",
    href="https://github.com/parham-membari-terradue/machine-learning-process/blob/main/inference/make-inference/src/make_inference/model/model.onnx",
    media_type="application/octet-stream; framework=onnx; profile=onnx",
    roles=["mlm:model"],
)
item.add_asset("model", asset)

item.assets
```




    {'tile-based-training': <Asset href=https://github.com/parham-membari-terradue/machine-learning-process/releases/download/0.0.2/tile-sat-training.0.0.2.cwl>,
     'tile-based-inference': <Asset href=https://github.com/parham-membari-terradue/machine-learning-process/releases/download/0.0.2/tile-sat-inference.0.0.2.cwl>,
     'model': <Asset href=https://github.com/parham-membari-terradue/machine-learning-process/blob/main/inference/make-inference/src/make_inference/model/model.onnx>}




```python
# Add links
rel_path = f"./{SUB_DIR}/{item.id}/{item.id}.json"
item.set_self_href(rel_path)
item.links
```




    [<Link rel=self target=/home/t2/Desktop/p/argo/machine-learning-process/MLM/ML_Catalog/ML-Models_EO/Tile-based-ML-Models/Tile-based-ML-Models.json>]



In addition to the `EO` STAC Extension, the user can add the ["ML Model" STAC Extension](https://github.com/stac-extensions/ml-model) (`ml-model`) in the STAC Item. 

There is an upcoming extension for ML models that is under development, which will allow to store more details and information related to the ML model: ["Machine Learning Model" STAC Extension](https://pypi.org/project/stac-model/0.1.1a3/) (`mlm`). 


```python
# Add Extensions
EOExtension.ext(item, add_if_missing=True)

# Add the extension to the item and set the schema URL
if not any("ml-model" in url for url in item.stac_extensions):
    item.stac_extensions.append(
        "https://stac-extensions.github.io/ml-model/v1.0.0/schema.json"
    )
if not any("mlm-extension" in url for url in item.stac_extensions):
    item.stac_extensions.append(
        "https://crim-ca.github.io/mlm-extension/v1.2.0/schema.json"
    )
if not any("raster" in url for url in item.stac_extensions):
    item.stac_extensions.append(
        "https://stac-extensions.github.io/raster/v1.1.0/schema.json"
    )
if not any("file" in url for url in item.stac_extensions):
    item.stac_extensions.append(
        "https://stac-extensions.github.io/file/v2.1.0/schema.json"
    )
item.stac_extensions
```




    ['https://stac-extensions.github.io/eo/v1.1.0/schema.json',
     'https://stac-extensions.github.io/ml-model/v1.0.0/schema.json',
     'https://crim-ca.github.io/mlm-extension/v1.2.0/schema.json',
     'https://stac-extensions.github.io/raster/v1.1.0/schema.json',
     'https://stac-extensions.github.io/file/v2.1.0/schema.json']




```python
item
```






<style>
.pystac-summary {
    cursor: pointer;
    display: list-item;
    list-style: revert;
    margin-bottom: 0 !important;

    .pystac-l {
        padding-left: 0.5em;
        color: rgb(64, 128, 128);
        font-style: italic;
    }
}
.pystac-row {
    overflow-wrap: break-word;
    padding-left: .825em;

    .pystac-k {
        display: inline-block;
        margin: 0px 0.5em 0px 0px;
    }
    .pystac-v {
        color: rgb(186, 33, 33);
    }
}
.pystac-k {
    color: rgb(0, 128, 0);
    font-weight: 700;
}
</style>
<div class="jp-RenderedJSON jp-mod-trusted jp-OutputArea-output">
    <div class="container" style="line-height: normal;">
        <ul style="padding: 0px; margin: 0px; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"Feature"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">stac_version</span>
            <span class="pystac-v">"1.1.0"</span>
        </li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">stac_extensions</span><span class="pystac-l">[] 5 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"https://stac-extensions.github.io/eo/v1.1.0/schema.json"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">"https://stac-extensions.github.io/ml-model/v1.0.0/schema.json"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">"https://crim-ca.github.io/mlm-extension/v1.2.0/schema.json"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">3</span>
            <span class="pystac-v">"https://stac-extensions.github.io/raster/v1.1.0/schema.json"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">4</span>
            <span class="pystac-v">"https://stac-extensions.github.io/file/v2.1.0/schema.json"</span>
        </li>



    </ul>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">id</span>
            <span class="pystac-v">"Tile-based-ML-Models"</span>
        </li>





        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">geometry</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"Polygon"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">coordinates</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">0</span><span class="pystac-l">[] 5 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">0</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">1</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-120.06532070709298</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">2</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-120.06532070709298</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">38.84330548198025</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">3</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">38.84330548198025</span>
        </li>



    </ul>

    </details></li>


    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">4</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

    </details></li>


    </ul>

    </details></li>


    </ul>

    </details></li>


    </ul>
        </details></li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">bbox</span><span class="pystac-l">[] 4 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-121.87680832296513</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">36.93063805399626</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">-120.06532070709298</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">3</span>
            <span class="pystac-v">38.84330548198025</span>
        </li>



    </ul>

    </details></li>




        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">properties</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">datetime</span>
            <span class="pystac-v">"2025-04-04T12:30:39.002998Z"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">start_datetime</span>
            <span class="pystac-v">"2023-06-13T00:00:00Z"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">end_datetime</span>
            <span class="pystac-v">"2023-06-18T23:59:59Z"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Tile based classifier using CNNs for land cover classification. 
    The model is trained on the Sentinel-2 dataset and is capable of classifying 
    land cover types such as water, forest, urban, and agriculture. 
    The model is designed to work with Sentinel-2 imagery and can be used for "</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">ml-model:type</span>
            <span class="pystac-v">"ml-model"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">ml-model:learning_approach</span>
            <span class="pystac-v">"supervised"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">ml-model:prediction_type</span>
            <span class="pystac-v">"classification"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">ml-model:architecture</span>
            <span class="pystac-v">"ResNet-18"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">ml-model:training-processor-type</span>
            <span class="pystac-v">"cpu"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">ml-model:training-os</span>
            <span class="pystac-v">"linux"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">mlm:name</span>
            <span class="pystac-v">"Tile-Based Classifier"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">mlm:architecture</span>
            <span class="pystac-v">"RandomForestClassifier"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">mlm:framework</span>
            <span class="pystac-v">"tensorflow"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">mlm:framework_version</span>
            <span class="pystac-v">"1.4.2"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">mlm:tasks</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"classification"</span>
        </li>



    </ul>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">mlm:compiled</span>
            <span class="pystac-v">False</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">mlm:accelerator</span>
            <span class="pystac-v">"amd64"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">mlm:accelerator_constrained</span>
            <span class="pystac-v">False</span>
        </li>





        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">mlm:hyperparameters</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">learning_rate</span>
            <span class="pystac-v">0.001</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">batch_size</span>
            <span class="pystac-v">32</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">number_of_epochs</span>
            <span class="pystac-v">50</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">optimizer</span>
            <span class="pystac-v">"adam"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">momentum</span>
            <span class="pystac-v">0.9</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">dropout_rate</span>
            <span class="pystac-v">0.5</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">number_of_convolutional_layers</span>
            <span class="pystac-v">3</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">filter_size</span>
            <span class="pystac-v">"3x3"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">number_of_filters</span>
            <span class="pystac-v">64</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">activation_function</span>
            <span class="pystac-v">"relu"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">pooling_layers</span>
            <span class="pystac-v">"max"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">learning_rate_scheduler</span>
            <span class="pystac-v">"step_decay"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">l2_regularization</span>
            <span class="pystac-v">0.0001</span>
        </li>



    </ul>
        </details></li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">mlm:input</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">0</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"EO Data"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">bands</span><span class="pystac-l">[] 13 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"B01"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">"B02"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">"B03"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">3</span>
            <span class="pystac-v">"B04"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">4</span>
            <span class="pystac-v">"B05"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">5</span>
            <span class="pystac-v">"B06"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">6</span>
            <span class="pystac-v">"B07"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">7</span>
            <span class="pystac-v">"B08"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">8</span>
            <span class="pystac-v">"B8A"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">9</span>
            <span class="pystac-v">"B09"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">10</span>
            <span class="pystac-v">"B10"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">11</span>
            <span class="pystac-v">"B11"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">12</span>
            <span class="pystac-v">"B12"</span>
        </li>



    </ul>

    </details></li>




        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">input</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">shape</span><span class="pystac-l">[] 4 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-1</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">3</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">64</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">3</span>
            <span class="pystac-v">64</span>
        </li>



    </ul>

    </details></li>



                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">dim_order</span><span class="pystac-l">[] 4 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"batch"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">"channel"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">"height"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">3</span>
            <span class="pystac-v">"width"</span>
        </li>



    </ul>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">data_type</span>
            <span class="pystac-v">"float32"</span>
        </li>



    </ul>
        </details></li>





        <li class="pystac-row">
            <span class="pystac-k">norm_type</span>
            <span class="pystac-v">"z-score"</span>
        </li>



    </ul>
        </details></li>



    </ul>

    </details></li>



                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">mlm:output</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">0</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"CLASSIFICATION"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">tasks</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"segmentation"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">"semantic-segmentation"</span>
        </li>



    </ul>

    </details></li>




        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">result</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">shape</span><span class="pystac-l">[] 3 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-1</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">10980</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">10980</span>
        </li>



    </ul>

    </details></li>



                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">dim_order</span><span class="pystac-l">[] 3 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"batch"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">"height"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">"width"</span>
        </li>



    </ul>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">data_type</span>
            <span class="pystac-v">"uint8"</span>
        </li>



    </ul>
        </details></li>





        <li class="pystac-row">
            <span class="pystac-k">post_processing_function</span>
            <span class="pystac-v">None</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">classification:classes</span><span class="pystac-l">[] 10 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">0</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Annual Crop"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Annual Crop tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"228b22"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">1</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Forest"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">1</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Forest tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"006400"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">2</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Herbaceous Vegetation"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">2</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Herbaceous Vegetation tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"90ee90"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">3</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Highway"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">3</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Highway tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"808080"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">4</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Industrial Buildings"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">4</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Industrial Buildings tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"a9a9a9"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">5</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Pasture"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">5</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Pasture tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"556b2f"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">6</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Permanent Crop"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">6</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Permanent Crop tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"3cb371"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">7</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"Residential Buildings"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">7</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"Residential Buildings tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"8b4513"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">8</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"River"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">8</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"River tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"1e90ff"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">9</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"SeaLake"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">value</span>
            <span class="pystac-v">9</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"SeaLake tile"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">color_hint</span>
            <span class="pystac-v">"0000ff"</span>
        </li>



    </ul>
        </details></li>



    </ul>

    </details></li>


    </ul>
        </details></li>



    </ul>

    </details></li>



                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">raster:bands</span><span class="pystac-l">[] 9 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">0</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"B01"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">common_name</span>
            <span class="pystac-v">"coastal"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">nodata</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">data_type</span>
            <span class="pystac-v">"float32"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">bits_per_sample</span>
            <span class="pystac-v">15</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">spatial_resolution</span>
            <span class="pystac-v">60</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">scale</span>
            <span class="pystac-v">0.0001</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">offset</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">unit</span>
            <span class="pystac-v">"m"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">1</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"B02"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">common_name</span>
            <span class="pystac-v">"blue"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">nodata</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">data_type</span>
            <span class="pystac-v">"float32"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">bits_per_sample</span>
            <span class="pystac-v">15</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">spatial_resolution</span>
            <span class="pystac-v">10</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">scale</span>
            <span class="pystac-v">0.0001</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">offset</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">unit</span>
            <span class="pystac-v">"m"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">2</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"B03"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">common_name</span>
            <span class="pystac-v">"green"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">nodata</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">data_type</span>
            <span class="pystac-v">"float32"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">bits_per_sample</span>
            <span class="pystac-v">15</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">spatial_resolution</span>
            <span class="pystac-v">10</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">scale</span>
            <span class="pystac-v">0.0001</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">offset</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">unit</span>
            <span class="pystac-v">"m"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">3</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"B04"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">common_name</span>
            <span class="pystac-v">"red"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">nodata</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">data_type</span>
            <span class="pystac-v">"float32"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">bits_per_sample</span>
            <span class="pystac-v">15</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">spatial_resolution</span>
            <span class="pystac-v">10</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">scale</span>
            <span class="pystac-v">0.0001</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">offset</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">unit</span>
            <span class="pystac-v">"m"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">4</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"B08"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">common_name</span>
            <span class="pystac-v">"nir"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">nodata</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">data_type</span>
            <span class="pystac-v">"float32"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">bits_per_sample</span>
            <span class="pystac-v">15</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">spatial_resolution</span>
            <span class="pystac-v">10</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">scale</span>
            <span class="pystac-v">0.0001</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">offset</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">unit</span>
            <span class="pystac-v">"m"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">5</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"B8A"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">common_name</span>
            <span class="pystac-v">"nir08"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">nodata</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">data_type</span>
            <span class="pystac-v">"float32"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">bits_per_sample</span>
            <span class="pystac-v">15</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">spatial_resolution</span>
            <span class="pystac-v">20</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">scale</span>
            <span class="pystac-v">0.0001</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">offset</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">unit</span>
            <span class="pystac-v">"m"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">6</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"B09"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">common_name</span>
            <span class="pystac-v">"nir09"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">nodata</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">data_type</span>
            <span class="pystac-v">"float32"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">bits_per_sample</span>
            <span class="pystac-v">15</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">spatial_resolution</span>
            <span class="pystac-v">60</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">scale</span>
            <span class="pystac-v">0.0001</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">offset</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">unit</span>
            <span class="pystac-v">"m"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">7</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"B11"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">common_name</span>
            <span class="pystac-v">"swir16"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">nodata</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">data_type</span>
            <span class="pystac-v">"float32"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">bits_per_sample</span>
            <span class="pystac-v">15</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">spatial_resolution</span>
            <span class="pystac-v">20</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">scale</span>
            <span class="pystac-v">0.0001</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">offset</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">unit</span>
            <span class="pystac-v">"m"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">8</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"B12"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">common_name</span>
            <span class="pystac-v">"swir22"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">nodata</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">data_type</span>
            <span class="pystac-v">"float32"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">bits_per_sample</span>
            <span class="pystac-v">15</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">spatial_resolution</span>
            <span class="pystac-v">20</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">scale</span>
            <span class="pystac-v">0.0001</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">offset</span>
            <span class="pystac-v">0</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">unit</span>
            <span class="pystac-v">"m"</span>
        </li>



    </ul>
        </details></li>



    </ul>

    </details></li>


    </ul>
        </details></li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">links</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">0</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">rel</span>
            <span class="pystac-v">"self"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">href</span>
            <span class="pystac-v">"/home/t2/Desktop/p/argo/machine-learning-process/MLM/ML_Catalog/ML-Models_EO/Tile-based-ML-Models/Tile-based-ML-Models.json"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"application/json"</span>
        </li>



    </ul>
        </details></li>



    </ul>

    </details></li>




        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">assets</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">tile-based-training</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">href</span>
            <span class="pystac-v">"https://github.com/parham-membari-terradue/machine-learning-process/releases/download/0.0.2/tile-sat-training.0.0.2.cwl"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"application/cwl+yaml"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">title</span>
            <span class="pystac-v">"Workflow for tile-based training"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">roles</span><span class="pystac-l">[] 3 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"ml-model:training-runtime"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">"runtime"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">"mlm:training-runtime"</span>
        </li>



    </ul>

    </details></li>


    </ul>
        </details></li>





        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">tile-based-inference</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">href</span>
            <span class="pystac-v">"https://github.com/parham-membari-terradue/machine-learning-process/releases/download/0.0.2/tile-sat-inference.0.0.2.cwl"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"application/cwl+yaml"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">title</span>
            <span class="pystac-v">"Workflow for tile-based inference"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">roles</span><span class="pystac-l">[] 3 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"ml-model:inference-runtime"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">"runtime"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">"mlm:inference-runtime"</span>
        </li>



    </ul>

    </details></li>


    </ul>
        </details></li>





        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">model</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">href</span>
            <span class="pystac-v">"https://github.com/parham-membari-terradue/machine-learning-process/blob/main/inference/make-inference/src/make_inference/model/model.onnx"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"application/octet-stream; framework=onnx; profile=onnx"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">title</span>
            <span class="pystac-v">"ONNX Model"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">roles</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"mlm:model"</span>
        </li>



    </ul>

    </details></li>


    </ul>
        </details></li>



    </ul>
        </details></li>



        </ul>
    </div>
</div>




```python
# Validate STAC Item
item.validate()
```




    ['https://schemas.stacspec.org/v1.1.0/item-spec/json-schema/item.json',
     'https://stac-extensions.github.io/eo/v1.1.0/schema.json',
     'https://stac-extensions.github.io/ml-model/v1.0.0/schema.json',
     'https://crim-ca.github.io/mlm-extension/v1.2.0/schema.json',
     'https://stac-extensions.github.io/raster/v1.1.0/schema.json',
     'https://stac-extensions.github.io/file/v2.1.0/schema.json']



### 2.3) STAC Objects 
#### STAC Catalog
Check if a `catalog.json` exists already. If not, create it, otherwise read existing catalog and add STAC Item to it.


```python
cat_path = os.path.join(CATALOG_DIR, "catalog.json")

if not os.path.exists(cat_path):
    # Catalog does not exist - create it
    print("Catalog does not exist. Creating it")

    catalog = pystac.Catalog(
        id="ML-Model_EO", description="A catalog to describe ML models", title="ML Models"
    )
else:
    # Read Catalog and add the STAC Item to it
    print("Catalog exists already. Reading it")

    catalog = pystac.read_file(cat_path)
catalog.validate()
catalog
```

    Catalog does not exist. Creating it







<style>
.pystac-summary {
    cursor: pointer;
    display: list-item;
    list-style: revert;
    margin-bottom: 0 !important;

    .pystac-l {
        padding-left: 0.5em;
        color: rgb(64, 128, 128);
        font-style: italic;
    }
}
.pystac-row {
    overflow-wrap: break-word;
    padding-left: .825em;

    .pystac-k {
        display: inline-block;
        margin: 0px 0.5em 0px 0px;
    }
    .pystac-v {
        color: rgb(186, 33, 33);
    }
}
.pystac-k {
    color: rgb(0, 128, 0);
    font-weight: 700;
}
</style>
<div class="jp-RenderedJSON jp-mod-trusted jp-OutputArea-output">
    <div class="container" style="line-height: normal;">
        <ul style="padding: 0px; margin: 0px; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"Catalog"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">id</span>
            <span class="pystac-v">"ML-Model_EO"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">stac_version</span>
            <span class="pystac-v">"1.1.0"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"A catalog to describe ML models"</span>
        </li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">links</span><span class="pystac-l">[] 0 items</span></summary>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">title</span>
            <span class="pystac-v">"ML Models"</span>
        </li>



        </ul>
    </div>
</div>



#### STAC Collection
Check if a `collection.json` exists already. If not, create it, otherwise read existing collection and add STAC Item to it.


```python
coll_path = os.path.join(CATALOG_DIR, COLLECTION_NAME, "collection.json")

if not os.path.exists(coll_path):
    # Collection does not exist - create it
    print("Collection does not exist. Creating it")

    # Spatial extent
    bbox_world = [-180, -90, 180, 90]
    # Define temporal extent
    start_date = "2015-06-27T00:00:01.000000+00:00"
    end_date = None  # "2024-04-29T13:23:32.741484+00:00"

    collection = pystac.Collection(
        id=COLLECTION_NAME,
        description="A collection for ML Models",
        extent=pystac.Extent(
            spatial=pystac.SpatialExtent(bbox_world),
            temporal=getTemporalExtent(start_date, end_date),
        ),
        title=COLLECTION_NAME,
        license="proprietary",
        keywords=[],
        providers=[
            pystac.Provider(
                name="AI-Extensions Project",
                roles=["producer"],
                url="https://ai-extensions.github.io/docs",
            )
        ],
    )

else:
    # Read Collection and add the STAC Item to it
    print("Collection exists already. Reading it")

    collection = read_file(coll_path)

collection

```

    Collection does not exist. Creating it







<style>
.pystac-summary {
    cursor: pointer;
    display: list-item;
    list-style: revert;
    margin-bottom: 0 !important;

    .pystac-l {
        padding-left: 0.5em;
        color: rgb(64, 128, 128);
        font-style: italic;
    }
}
.pystac-row {
    overflow-wrap: break-word;
    padding-left: .825em;

    .pystac-k {
        display: inline-block;
        margin: 0px 0.5em 0px 0px;
    }
    .pystac-v {
        color: rgb(186, 33, 33);
    }
}
.pystac-k {
    color: rgb(0, 128, 0);
    font-weight: 700;
}
</style>
<div class="jp-RenderedJSON jp-mod-trusted jp-OutputArea-output">
    <div class="container" style="line-height: normal;">
        <ul style="padding: 0px; margin: 0px; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"Collection"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">id</span>
            <span class="pystac-v">"ML-Models_EO"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">stac_version</span>
            <span class="pystac-v">"1.1.0"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"A collection for ML Models"</span>
        </li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">links</span><span class="pystac-l">[] 0 items</span></summary>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">title</span>
            <span class="pystac-v">"ML-Models_EO"</span>
        </li>





        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">extent</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">spatial</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">bbox</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">0</span><span class="pystac-l">[] 4 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-180</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">-90</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">180</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">3</span>
            <span class="pystac-v">90</span>
        </li>



    </ul>

    </details></li>


    </ul>

    </details></li>


    </ul>
        </details></li>





        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">temporal</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">interval</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">0</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"2015-06-27T00:00:01Z"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">None</span>
        </li>



    </ul>

    </details></li>


    </ul>

    </details></li>


    </ul>
        </details></li>



    </ul>
        </details></li>





        <li class="pystac-row">
            <span class="pystac-k">license</span>
            <span class="pystac-v">"proprietary"</span>
        </li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">providers</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">0</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"AI-Extensions Project"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">roles</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"producer"</span>
        </li>



    </ul>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">url</span>
            <span class="pystac-v">"https://ai-extensions.github.io/docs"</span>
        </li>



    </ul>
        </details></li>



    </ul>

    </details></li>


        </ul>
    </div>
</div>



#### Interlink STAC Objects

**Note**: In order to add a STAC Item to the Collection, ensure that a STAC Item is not already present in the Collection. 

If that's the case, firstly open the `collection.json` file and delete the Item from it, then open the `catalog.json` file and delete the Collection from it. 

This will ensure that both `collection.json` and `catalog.json` files are updated correctly.  


```python
# Add STAC Item to the Collection. Note: this works only if there are no items in the collection
if not any(item.id in link.href for link in collection.links if link.rel == "item"):
    # Add item
    print("Adding item")
    collection.add_item(item=item)
collection
```

    Adding item







<style>
.pystac-summary {
    cursor: pointer;
    display: list-item;
    list-style: revert;
    margin-bottom: 0 !important;

    .pystac-l {
        padding-left: 0.5em;
        color: rgb(64, 128, 128);
        font-style: italic;
    }
}
.pystac-row {
    overflow-wrap: break-word;
    padding-left: .825em;

    .pystac-k {
        display: inline-block;
        margin: 0px 0.5em 0px 0px;
    }
    .pystac-v {
        color: rgb(186, 33, 33);
    }
}
.pystac-k {
    color: rgb(0, 128, 0);
    font-weight: 700;
}
</style>
<div class="jp-RenderedJSON jp-mod-trusted jp-OutputArea-output">
    <div class="container" style="line-height: normal;">
        <ul style="padding: 0px; margin: 0px; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"Collection"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">id</span>
            <span class="pystac-v">"ML-Models_EO"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">stac_version</span>
            <span class="pystac-v">"1.1.0"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"A collection for ML Models"</span>
        </li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">links</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">0</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">rel</span>
            <span class="pystac-v">"item"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">href</span>
            <span class="pystac-v">"/home/t2/Desktop/p/argo/machine-learning-process/MLM/ML_Catalog/ML-Models_EO/Tile-based-ML-Models/Tile-based-ML-Models.json"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"application/geo+json"</span>
        </li>



    </ul>
        </details></li>



    </ul>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">title</span>
            <span class="pystac-v">"ML-Models_EO"</span>
        </li>





        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">extent</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">spatial</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">bbox</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">0</span><span class="pystac-l">[] 4 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">-180</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">-90</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">2</span>
            <span class="pystac-v">180</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">3</span>
            <span class="pystac-v">90</span>
        </li>



    </ul>

    </details></li>


    </ul>

    </details></li>


    </ul>
        </details></li>





        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">temporal</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">interval</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">


                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">0</span><span class="pystac-l">[] 2 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"2015-06-27T00:00:01Z"</span>
        </li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">1</span>
            <span class="pystac-v">None</span>
        </li>



    </ul>

    </details></li>


    </ul>

    </details></li>


    </ul>
        </details></li>



    </ul>
        </details></li>





        <li class="pystac-row">
            <span class="pystac-k">license</span>
            <span class="pystac-v">"proprietary"</span>
        </li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">providers</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">0</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">name</span>
            <span class="pystac-v">"AI-Extensions Project"</span>
        </li>




                <li><details>
        <summary class="pystac-summary"><span class="pystac-k">roles</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">0</span>
            <span class="pystac-v">"producer"</span>
        </li>



    </ul>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">url</span>
            <span class="pystac-v">"https://ai-extensions.github.io/docs"</span>
        </li>



    </ul>
        </details></li>



    </ul>

    </details></li>


        </ul>
    </div>
</div>




```python
# Add Collection to the Catalog.
print("Adding Collection")
collection.set_parent(catalog)
catalog.add_child(collection)
catalog
```

    Adding Collection







<style>
.pystac-summary {
    cursor: pointer;
    display: list-item;
    list-style: revert;
    margin-bottom: 0 !important;

    .pystac-l {
        padding-left: 0.5em;
        color: rgb(64, 128, 128);
        font-style: italic;
    }
}
.pystac-row {
    overflow-wrap: break-word;
    padding-left: .825em;

    .pystac-k {
        display: inline-block;
        margin: 0px 0.5em 0px 0px;
    }
    .pystac-v {
        color: rgb(186, 33, 33);
    }
}
.pystac-k {
    color: rgb(0, 128, 0);
    font-weight: 700;
}
</style>
<div class="jp-RenderedJSON jp-mod-trusted jp-OutputArea-output">
    <div class="container" style="line-height: normal;">
        <ul style="padding: 0px; margin: 0px; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"Catalog"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">id</span>
            <span class="pystac-v">"ML-Model_EO"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">stac_version</span>
            <span class="pystac-v">"1.1.0"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"A catalog to describe ML models"</span>
        </li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">links</span><span class="pystac-l">[] 1 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">0</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">rel</span>
            <span class="pystac-v">"child"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">href</span>
            <span class="pystac-v">None</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"application/json"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">title</span>
            <span class="pystac-v">"ML-Models_EO"</span>
        </li>



    </ul>
        </details></li>



    </ul>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">title</span>
            <span class="pystac-v">"ML Models"</span>
        </li>



        </ul>
    </div>
</div>



Normalise the catalog to save the files under a specific folder name


```python
catalog.normalize_and_save(
    root_href=CATALOG_DIR, catalog_type=pystac.CatalogType.SELF_CONTAINED
)
catalog.validate()
catalog
```






<style>
.pystac-summary {
    cursor: pointer;
    display: list-item;
    list-style: revert;
    margin-bottom: 0 !important;

    .pystac-l {
        padding-left: 0.5em;
        color: rgb(64, 128, 128);
        font-style: italic;
    }
}
.pystac-row {
    overflow-wrap: break-word;
    padding-left: .825em;

    .pystac-k {
        display: inline-block;
        margin: 0px 0.5em 0px 0px;
    }
    .pystac-v {
        color: rgb(186, 33, 33);
    }
}
.pystac-k {
    color: rgb(0, 128, 0);
    font-weight: 700;
}
</style>
<div class="jp-RenderedJSON jp-mod-trusted jp-OutputArea-output">
    <div class="container" style="line-height: normal;">
        <ul style="padding: 0px; margin: 0px; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"Catalog"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">id</span>
            <span class="pystac-v">"ML-Model_EO"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">stac_version</span>
            <span class="pystac-v">"1.1.0"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">description</span>
            <span class="pystac-v">"A catalog to describe ML models"</span>
        </li>




                    <li><details>
        <summary class="pystac-summary"><span class="pystac-k">links</span><span class="pystac-l">[] 3 items</span></summary>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">0</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">rel</span>
            <span class="pystac-v">"root"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">href</span>
            <span class="pystac-v">"/home/t2/Desktop/p/argo/machine-learning-process/MLM/ML_Catalog/catalog.json"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"application/json"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">title</span>
            <span class="pystac-v">"ML Models"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">1</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">rel</span>
            <span class="pystac-v">"child"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">href</span>
            <span class="pystac-v">"/home/t2/Desktop/p/argo/machine-learning-process/MLM/ML_Catalog/ML-Models_EO/collection.json"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"application/json"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">title</span>
            <span class="pystac-v">"ML-Models_EO"</span>
        </li>



    </ul>
        </details></li>



    </ul>

            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li><details>
            <summary class="pystac-summary"><span class="pystac-k">2</span></summary>
            <ul style="margin: 0px; padding: 0px 0px 0px 1.75em; list-style: none; display: block;">



        <li class="pystac-row">
            <span class="pystac-k">rel</span>
            <span class="pystac-v">"self"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">href</span>
            <span class="pystac-v">"/home/t2/Desktop/p/argo/machine-learning-process/MLM/ML_Catalog/catalog.json"</span>
        </li>





        <li class="pystac-row">
            <span class="pystac-k">type</span>
            <span class="pystac-v">"application/json"</span>
        </li>



    </ul>
        </details></li>



    </ul>

    </details></li>




        <li class="pystac-row">
            <span class="pystac-k">title</span>
            <span class="pystac-v">"ML Models"</span>
        </li>



        </ul>
    </div>
</div>




```python
# Check that collection and item have been included in the catalog
catalog.describe()
```

    * <Catalog id=ML-Model_EO>
        * <Collection id=ML-Models_EO>
          * <Item id=Tile-based-ML-Models>

