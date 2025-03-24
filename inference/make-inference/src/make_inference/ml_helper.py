from loguru import logger
import os
from shutil import move
import rasterio
import pystac
from rio_stac.stac import create_stac_item
from rasterio.warp import Resampling
from rasterio.windows import Window
from typing import Dict, List
import pystac
import warnings
import math
import numpy as np

warnings.filterwarnings("ignore")


def _get_stats(arr: np.ma.MaskedArray) -> Dict:
    """Calculate array statistics."""
    # Avoid non classified nan/inf values
    np.ma.fix_invalid(arr, copy=False)
    sample, edges = np.histogram(arr[~arr.mask], bins=np.arange(256))
    return {
        "statistics": {
            "mean": arr.mean().item(),
            "minimum": arr.min().item(),
            "maximum": arr.max().item(),
            "stddev": arr.std().item(),
            "valid_percent": np.count_nonzero(~arr.mask) / float(arr.data.size) * 100,
        },
        "histogram": {
            "count": len(edges),
            "min": float(edges.min()),
            "max": float(edges.max()),
            "buckets": sample.tolist(),
        },
    }


def get_raster_info(
    src_dst,
    max_size: int = 1024,
):
    """Get raster metadata.
    see: https://github.com/stac-extensions/raster#raster-band-object
    """
    height = src_dst.height
    width = src_dst.width
    if max_size:
        if max(width, height) > max_size:
            ratio = height / width
            if ratio > 1:
                height = max_size
                width = math.ceil(height / ratio)
            else:
                width = max_size
                height = math.ceil(width * ratio)

    meta: List[Dict] = []

    area_or_point = src_dst.tags().get("AREA_OR_POINT", "").lower()

    # Missing `bits_per_sample` and `spatial_resolution`
    for band in src_dst.indexes:
        value = {
            "data_type": src_dst.dtypes[band - 1],
            "scale": src_dst.scales[band - 1],
            "offset": src_dst.offsets[band - 1],
        }
        if area_or_point:
            value["sampling"] = area_or_point

        # If the Nodata is not set we don't forward it.
        if src_dst.nodata is not None:
            if np.isnan(src_dst.nodata):
                value["nodata"] = "nan"
            elif np.isposinf(src_dst.nodata):
                value["nodata"] = "inf"
            elif np.isneginf(src_dst.nodata):
                value["nodata"] = "-inf"
            else:
                value["nodata"] = src_dst.nodata

        if src_dst.units[band - 1] is not None:
            value["unit"] = src_dst.units[band - 1]

        value.update(_get_stats(src_dst.read(indexes=band, out_shape=(height, width), masked=True)))
        meta.append(value)

    return meta


def generate_asset_overview(asset_in_key, target_dir):
    asset_out_key = f"{asset_in_key}"
    raster_info = {
        "raster:bands": get_raster_info(
            rasterio.open(target_dir),
            max_size=1024,
        )
    }

    return "overview-" + asset_in_key, pystac.asset.Asset(
        href=f"overview-{asset_out_key}_classified.tif",
        media_type=pystac.media_type.MediaType.COG,
        title=f"{asset_out_key} overview",
        roles=["visual", "overview"],
        extra_fields=raster_info,
    )


def generate_asset(asset_in_key, target_dir):
    asset_out_key = f"{asset_in_key}"
    raster_info = {
        "raster:bands": get_raster_info(
            rasterio.open(target_dir),
            max_size=1024,
        )
    }

    return asset_in_key, pystac.asset.Asset(
        href=f"{asset_out_key}_classified.tif",
        media_type=pystac.media_type.MediaType.COG,
        title=f"{asset_out_key}",
        roles=["visual", "data"],
        extra_fields=raster_info,
    )


def to_stac(geotiff_path, item):
    asset_key_image, asset_image = generate_asset(asset_in_key=item.id, target_dir=geotiff_path)

    asset_key_overview, asset_overview = generate_asset_overview(asset_in_key=item.id, target_dir=geotiff_path)

    result_item = create_stac_item(
        id=f"{item.id}_classified",
        source=geotiff_path,
        assets={asset_key_image: asset_image, asset_key_overview: asset_overview},
        with_proj=True,
        with_raster=False,
        properties={},
    )

    return result_item


def save_prediction(data, output_href, meta):
    # Create a mask for the dataset
    # 0 in data becomes 0 in mask (invalid), all other values become 255 (valid)
    mask = np.where(data == 0, 0, data).astype(np.uint8)

    meta.update(
        {
            "driver": "COG",
            "dtype": "uint8",
            "blockxsize": 512,
            "blockysize": 512,
            "count": 1,
            "tiled": True,
            "compress": "deflate",
            "interleave": "band",
            "nodata": 10,  # Setting nodata to -1 for this example
        }
    )

    with rasterio.open(output_href, "w", **meta) as dst:
        dst.write(data, indexes=1)
        # Apply colormap to the data
        dst.write_colormap(
            1,
            {
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
            },
        )

        cmap = dst.colormap(1)
        assert cmap[0] == (34, 139, 34, 255)

        dst.build_overviews([2, 4, 8, 16, 32, 64], Resampling.nearest)
        dst.update_tags(ns="rio_overview", resampling="nearest")


def save_overview(data, output_href, meta):
    mask = np.where(data == 0, 0, 255).astype(np.uint8)
    meta.update(
        {
            "driver": "COG",
            "dtype": "uint8",
            "blockxsize": 512,
            "blockysize": 512,
            "count": 1,
            "tiled": True,
            "compress": "deflate",
            "interleave": "band",
            "nodata": 10,  # Setting nodata to 0 for this example
        }
    )
    with rasterio.open(output_href, "w", **meta) as dst:
        dst.write(data, indexes=1)
        dst.write_colormap(
            1,
            {
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
            },
        )
        cmap = dst.colormap(1)
        assert cmap[0] == (34, 139, 34, 255)
        dst.build_overviews([2, 4, 8, 16, 32, 64], Resampling.nearest)
        dst.update_tags(ns="rio_overview", resampling="nearest")


def create_stac_catalog(item: pystac.Item):
    out_item = to_stac(f"{item.id}_classified.tif", item)
    logger.info(f"Creating a STAC Catalog for the segmentation result")
    cat = pystac.Catalog(id="catalog", description="segmentation result", title="segmentation result")
    cat.add_items([out_item])
    cat.normalize_and_save(root_href=os.getcwd(), catalog_type=pystac.CatalogType.SELF_CONTAINED)
    move(
        f"{item.id}_classified.tif",
        os.path.join(out_item.id, f"{item.id}_classified.tif"),
    )
    move(
        f"overview-{item.id}_classified.tif",
        os.path.join(out_item.id, f"overview-{item.id}_classified.tif"),
    )


def get_asset(item, common_name):
    """Returns the asset of a STAC Item defined with its common band name"""
    for key, asset in item.get_assets().items():
        if not "data" in asset.to_dict()["roles"]:
            continue

        eo_asset = pystac.extensions.eo.AssetEOExtension(asset)
        if not eo_asset.bands:
            continue
        for b in eo_asset.bands:

            if "common_name" in b.properties.keys() and common_name in b.properties["common_name"]:

                return asset.get_absolute_href()


def item_filter_assets(item):

    common_names = [
        "coastal",
        "blue",
        "green",
        "red",
        "rededge",
        "nir",
        "nir08",
        "nir09",
        "cirrus",
        "swir16",
        "swir22",
    ]
    desirable_assets = {}
    for common_name in common_names:

        desirable_assets[common_name] = get_asset(item, common_name)

    assert len(desirable_assets) > 0, "Item has no desirable asset"
    return desirable_assets


def resize_and_convert_to_cog(asset_path, target_resolution=10):
    output_file = f'./{asset_path.split("/")[-1]}'
    with rasterio.open(asset_path) as src:
        src_transform = src.transform
        if src_transform.a > target_resolution:
            asset_path = output_file
            # Calculate the new shape based on the target resolution
            scale_x = int(src.width * (src.res[0] / target_resolution))
            scale_y = int(src.height * (src.res[1] / target_resolution))
            logger.info(f"Resizing {output_file} to {scale_x}x{scale_y}")
            # Read and resample data
            data = src.read(
                out_shape=(src.count, int(scale_y), int(scale_x)),
                resampling=Resampling.bilinear,
            )

            # Update the metadata for the transformed dataset
            transform = src.transform * src.transform.scale((src.width / data.shape[-1]), (src.height / data.shape[-2]))
            profile = src.profile
            profile.update(
                {
                    "driver": "COG",
                    "dtype": data.dtype,
                    "height": data.shape[1],
                    "width": data.shape[2],
                    "transform": transform,
                    "row_off": 1024,
                    "col_off": 1024,
                    "compress": "LZW",
                    "interleave": "pixel",
                }
            )

            # Write data directly to a COG file
            with rasterio.open(output_file, "w", **profile) as dst:
                dst.write(data)

    return asset_path


def asset_reader(assets):
    srcs = {asset_key: rasterio.open(asset_href) for asset_key, asset_href in assets.items()}
    print(srcs)
    # common bands order:
    # ['coastal', 'blue', 'green', 'red', 'rededge70', 'rededge74', 'rededge78', 'nir', 'nir08', 'nir09', 'cirrus', 'swir16', 'swir22']
    referenced_src = next(iter(srcs.items()))[1]

    meta = referenced_src.meta.copy()

    return srcs, referenced_src, meta


def sliding(shape, window_size, step_size=None, fixed=True):

    h, w = shape
    if step_size:
        h_step = step_size
        w_step = step_size
    else:
        h_step = window_size
        w_step = window_size

    h_wind = window_size
    w_wind = window_size
    windows = []
    for y in range(0, h, h_step):
        for x in range(0, w, w_step):
            h_min = min(h_wind, h - y)
            w_min = min(w_wind, w - x)
            if fixed:
                if h_min < h_wind or w_min < w_wind:
                    continue
            window = Window(x, y, w_min, h_min)
            windows.append(window)

    return windows


def stack_separated_bands(window, srcs, block_shape=(13, 64, 64)):
    """
    Stack specified bands from raster sources into a numpy array block.

    Parameters:
    - window (rasterio.windows.Window): Window of pixels to read.
    - srcs (dict): Dictionary containing raster sources with band names as keys.

    Returns:
    - block (np.ndarray): Stacked array of bands and derived indices.
      Shape will be (num_bands + num_indices, window.height, window.width).
    """
    bands = srcs.keys()

    block = np.empty(block_shape, dtype=np.uint16)
    for i, band_name in enumerate(bands):
        block[i, :, :] = srcs[band_name].read(1, window=window)

    return block


def predict(input_array, session, input_name, output_name):

    prediction_block = np.empty(
        (input_array.shape[1], input_array.shape[2]),
        dtype=np.uint8,
    )
    if np.all(input_array == 0):
        prediction_block[:, :] = 10
    else:
        input_array = np.expand_dims(input_array, axis=0) / 10000.0
        input_array = np.transpose(input_array, (0, 2, 3, 1)).astype(np.float32)
        pred = session.run([output_name], {input_name: input_array})[0]
        prediction_block[:, :] = np.argmax(pred[0], axis=-1)
    return prediction_block
