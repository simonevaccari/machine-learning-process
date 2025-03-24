# `make-inference` Module:
This directory helps the user create the `make-inference` module, which is responsible for reading assets from a Sentinel-2 L1C STAC item, loading 13 common bands, and providing a binary TIFF image (water, non-water) using a CNN model that has already been trained in the [training](../../training/) module. The module is already containerized in a dedicated [gcr.io](https://github.com/orgs/ai-extensions/packages/container/package/tile-sat-inference) container registry (please check the [README](../app-package/README.md#1-run-the-application-package) for information on how the image can be automatically pulled using cwltool/Calrissian). However, there is an [option](#containerize-make-inference-module-on-users-local-environment) for the user to build a Podman image on their local ml-lab environment using the `Dockerfile`.

## **Make Inference Module:**

**Inputs**:
- `input_reference`: The URL to the Sentinel-2 L1C STAC Item to provide inference on Sentinel-2 L1C images with 13 common bands.

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

## How to Execute
The module will be triggered using the [tile-sat-inference.cwl](../app-package/tile-sat-inference.cwl). For more information about how to trigger the module, please check the related [README](../app-package/README.md) file.

## Containerize the `make-inference` Module on the User's Local Environment:
The user can build a `Podman` image to containerize the module using the commands below (`not recommended`).

```bash
cd inference/make-inference
docker build -t <image_tag> .
```
