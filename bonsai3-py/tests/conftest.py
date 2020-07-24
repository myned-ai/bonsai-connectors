"""
Test fixtures
Copyright 2020 Microsoft
"""

import time
from multiprocessing import Process

import pytest
from _pytest.fixtures import FixtureRequest

from bonsai3.simulator_protocol import ServiceConfig
from bonsai3.simulator_protocol import SimulatorInterface, Schema
from bonsai3 import SimulatorSession
from .web_server import start_app


class MinimalSim(SimulatorSession):
    def episode_start(self, config: Schema):
        pass
    def episode_step(self, action: Schema):
        pass
    def get_state(self) -> Schema:
        return {}
    def get_interface(self) -> SimulatorInterface:
        face = SimulatorInterface(self.get_simulator_context())
        return face
    def halted(self) -> bool:
        return False

@pytest.fixture
def minimal_sim():
    config = ServiceConfig(argv=[
        __name__
    ])
    config.server = 'https://testingBonsaiPyClient.bons.ai'
    config.workspace = 'minimal_sim'
    config.access_key = '1111'
    sim = MinimalSim(config)
    return sim

@pytest.fixture
def do_not_retry_sim():
    config = ServiceConfig(argv=[
        __name__
    ])
    config.server = 'https://testingBonsaiPyClient.bons.ai'
    config.workspace = 'no_retry'
    config.access_key = '1111'
    config.retry_timeout_seconds = 0
    sim = MinimalSim(config)
    return sim

@pytest.fixture
def unauthorized_sim():
    config = ServiceConfig()
    config.server = 'http://127.0.0.1:9000'
    config.workspace = 'unauthorized'
    config.access_key = '1111'
    sim = MinimalSim(config)
    return sim

@pytest.fixture
def forbidden_sim():
    config = ServiceConfig()
    config.server = 'http://127.0.0.1:9000'
    config.workspace = 'forbidden'
    config.access_key = '1111'
    sim = MinimalSim(config)
    return sim

@pytest.fixture
def bad_gateway_sim():
    config = ServiceConfig()
    config.server = 'http://127.0.0.1:9000'
    config.workspace = 'badgateway'
    config.access_key = '1111'
    config.retry_timeout_seconds = 0
    sim = MinimalSim(config)
    return sim

@pytest.fixture
def unavailable_sim():
    config = ServiceConfig()
    config.server = 'http://127.0.0.1:9000'
    config.workspace = 'unavailable'
    config.access_key = '1111'
    config.retry_timeout_seconds = 0
    sim = MinimalSim(config)
    return sim

@pytest.fixture
def gateway_timeout_sim():
    config = ServiceConfig()
    config.server = 'http://127.0.0.1:9000'
    config.workspace = 'gatewaytimeout'
    config.access_key = '1111'
    config.retry_timeout_seconds = 0
    sim = MinimalSim(config)
    return sim

@pytest.fixture
def train_sim():
    config = ServiceConfig()
    config.server = 'http://127.0.0.1:9000'
    config.workspace = 'train'
    config.access_key = '1111'
    sim = MinimalSim(config)
    return sim

@pytest.fixture
def flaky_sim():
    config = ServiceConfig()
    config.server = 'http://127.0.0.1:9000'
    config.workspace = 'flaky'
    config.access_key = '1111'
    sim = MinimalSim(config)
    return sim

@pytest.fixture
def internal_server_err_sim():
    config = ServiceConfig()
    config.server = 'http://127.0.0.1:9000'
    config.workspace = '500'
    config.access_key = '1111'
    sim = MinimalSim(config)
    return sim

@pytest.fixture(scope='session', autouse=True)
def start_server_process(request: FixtureRequest):

    proc = Process(target=start_app)
    proc.daemon = True
    proc.start()
    time.sleep(2)

    def fin():
        proc.terminate()

    request.addfinalizer(fin)
