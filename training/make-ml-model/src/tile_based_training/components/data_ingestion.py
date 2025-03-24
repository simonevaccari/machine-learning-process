# from . import logger
from tile_based_training.utils.common import *
from tile_based_training.entity.config_entity import DataIngestionConfig
import os
from tqdm import tqdm
from pystac_client import Client
from pystac.stac_io import DefaultStacIO, StacIO
from stac_geoparquet.arrow._api import stac_table_to_items
import botocore
import io
from tile_based_training.utils.common import duckdb_s3_config, sql_generator

# UPDATING src's component
class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def stac_loader(self) -> list:
        """
        Fetch data from the endpoint
        """
        try:
            StacIO.set_default(CustomStacIO)
            StacIO.read_text_method = CustomStacIO.read_text
            stac_endpoint = self.config.stac_endpoint
            self.config.local_data_file
            collection_name = self.config.collection_name
            samples_per_class = self.config.samples_per_class
            logger.info(f"Accessing STAC endpoint")
            image_urls = []
            catalog = Client.open(
                stac_endpoint,
                ignore_conformance=True,
            )
            collection = catalog.get_child(collection_name)
            for key, asset in collection.get_assets().items():
                if asset.media_type == "application/vnd.apache.parquet":
                    geoparquet_asset_path = asset.href
            logger.info(f"geoparquet url: {geoparquet_asset_path}")
            connection = duckdb_s3_config()
            for class_name in tqdm(self.config.data_classes):
                sql_query = sql_generator(
                    class_name=class_name, geoparquet_asset_path=geoparquet_asset_path, samples_per_class=samples_per_class
                )
                table = connection.execute(sql_query).fetch_arrow_table()

                params = {
                    "collections": collection_name,
                    "max_items": samples_per_class,
                    "filter": {
                        "op": "like",
                        "args": [{"property": "id"}, f"{class_name}%"],
                    },
                    "limit": int(samples_per_class * 0.9),
                }
                try:
                    for item in tqdm(stac_table_to_items(table), desc=f"Fetching data from class {class_name}"):
                        # print(item)
                        image_urls.append(
                            {
                                "url": item["assets"]["image"]["href"],
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
        from sklearn.model_selection import train_test_split

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

        json.dump(dataset, open(self.config.root_dir + "/splited_data.json", "w"))

        return dataset

    def data_downloader(self, data, split_name="train"):
        urls = data["url"]

        labels = data["label"]
        settings = UserSettings("/etc/Stars/appsettings.json")
        settings.set_s3_environment(f"s3://{bucket_name}/Euro_SAT/Euro_SAT")
        StacIO.set_default(DefaultStacIO)
        # reach to bucket name and key

        session = botocore.session.Session()
        s3_client = session.create_client(
            service_name="s3",
            use_ssl=True,
            region_name=os.environ.get("AWS_REGION"),
            endpoint_url=os.environ.get("AWS_S3_ENDPOINT"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        )

        try:
            for url, label in zip(tqdm(urls, desc=f"Downloading {split_name}"), labels):
                parsed = urlparse(url)
                bucket = parsed.netloc
                key = parsed.path[1:]

                # retrive the obj which was stored on s3
                respond = s3_client.get_object(Bucket=bucket, Key=key)
                content = io.BytesIO(respond["Body"].read())
                # create trin/test/val directories
                output_dir = f"output/data_ingestion/{split_name}/{label}"
                os.makedirs(output_dir, exist_ok=True)

                # Save the tif content to a local file
                with open(f'{output_dir}/{url.split("/")[-1].replace(".tif","")}.tif', "wb") as file:
                    file.write(content.getvalue())

        except Exception as e:
            raise e
