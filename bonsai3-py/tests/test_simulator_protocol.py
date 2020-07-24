"""
Tests for the protocol definitions in the bonsai3 library
"""

#pyright: strict

from bonsai3.simulator_protocol import SimulatorEvent, SimulatorInterface

_MOCK_REGISTRATION_RESPONSE = {
    "sessionId": "0123",
    "interface": {},
    "simulatorContext": {},
    "registrationTime": "2020-01-01T17:24:34.186309100Z",
    "lastSeenTime": "2020-04-20T17:24:34.186309100Z",
    "iterationRate": 0,
    "details": "",
    "sessionStatus": "Attachable",
    "sessionProgress": {}
}

_MOCK_IDLE_RESPONSE = {
    "type": "Idle",
    "sessionId": "0123",
    "sequenceId": "1",
    "idle": {}
}

_MOCK_UNREGISTER_RESPONSE = {
    "type": "Unregister",
    "sessionId": "0123",
    "sequenceId": "1",
    "unregister": {
        "reason": "Finished",
        "details": "Some details"
    }
}

_MOCK_EPISODE_START_RESPONSE = {
    "type": "EpisodeStart",
    "sessionId": "0123",
    "sequenceId": "1",
    "episodeStart": {
        "config": {},
    }
}

_MOCK_EPISODE_STEP_RESPONSE = {
    "type": "EpisodeStep",
    "sessionId": "0123",
    "sequenceId": "1",
    "episodeStep": {
        "action": {},
    }
}

_MOCK_EPISODE_FINISH_RESPONSE = {
    "type": "EpisodeFinish",
    "sessionId": "0123",
    "sequenceId": "1",
    "episodeFinish": {
        "reason": "Unspecified",
    }
}


def test_simulator_event_constructor():
    registration_event = SimulatorEvent(_MOCK_REGISTRATION_RESPONSE)
    assert registration_event.interface is not None
    assert registration_event.simulatorContext is not None
    assert registration_event.registrationTime is not None
    assert registration_event.lastSeenTime is not None
    assert registration_event.iterationRate == 0
    assert registration_event.details == ""
    assert registration_event.sessionStatus == "Attachable"
    assert registration_event.sessionProgress is not None

    idle_event = SimulatorEvent(_MOCK_IDLE_RESPONSE)
    assert idle_event.type == 'Idle'
    assert idle_event.idle is not None

    unregister_event = SimulatorEvent(_MOCK_UNREGISTER_RESPONSE)
    assert unregister_event.type == 'Unregister'
    assert unregister_event.unregister is not None
    assert 'reason' in unregister_event.unregister.__dict__
    assert 'details' in unregister_event.unregister.__dict__

    episode_start_event = SimulatorEvent(_MOCK_EPISODE_START_RESPONSE)
    assert episode_start_event.type == 'EpisodeStart'
    assert episode_start_event.episodeStart is not None
    assert 'config' in episode_start_event.episodeStart.__dict__

    episode_step_event = SimulatorEvent(_MOCK_EPISODE_STEP_RESPONSE)
    assert episode_step_event.type == 'EpisodeStep'
    assert episode_step_event.episodeStep is not None
    assert 'action' in episode_step_event.episodeStep.__dict__

    episode_finish_event = SimulatorEvent(_MOCK_EPISODE_FINISH_RESPONSE)
    assert episode_finish_event.type == 'EpisodeFinish'
    assert episode_finish_event.episodeFinish is not None
    assert 'reason' in episode_finish_event.episodeFinish.__dict__


def test_simulator_protocol_constructor():
    interface = SimulatorInterface()
    assert interface.name == ''
    assert interface.timeout == 0
    # JSON prop dumps it to json so it fails here if it is not valid json
    _ = interface.json


def test_simulator_protocol_sim_context():
    interface = SimulatorInterface(context='foo')
    interface_impl = interface.__getattribute__('_interface')
    assert interface_impl['simulatorContext'] == 'foo'
