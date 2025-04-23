# Inference container:

This module enables users to create an inference pipeline that take a Sentinel-2 STAC Item from the [Planetary Computer](https://planetarycomputer.microsoft.com/api/stac/v1/collections), and generates a binary mask TIFF image using a pre-trained CNN model. For details on how the model was trained, refer to the [training container documentation](./training-container.md).



## **Make Inference Module:**

**Inputs**:
- `input_reference`: The reference to a Sentinel-2 product on [planetary computer](https://planetarycomputer.microsoft.com/api/stac/v1/collections). The application will give you an accurate result if the sentinel-2 product has no/low cloud-cover.

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

## How the Application Works

The application begins by reading a Sentinel-2 STAC Item from the [Planetary Computer](https://planetarycomputer.microsoft.com/api/stac/v1/collections). It then filters and selects 12 specific asset references in the order expected by the machine learning model. These assets correspond to common Sentinel-2 bands, as shown below:

| Index | Asset Key  | Asset Common Name |
|-------|------------|-------------------|
| 1     | B01        | Coastal           |
| 2     | B02        | Blue              |
| 3     | B03        | Green             |
| 4     | B04        | Red               |
| 5     | B05        | Red Edge          |
| 6     | B06        | Red Edge          |
| 7     | B07        | Red Edge          |
| 8     | B08        | NIR               |
| 9     | B8A        | Narrow NIR        |
| 10    | B09        | Water Vapor       |
| 11    | B11        | SWIR 1 (16)       |
| 12    | B12        | SWIR 2 (22)       |

As a preprocessing step, all selected assets are resampled to a uniform resolution of 10 meters.

The pipeline then proceeds with a sliding window approach: it reads and stacks small image chips from the selected bands in the order listed above. These chips are fed into a trained CNN model, which predicts the corresponding class for each chip.

Finally, the application generates:
- The classification prediction map (as a GeoTIFF mask)
- A visual overview image
- An updated STAC item containing metadata and references to the output files