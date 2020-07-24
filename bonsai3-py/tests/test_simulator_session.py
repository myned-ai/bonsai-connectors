"""
Tests for simulator_session.py
Copyright 2020 Microsoft
"""

#pyright: strict
from typing import Any
from unittest.mock import Mock, patch

import pytest
import requests

from bonsai3.simulator_session import SimulatorSession, log

log.set_enabled("debug")

@patch('requests.Session.put')
def test_http_req_raises_error_request_exception(put_mock: Mock, minimal_sim: SimulatorSession):
    put_mock.side_effect = requests.exceptions.RequestException()
    with pytest.raises(requests.exceptions.RequestException):
        minimal_sim.run()

def test_401_error_registration(unauthorized_sim: SimulatorSession, capsys: Any):
    unauthorized_sim.run()
    captured = capsys.readouterr()
    assert '401' in captured.err

def test_403_error_registration(forbidden_sim: SimulatorSession, capsys: Any):
    forbidden_sim.run()
    captured = capsys.readouterr()
    assert '403' in captured.err

def test_502_raises_retry_exception(bad_gateway_sim: SimulatorSession, capsys: Any):
    bad_gateway_sim.run()
    captured = capsys.readouterr()
    assert '502' in captured.err
    assert 'Simulator Retry time exceeded' in captured.err

def test_503_raises_retry_exception(unavailable_sim: SimulatorSession, capsys: Any):
    unavailable_sim.run()
    captured = capsys.readouterr()
    assert '503' in captured.err
    assert 'Simulator Retry time exceeded' in captured.err

def test_504_raises_retry_exception(gateway_timeout_sim: SimulatorSession, capsys: Any):
    gateway_timeout_sim.run()
    captured = capsys.readouterr()
    assert '504' in captured.err
    assert 'Simulator Retry time exceeded' in captured.err

def test_training(train_sim: SimulatorSession):
    counter = 0
    while train_sim.run():
        if counter == 100:
            break
        counter += 1

@patch('time.sleep', return_value=None)
def test_flaky_sim(patched_sleep: Mock, flaky_sim: SimulatorSession, capsys: Any):
    counter = 0
    while flaky_sim.run():
        if counter == 100:
            break
        counter += 1
    captured = capsys.readouterr()
    assert 'Retrying request' in captured.err

def test_500_err_sim(internal_server_err_sim: SimulatorSession):
    """ Test that a 500 during get next event ends sim loop """
    counter = 0
    while internal_server_err_sim.run():
        if counter == 100:
            # Avoid infinite simulation loops and fail
            assert False
        counter += 1

def test_unregister_only_called_once(internal_server_err_sim: SimulatorSession, capsys: Any):
    """ Test to check that unregister is only called once during training """
    counter = 0
    while internal_server_err_sim.run():
        if counter == 100:
            # Avoid infinite simulation loops and fail
            assert False
        counter += 1
    captured = capsys.readouterr()
    assert captured.err.count('Attempting to unregister simulator') == 1

@patch('time.sleep', return_value=None)
@patch('requests.Session.post')
def test_http_req_timeout_error_raises_retry_exception(
        put_mock: Mock,
        patched_sleep: Mock,
        do_not_retry_sim: SimulatorSession,
        capsys: Any):
    put_mock.side_effect = requests.exceptions.Timeout()
    do_not_retry_sim.run()
    captured = capsys.readouterr()
    assert 'Simulator Retry time exceeded' in captured.err
