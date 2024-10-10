import os
from typing import Any
from http import HTTPStatus

from botocore.client import BaseClient
from pydantic import BaseModel, ValidationError

from .exceptions import DetectorConnectionError, DetectorDataError
from .bases import LanguageDetectorBase, ApiHandler


class LangsModel(BaseModel):
    language: str
    probability: float


class AWSLanguageDetector(LanguageDetectorBase, ApiHandler):

    def __init__(self, client: BaseClient) -> None:

        self.client = client
        self._exc = self.client.exceptions

    def validate_response(self, response: list[dict]) -> list[LangsModel]:

        if not isinstance(response, list):
            raise DetectorDataError(
                'AWSLanguageDetector response is not iterable. Cannot be parse.',
            )
        try:
            return [
                LangsModel(language=data.get('LanguageCode'), probability=data.get('Score'))
                for data in response
            ]
        except ValidationError as e:
            raise DetectorDataError(
                f'AWSLanguageDetector response cant parse to LangsModel. Pydantic error: {str(e)}'
            )

    def make_request(self, **kwargs) -> dict[str, Any]:

        try:
            response = self.client.detect_dominant_language(**kwargs)
        except (
            self._exc.InvalidRequestException,
            self._exc.InternalServerException,
        ) as e:
            raise DetectorConnectionError(
                f'AWSLanguageDetector request was failed with exception {e}: {e.args}',
            )
        except self._exc.TextSizeLimitExceededException as e:
            raise DetectorDataError(
                f'AWSLanguageDetector get text size over limit. AWS error {e}: {e.args}',
            )

        resp_meta = response.get('ResponseMetadata')
        resp_status = resp_meta.get('HTTPStatusCode')

        if resp_status != HTTPStatus.OK:
            raise DetectorConnectionError(f'AWS server response status code {resp_status}')

        return response

    def detect_languages(self, text: str) -> list[LangsModel]:

        response = self.make_request(Text=text)
        return self.validate_response(response.get('Languages'))
    

def get_detector(
    client_name: str = "comprehend", region_name: str = "us-east-1",
) -> AWSLanguageDetector:
    
    if not client_name or not region_name:
        raise ValueError(
            (
                f'AWSLanguageDetector client must get "client_name", "region_name".'
                f'Hand over in get_detector signature or accept the default.'
            )
        )
    
    required_env = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]

    if pub_key := os.getenv("AWS_ACCESS_KEY_ID"):
        required_env.remove("AWS_ACCESS_KEY_ID")

    if secret_key := os.getenv("AWS_SECRET_ACCESS_KEY"):
        required_env.remove("AWS_SECRET_ACCESS_KEY")

    if not required_env:

        import boto3
        client = boto3.client(
            client_name, region_name=region_name, 
            aws_access_key_id=pub_key, aws_secret_access_key=secret_key,
        )
        return AWSLanguageDetector(client)
    raise AttributeError(f'{required_env} not found in env params.')