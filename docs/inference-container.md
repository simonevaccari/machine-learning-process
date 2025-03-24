# Inference container:
This module helps the user to create a pipeline for inference, which is responsible for reading assets from a Sentinel-2 L1C STAC item, loading 13 common bands, and providing a binary mask TIFF image using a CNN model that has already been trained (Please check the [training-container](./training-container.md)). 


## **Make Inference Module:**

**Inputs**:
- `input_reference`: The reference to a [staged-in](./stage-in.md) Sentinel-2 L1C product to run the inference on Sentinel-2 L1C images with 13 common bands.

**Outputs**:

- `{STAC_ITEM_ID}_classified.tif`: A binary `.tif` image in `COG` format classifies:

| Class ID | Class Name            |
|----------|-----------------------|
| 0        | AnnualCrop            |
| 1        | Forest                |
| 2        | HerbaceousVegetation  |
| 3        | Highway               |
| 4        | Industrial            |
| 5        | Pasture               |
| 6        | PermanentCrop         |
| 7        | Residential           |
| 8        | River                 |
| 9        | SeaLake               |
| 10       | No Data               |

- `overview_{STAC_ITEM_ID}_classified.tif`: A binary `.tif` image in `COG` format classifies:

| Class ID | Class Name            |
|----------|-----------------------|
| 0        | AnnualCrop            |
| 1        | Forest                |
| 2        | HerbaceousVegetation  |
| 3        | Highway               |
| 4        | Industrial            |
| 5        | Pasture               |
| 6        | PermanentCrop         |
| 7        | Residential           |
| 8        | River                 |
| 9        | SeaLake               |
| 10       | No Data               |

- `STAC objects`: STAC objects related to the provided masks, including STAC catalog and STAC Item.


Certainly! Here's a grammatically correct and technically clearer version of your section:


## How the Application Package Works

Before developing the inference module, one crucial step must be completed: the user needs to **select a candidate model from MLflow**, based on preferred evaluation metrics. The selected model should then be exported in the [ONNX](https://onnx.ai/) format and used for building the inference module.

The user must also provide a staged-in Sentinel-2 L1C product and read the STAC Item's 13 common spectral bands, which serve as the input to the trained model. These assets are processed using a 64×64 sliding window to handle memory limitations and ensure the input size matches that of the machine learning model.

Finally, the model generates predictions, and the resulting classification masks are stored as a **COG (Cloud-Optimized GeoTIFF)** image.
