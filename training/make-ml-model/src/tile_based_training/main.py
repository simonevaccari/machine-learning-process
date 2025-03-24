import os

# os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices=0'
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
from tile_based_training import logger
import warnings
import click
from pathlib import Path
from tile_based_training.utils.common import (
    s3_bucket_config,
    write_yaml,
    configure_gpu,
)
from tile_based_training.pipeline.stage_01_data_ingestion import (
    DataIngestionTrainingPipeline,
)
from tile_based_training.pipeline.stage_02_prepare_base_model import (
    PrepareBaseModelTRainingPipeline,
)
from tile_based_training.pipeline.stage_03_model_training import ModelTRainingPipeline
from tile_based_training.pipeline.stage_04_model_evaluation import (
    ModelEvaluationPipeline,
)

warnings.filterwarnings("ignore")


@click.command(
    short_help="making a tile-based classification on a sentinel-2 L1C data ",
    help="A selected model with highest evaluation metrics will making an inference on a sentinel-2 L1C data",
)
@click.option(
    "--stac_endpoint_url",
    "stac_endpoint_url",
    help="The url which point to STAC endpoint (Catalog)",
    required=True,
    show_default=True,
)
@click.option(
    "--BATCH_SIZE",
    "BATCH_SIZE",
    help="BATCH_SIZE",
    required=False,
    default=4,
    show_default=True,
    type=int,
)
@click.option(
    "--CLASSES",
    "CLASSES",
    help="Number of classes",
    required=False,
    default=10,
    show_default=True,
    type=int,
)
@click.option(
    "--DECAY",
    "DECAY",
    help="DECAY - model metadata",
    required=False,
    default=0.1,
    show_default=True,
    type=float,
)
@click.option("--EPOCHS", "EPOCHS", help="Number of epochs", required=False, default=5, type=int)
@click.option(
    "--EPSILON",
    "EPSILON",
    help="EPSILON - model metadata",
    required=False,
    default=0.000001,
    show_default=True,
    type=float,
)
@click.option(
    "--IMAGE_SIZE",
    "IMAGE_SIZE",
    help="input image size to model",
    required=False,
    multiple=True,
    default=[64, 64, 13],
    show_default=True,
)
@click.option(
    "--LEARNING_RATE",
    "LEARNING_RATE",
    help="LEARNING_RATE",
    required=False,
    default=0.0001,
    show_default=True,
    type=float,
)
@click.option(
    "--LOSS",
    "LOSS",
    help="loss function",
    required=False,
    default="categorical_crossentropy",
    show_default=True,
    type=str,
)
@click.option(
    "--MEMENTUM",
    "MEMENTUM",
    help="MEMENTUM - model metadata",
    required=False,
    default=0.95,
    show_default=True,
    type=float,
)
@click.option(
    "--OPTIMIZER",
    "OPTIMIZER",
    help="OPTIMIZER",
    required=False,
    default="Adam",
    show_default=True,
    type=str,
)
@click.option(
    "--REGULIZER",
    "REGULIZER",
    help="REGULIZER",
    required=False,
    default="None",
    type=str,
)
@click.option(
    "--SAMPLES_PER_CLASS",
    "SAMPLES_PER_CLASS",
    help="number of sample for each class to train model based on",
    required=False,
    default=500,
    show_default=True,
    type=int,
)
@click.option(
    "--enable_data_ingestion",
    "enable_data_ingestion",
    help="A flag to enable data ingestion pipeline",
    required=False,
    is_flag=True,
    default=False,
    show_default=True,
    type=bool,
)
@click.pass_context
def run_tile_based_classification_training(ctx, **kwargs):
    device_name = configure_gpu()
    logger.info(f"MLFLOW URI: {os.environ.get('MLFLOW_TRACKING_URI')}")
    logger.info(f"{os.getcwd()}")
    logger.info(
        f"\n=================================================================\nDevice name is: {device_name} \n================================================================="
    )
    write_yaml(path_to_yaml=Path("params.yaml"), args=kwargs)

    s3_bucket_config()
    # First step
    STAGE_NAME = "Data Ingestion stage"
    if kwargs["enable_data_ingestion"] == True:
        try:
            logger.info(f"\n=================================================================\n>>>>>> stage {STAGE_NAME} started <<<<<<")
            obj = DataIngestionTrainingPipeline()
            obj.main()
            logger.info(
                f"\n=================================================================\n>>>>>> stage {STAGE_NAME} completed <<<<<<\n================================================================="
            )
        except Exception as e:
            logger.exception(e)
            raise e
    else:
        logger.info(
            f"\n=================================================================\n>>>>>> stage {STAGE_NAME} skipped <<<<<<\n================================================================="
        )

    STAGE_NAME = "Prepare Base Model"
    logger.info(f"\n=================================================================\n>>>>>> stage {STAGE_NAME} started <<<<<<")

    try:
        obj = PrepareBaseModelTRainingPipeline()
        obj.main()
        logger.info(
            f"\n=================================================================\n>>>>>> stage {STAGE_NAME} completed <<<<<<\n================================================================="
        )
    except Exception as e:
        logger.exception(e)
        raise e
    STAGE_NAME = "Training Model"

    try:
        logger.info(f"\n=================================================================\n>>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = ModelTRainingPipeline()
        obj.main(device_name)
        logger.info(
            f"\n=================================================================\n>>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x"
        )
    except Exception as e:
        logger.exception(e)
        raise e

    STAGE_NAME = "Evaluating Model"

    try:
        logger.info(f"\n=================================================================\n>>>>>> stage {STAGE_NAME} started <<<<<<")
        obj = ModelEvaluationPipeline()
        obj.main()
        logger.info(
            f"\n=================================================================\n>>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x"
        )
    except Exception as e:
        logger.exception(e)
        raise e


def main():
    run_tile_based_classification_training()


if __name__ == "__main__":
    # Log the experiment
    main()


# # First step
# STAGE_NAME = "Data Ingestion stage"

# try:
#     if not (os.path.isfile("./output/data_ingestion/splited_data.json")):
#         logger.info(f"\n>>>>>> stage {STAGE_NAME} started <<<<<<")
#         obj = DataIngestionTrainingPipeline()
#         obj.main()
#         logger.info(
#             f"\n>>>>>> stage {STAGE_NAME} completed <<<<<<\n================================================================="
#         )
#     else:
#         logger.info(
#             f"\n>>> stage {STAGE_NAME} is completed in previous attempts <<<\n================================================================="
#         )
# except Exception as e:
#     logger.exception(e)
#     raise e

# STAGE_NAME = "Prepare Base Model"

# try:
#     logger.info(f"\n>>>>>> stage {STAGE_NAME} started <<<<<<")
#     obj = PrepareBaseModelTRainingPipeline()
#     obj.main()
#     logger.info(
#         f"\n\n>>>>>> stage {STAGE_NAME} completed <<<<<<\n================================================================="
#     )
# except Exception as e:
#     logger.exception(e)
#     raise e


# STAGE_NAME = "Training Model"

# try:
#     logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
#     obj = ModelTRainingPipeline()
#     obj.main()
#     logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
# except Exception as e:
#     logger.exception(e)
#     raise e


# STAGE_NAME = "Evaluating Model"

# try:
#     logger.info(f">>>>>> stage {STAGE_NAME} started <<<<<<")
#     obj = ModelEvaluationPipeline()
#     obj.main()
#     logger.info(f">>>>>> stage {STAGE_NAME} completed <<<<<<\n\nx==========x")
# except Exception as e:
#     logger.exception(e)
#     raise e
