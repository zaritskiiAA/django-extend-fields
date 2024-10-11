import os
from typing import Any
from http import HTTPStatus

from botocore.client import BaseClient
from pydantic import BaseModel, ValidationError, Field

from extends.exceptions import UndefinedMethodError
from .exceptions import DetectorConnectionError, DetectorDataError
from .bases import LanguageDetectorBase, ApiHandler


class LangsModel(BaseModel):
    language: str
    probability: float


class BatchLangsModel(BaseModel):
    index: int
    languages: list[LangsModel]


class AWSLangsModel(LangsModel):
    language: str = Field(alias="LanguageCode")
    probability: float = Field(alias="Score")


class AWSBatchLangsModel(BatchLangsModel):
    index: int = Field(alias="Index")
    languages: list[AWSLangsModel] = Field(alias="Languages")


class AWSLanguageDetector(LanguageDetectorBase, ApiHandler):

    def __init__(self, client: BaseClient) -> None:

        self.client = client
        self._exc = self.client.exceptions

    def validate_response(self, schema: BaseModel, response: list[dict]) -> list[BaseModel]:
        if not isinstance(response, list):
            raise DetectorDataError(
                'AWSLanguageDetector response is not iterable. Cannot be parse.',
            )
        try:
            return [schema.model_validate(data) for data in response]
        except ValidationError as e:
            raise DetectorDataError(
                f'AWSLanguageDetector response cant parse to {schema.__class__.__name__}. Pydantic error: {str(e)}' # noqa E501
            )

    def make_request(self, method: str, **kwargs) -> dict[str, Any]:

        try:
            response = getattr(self.client, method)(**kwargs)
        except (
            self._exc.InvalidRequestException,
            self._exc.InternalServerException,
        ) as e:
            raise DetectorConnectionError(
                f'AWSLanguageDetector request was failed with exception {e}: {e.args}',
            )
        except (
            self._exc.TextSizeLimitExceededException,
            self._exc.BatchSizeLimitExceededException,
        ) as e:
            raise DetectorDataError(
                f'AWSLanguageDetector get text size over limit. AWS error {e}: {e.args}',
            )
        except AttributeError:
            raise UndefinedMethodError(f'AWS client has not method {method}')
        resp_meta = response.get('ResponseMetadata')
        resp_status = resp_meta.get('HTTPStatusCode')
        if resp_status != HTTPStatus.OK:
            raise DetectorConnectionError(f'AWS server response status code {resp_status}')
        return response

    def detect_languages(self, text: str) -> list[AWSLangsModel]:

        response = self.make_request('detect_dominant_language', Text=text)
        return self.validate_response(AWSLangsModel, response.get('Languages'))

    def batch_detect_languages(self, text_list: list[str]):
        response = self.make_request('batch_detect_dominant_language', TextList=text_list)
        return self.validate_response(AWSBatchLangsModel, response.get('ResultList'))


def get_detector(
    client_name: str = "comprehend",
    region_name: str = "us-east-1",
) -> AWSLanguageDetector:

    if not client_name or not region_name:
        raise ValueError(
            (
                'AWSLanguageDetector client must get "client_name", "region_name".'
                'Hand over in get_detector signature or accept the default.'
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
            client_name,
            region_name=region_name,
            aws_access_key_id=pub_key,
            aws_secret_access_key=secret_key,
        )
        return AWSLanguageDetector(client)
    raise AttributeError(f'{required_env} not found in env params.')
