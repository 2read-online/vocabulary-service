"""Configuration"""
from pydantic import BaseSettings, Field


class Config(BaseSettings):
    """App configuration"""
    mongodb_url: str = Field(
        description='MongoDB URL with credentials e.g. mongodb:user:pwd@server:port',
        default='mongodb://root:root@mongo:27017')
    authjwt_secret_key: str = Field(description='Secret key for JWT',
                                    env='secret_key', default='secret')
    deepl_key: str = Field(description='DeepL authentication key', default='xxxxxxx')


CONFIG = Config()
