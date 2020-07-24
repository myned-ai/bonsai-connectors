"""
Tests for ServiceConfig class
Copyright 2020 Microsoft
"""

from bonsai3.simulator_protocol import ServiceConfig
from unittest.mock import patch


def test_default_config():
    config = ServiceConfig()
    assert config.workspace == ''


def test_config_reads_env_vars():
    with patch.dict('os.environ', 
                    {'SIM_ACCESS_KEY': '111',
                     'SIM_API_HOST': 'https://bonsai-api.com',
                     'SIM_WORKSPACE': '777',
                     'SIM_CONTEXT': 'TRAIN'}):
        config = ServiceConfig()
        assert config.access_key == '111'
        assert config.server == 'https://bonsai-api.com'
        assert config.workspace == '777'

def test_config_reads_args():
    config = ServiceConfig(argv=[
        __name__,
        '--accesskey', '111',
        '--api-host', 'host',
        '--workspace', 'test',
        '--sim-context', 'context',
        '--retry-timeout', '30'
    ])
    assert config.access_key == '111'
    assert config.server == 'host'
    assert config.workspace == 'test'
    assert config.simulator_context == 'context'
    assert config.retry_timeout_seconds == 30
