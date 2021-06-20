import boto3
import configparser
import logging
from typing import Dict

def setup_aws_config() -> Dict[str, str]:

        access_key = input("AWS_ACCESS_KEY=").strip()
        secret_key = input("AWS_SECRET_KEY=").strip()
        region = input("AWS_REGION=").strip()

        config = {
            "access_key":access_key,
            "secret_key":secret_key,
            "region":region
        }

        return config

def get_authenticated_client(config: configparser.ConfigParser, logger: logging.Logger, service: str, **kwargs) -> boto3.client:

    if not config.has_section("aws"):
        logger.error("Cannot create {} client. No AWS credential present in config.".format(service))
        return None

    if not config.has_option("aws", "access_key"):
        logger.error("Cannot create {} client. aws.access_key required config.".format(service))
        return None

    if not config.has_option("aws", "secret_key"):
        logger.error("Cannot create {} client. aws.secret_key required config.".format(service))
        return None

    if not config.has_option("aws", "region"):
        logger.error("Cannot create {} client. aws.region required config.".format(service))
        return None

    boto3.setup_default_session(region_name=config.get("aws", "region"))

    return boto3.client(
        service,
        aws_access_key_id=config.get('aws', 'access_key'),
        aws_secret_access_key=config.get('aws', 'secret_key'),
    )