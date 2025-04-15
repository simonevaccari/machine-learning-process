# from . import logger
from tile_based_training.utils.common import *
from tile_based_training.entity.config_entity import DataIngestionConfig
import os
from tqdm import tqdm
from pystac_client import Client
import pystac
from pystac.stac_io import DefaultStacIO, StacIO
from stac_geoparquet.arrow._api import stac_table_to_items
# import botocore
from sklearn.model_selection import train_test_split
import io
from tile_based_training.utils.common import duckdb_config, sql_generator

# UPDATING src's component
class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def stac_loader(self) -> list:
        """
        Fetch data from the endpoint
        """
        try:
            samples_per_class = self.config.samples_per_class
            logger.info(f"Accessing STAC endpoint")
            image_urls = []
            catalog = pystac.read_file(self.config.stac_reference) 
            collection = next(iter(catalog.get_children()))
            for key, asset in collection.get_assets().items():
                if asset.media_type == "application/vnd.apache.parquet":
                    geoparquet_asset_path = asset.href
            
            for class_name in tqdm(self.config.data_classes):
                sql_query = sql_generator(
                    class_name=class_name, geoparquet_asset_path=geoparquet_asset_path, samples_per_class=samples_per_class
                )

                duckdb_config()
                db = duckdb.query(sql_query)
                
                table = db.fetch_arrow_table()
                try:
                    for item in tqdm(stac_table_to_items(table), desc=f"Fetching data from class {class_name}"):
                        # print(item)
                        asset = item["assets"]["image"]
                        image_urls.append(
                            {
                                "url": asset["href"] +"/"+ asset["archive:href"],
                                "label": class_name,
                            }
                        )
                except Exception as e:
                    raise e
            logger.info(f"{len(image_urls)} items are loaded")

        except Exception as e:
            raise e
        return image_urls

    def data_spliting(self, full_dataset, split_name="train"):
        

        X = [x["url"] for x in full_dataset]
        y = [x["label"] for x in full_dataset]
        random_state = 42
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=random_state)
        X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25, random_state=random_state)
        logger.info(f"Train size: {len(X_train)} , Valid size: {len(X_val)}, Test size: {len(X_test)}")
        dataset = {
            "train": {"url": X_train, "label": y_train},
            "val": {"url": X_val, "label": y_val},
            "test": {"url": X_test, "label": y_test},
        }

        json.dump(dataset, open(self.config.root_dir + "/splitted_data.json", "w"))

        return dataset