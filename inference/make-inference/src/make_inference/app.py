from loguru import logger
import os
import pystac
import click
from georeader.geotensor import GeoTensor
from tqdm import tqdm
import warnings
import numpy as np
import onnxruntime as ort
from .ml_helper import *

warnings.filterwarnings("ignore")


@click.command(
    short_help="making a tile-based classification on a sentinel-2 L1C data ",
    help="A selected model with highest evaluation metrics will making an inference on a sentinel-2 L1C data",
)
@click.option(
    "--input_reference",
    "input_reference",
    help="Url to sentinel-2 L1C STAC Item to provide inference on tif images for 13 common bands",
    type=click.Path(),
    required=True,
)
@click.pass_context
def run_inference(ctx, **params):
    # logger.info(os.path.dirname(os.path.abspath(".")))

    if os.path.isdir(params["input_reference"]):
        catalog = pystac.read_file(os.path.join(params["input_reference"], "catalog.json"))
        item = next(catalog.get_items())

        filtered_assets = item_filter_assets(item)

    else:
        item = pystac.read_file(params["input_reference"])
        filtered_assets = item_filter_assets(item)
    for key, asset in item.get_assets().items():
        print(key)
    logger.info(f"Read {item.get_self_href()}")
    window_size = 64
    for key, asset_href in filtered_assets.items():
        print(asset_href)
        updated_asset_href = resize_and_convert_to_cog(asset_href)
        filtered_assets[key] = updated_asset_href
    ### Open the tif file
    srcs, referenced_src, meta = asset_reader(filtered_assets)
    prediction = np.full(
        (
            referenced_src.height,
            referenced_src.width,
        ),
        np.nan,
        dtype=np.float32,  # Use a floating-point data type
    )  # create the empty array
    windows = sliding((referenced_src.height, referenced_src.width), window_size)

    tqdm_loop = tqdm(
        windows,
        total=len(windows),
        desc=f"Predicting",
    )
    model_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "model",
        "model.onnx",
    )
    session = ort.InferenceSession(model_path)
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    for i, window in enumerate(tqdm_loop):
        arr_block = stack_separated_bands(window, srcs)  ## you must add ndwi
        # print(arr_block.shape, prediction)
        tqdm_loop.set_postfix(
            ordered_dict={
                "col_off": window.col_off,
                "row_off": window.row_off,
                "block shape": arr_block.shape,
            }
        )

        prediction_block = predict(arr_block, session, input_name, output_name)
        prediction[
            window.row_off : window.row_off + window.height,
            window.col_off : window.col_off + window.width,
        ] = prediction_block

        # Save prediction as a COG tif image and provide STAC objs for that
    logger.info(f"Saving segmentation result to {item.id}_classified.tif")
    prediction_block_raster = GeoTensor(
        prediction,
        transform=meta["transform"],
        fill_value_default=None,
        crs=meta["crs"],
    )
    save_prediction(prediction_block_raster.values, f"{item.id}_classified.tif", meta)
    save_overview(prediction_block_raster.values, f"overview-{item.id}_classified.tif", meta)

    create_stac_catalog(item)
    del arr_block, prediction
    for file in os.listdir():
        if file.endswith("tiff") or file.endswith("tif"):
            os.remove(file)
    logger.info("Done!")


def main():
    run_inference()


if __name__ == "__main__":
    # Log the experiment
    main()
