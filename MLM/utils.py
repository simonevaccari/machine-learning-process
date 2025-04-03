import os
import sys
import pyproj

# don't remove this import, it's needed for the botocore session
import boto3  # noqa: F401
import botocore

from urllib.parse import urljoin, urlparse
from loguru import logger
import requests
import subprocess
from botocore.exceptions import ClientError
import numpy as np
import pystac
from pystac.extensions.eo import EOExtension
from pystac import Collection, read_file, Asset
from pystac.stac_io import DefaultStacIO, StacIO
import pandas as pd
from datetime import datetime, timezone

import folium
from folium import GeoJson, LayerControl


class StarsCopyWrapper:
    def __init__(self):
        self.command = ["Stars", "copy"]

    def _add_option(self, option):
        self.command.append(option)
        return self

    def recursivity(self):
        return self._add_option("-r")._add_option(str(4))

    def skip_assets(self):
        return self._add_option("-sa")

    def output(self, output_dir):
        return self._add_option("-o")._add_option(output_dir)

    def allow_ordering(self):
        return self._add_option("-ao")

    def extract_archive(self, extract=True):
        if extract:
            return self._add_option("-xa true")
        else:
            return self._add_option("-xa false")

    def stop_on_error(self, stop=True):
        if stop:
            return self._add_option("--stop-on-error")

    def supplier_included(self, supplier):
        return self._add_option("-si")._add_option(supplier)

    def supplier_excluded(self, supplier):
        return self._add_option("-se")._add_option(supplier)

    def append_catalog(self):
        return self._add_option("-ac")

    def keep_all(self):
        return self._add_option("-ka")

    def relative(self):
        return self._add_option("-rel")

    def harvest(self):
        return self._add_option("-h")

    def absolute_assets(self):
        return self._add_option("-aa")

    def result_file(self, result_file):
        return self._add_option("-res")._add_option(result_file)

    def asset_filter(self, asset_filter):
        return self._add_option("-af")._add_option(asset_filter)

    def keep_original_assets(self, keep=True):
        if keep:
            return self._add_option("-koa")

    def nocopy_cog(self):
        return self._add_option("--nocopy-cog")

    def asset_filter_out(self, asset_filter_out):
        return self._add_option("-afo")._add_option(asset_filter_out)

    def empty(self, empty_arg):
        return self._add_option("--empty")._add_option(empty_arg)

    def verbose(self):
        return self._add_option("-v")

    def config_file(self, config_file):
        return self._add_option("-conf")._add_option(config_file)

    def skip_certificate_validation(self):
        return self._add_option("-k")

    def run(self, *inputs):
        self.command.extend(inputs)
        result = subprocess.run(
            self.command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return (
            result.returncode,
            result.stdout.decode("utf-8"),
            result.stderr.decode("utf-8"),
        )


def get_headers():
    payload = {
        "client_id": "ai-extensions",
        "username": "ai-extensions-user",
        "password": os.environ.get("IAM_PASSWORD"),
        "grant_type": "password",
    }
    token = get_token(url=os.environ.get("IAM_URL"), **payload)
    headers = {"Authorization": f"Bearer {token}"}

    return headers


def post_or_put(url: str, data: dict, headers=None):
    """Post or put data to url."""

    if headers is None:
        headers = {}

    request = requests.post(url, json=data, timeout=20, headers=headers)
    if request.status_code == 409:
        new_url = url if data["type"] == "Collection" else url + f"/{data['id']}"
        # Exists, so update
        request = requests.put(new_url, json=data, timeout=20, headers=headers)
        # Unchanged may throw a 404
        if not request.status_code == 404:
            request.raise_for_status()
    else:
        request.raise_for_status()
    logger.info(f"{url} {request.status_code}")
    return request


def ingest_collection(app_host: str, collection: Collection, headers=None):
    """ingest collection."""

    post_or_put(urljoin(app_host, "/collections"), collection.to_dict(), headers)


def ingest_items(app_host: str, items, collection: None, headers=None):
    """ingest items."""

    for item in items:
        for _, asset in item.get_assets().items():
            parsed = urlparse(asset.href)
            # if parsed.scheme not in ["s3", "https", "http"]:
            #     logger.error(
            #         f"Item {item.id} has an asset with an invalid href: {asset.href}"
            #     )
            #     sys.exit(1)

        if item.get_collection() is not None and collection is not None:
            # item has a collection, so we need to override it
            item.set_collection(collection)
            collection_id = collection.id

        if item.get_collection() is not None and collection is None:
            # item has a collection, we use that
            collection_id = item.get_collection().id

        if item.get_collection() is None and collection is not None:
            # item has no collection, we use the one provided
            item.set_collection(collection)
            collection_id = collection.id

        logger.info(
            f"Post item {item.id} to {app_host}/collections/{collection_id}/items"
        )

        request = post_or_put(
            urljoin(app_host, f"/collections/{collection_id}/items"),
            item.to_dict(),
            headers=headers,
        )

        print(
            [link["href"] for link in request.json()["links"] if link["rel"] == "self"][
                0
            ]
        )


"""
This code defines a UserSettings class that has methods for reading JSON files,
matching regular expressions, and setting environment variables for an S3 service.
The set_s3_environment method sets environment variables for an S3 service based
on a given URL.
"""

import json
import os
import re


class UserSettings:
    """class for reading JSON files, matching regular expressions,
    and setting environment variables for an S3 service"""

    def __init__(self, file_path):
        self.file_path = file_path
        self.settings = self.read_json_file(file_path)

    @staticmethod
    def read_json_file(file_path):
        """read a JSON file and return the contents as a dictionary"""
        with open(file_path, "r", encoding="utf-8") as stream:
            return json.load(stream)

    @staticmethod
    def match_regex(regex, string):
        """match a regular expression to a string and return the match object"""
        return re.search(regex, string)

    @staticmethod
    def set_s3_vars(s3_service):
        """set environment variables for an S3 service"""
        os.environ["AWS_ACCESS_KEY_ID"] = s3_service["AccessKey"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = s3_service["SecretKey"]
        os.environ["AWS_DEFAULT_REGION"] = s3_service["Region"]
        os.environ["AWS_REGION"] = s3_service["Region"]
        os.environ["AWS_S3_ENDPOINT"] = s3_service["ServiceURL"]

    def set_s3_environment(self, url):
        """set environment variables for an S3 service based on a given URL"""
        for _, s3_service in self.settings["S3"]["Services"].items():
            self.set_s3_vars(s3_service)
            # if self.match_regex(s3_service["UrlPattern"], url):
            #     self.set_s3_vars(s3_service)
            #     break


class CustomStacIO(DefaultStacIO):
    """Custom STAC IO class that uses boto3 to read from S3."""

    def __init__(self):
        self.session = botocore.session.Session()
        self.headers = {}  # Initialize an empty headers dictionary

    def read_text(self, source, *args, **kwargs):
        parsed = urlparse(source)
        if parsed.scheme == "s3":
            # read the user settings file from the environment variable
            s3_settings = UserSettings("/workspace/appsettings.json")
            s3_settings.set_s3_environment(source)

            s3_client = self.session.create_client(
                service_name="s3",
                region_name=os.environ.get("AWS_REGION"),
                use_ssl=True,
                endpoint_url=os.environ.get("AWS_S3_ENDPOINT"),
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            )

            bucket = parsed.netloc
            key = parsed.path[1:]

            try:
                return (
                    s3_client.get_object(Bucket=bucket, Key=key)["Body"]
                    .read()
                    .decode("utf-8")
                )
            except ClientError as ex:
                if ex.response["Error"]["Code"] == "NoSuchKey":
                    logger.error(f"Error reading {source}: {ex}")
                    sys.exit(1)

        else:
            return super().read_text(source, *args, **kwargs)

    def set_headers(self, headers):
        self.headers = headers  # Set the headers to be used for HTTP requests


StacIO.set_default(CustomStacIO)


def read_url(source):
    """Reads a STAC object from a URL or file path."""
    return read_file(source)


def get_token(url, **kwargs):

    data = {**kwargs}

    response = requests.post(url, data=data)

    if response.status_code == 200:
        json_data = response.json()
        access_token = json_data.get("access_token")
        return access_token
    else:
        logger.error(
            f"Request for a token failed with status code {response.status_code}"
        )


def getTemporalExtent(start_date, end_date):
    # Define temporal extent
    if start_date == None:
        start_time = None
    else:
        start_time = datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
    if end_date == None:
        end_time = None
    else:
        end_time = datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)

    return pystac.TemporalExtent([start_time, end_time])


def getGeom(bbox):

    # Convert bbox to geometry dictionary with type and coordinates
    geometry_dict = {
        "type": "Polygon",
        "coordinates": [
            [
                [bbox[0], bbox[1]],
                [bbox[2], bbox[1]],
                [bbox[2], bbox[3]],
                [bbox[0], bbox[3]],
                [bbox[0], bbox[1]],
            ]
        ],
    }

    return geometry_dict
