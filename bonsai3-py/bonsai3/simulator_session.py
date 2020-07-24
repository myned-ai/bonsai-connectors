"""
Simulator session base class for bonsai3 library
"""
__copyright__ = "Copyright 2020, Microsoft Corp."

# pyright: strict

import abc
from typing import Optional

import jsons

from .exceptions import RetryTimeoutError, ServiceError
from .logger import Logger
from .simulator_protocol import (
    Schema,
    ServiceConfig,
    SimulatorEvent,
    SimulatorEventRequest,
    SimulatorEventType,
    SimulatorInterface,
)
from .simulator_client import SimulatorClient

log = Logger()


class SimulatorSession:
    _config = ServiceConfig()  # type: ServiceConfig
    _last_event = None  # type: Optional[SimulatorEvent]

    def __init__(self, config: ServiceConfig):
        self._last_event = None
        self._config = config
        self._client = SimulatorClient(config)

    # interface and state
    def get_state(self) -> Schema:
        """Called to retreive the current state of the simulator. """
        raise NotImplementedError("get_state not implemented.")

    def get_interface(self) -> SimulatorInterface:
        """Called to retreive the simulator interface during registration. """
        raise NotImplementedError("get_interface not implemented.")

    def get_simulator_context(self) -> str:
        """
        Called to retrieve the simulator context field for the SimulatorInterface.
        """
        return self._config.simulator_context or ""

    def halted(self) -> bool:
        """
        Should return weather the episode is halted, and
        no further action will result in a state.
        """
        raise NotImplementedError("halted not implemented.")

    # callbacks
    def registered(self):
        """Called after simulator is successfully registered. """
        log.info("Registered.")
        pass

    @abc.abstractmethod
    def episode_start(self, config: Schema) -> None:
        """Called at the start of each episode. """
        raise NotImplementedError("episode_start not implemented.")

    @abc.abstractmethod
    def episode_step(self, action: Schema) -> None:
        """Called for each step of the episode. """
        raise NotImplementedError("episode_step not implemented.")

    def episode_finish(self, reason: str) -> None:
        """Called at the end of an episode. """
        pass

    # TODO
    # def playback_start(self, config: dict):
    # def playback_step(self, action: dict, stateDescription: dict, action: dict):
    # def playback_finish(self):

    def idle(self, callbackTime: int):
        """Called when the simulator should idle and perform no action. """
        log.info("Idling...")
        pass

    def unregistered(self, reason: str):
        """Called when the simulator has been unregistered and should exit. """
        log.info("Unregistered.")
        pass

    # main entrypoint for driving the simulation
    def run(self) -> bool:
        """
        Runs simulator. Returns false when the simulator should exit.

        Example usage:
            ...
            mySim = MySimulator(config)
            while mySim.run():
                continue
            ...

        returns True if the simulator should continue.
        returns False if the simulator should exit its simulation loop.
        """
        # Flag to attempt to unregister sim on errors in SDK
        unregister = False
        try:
            keep_going = False
            if self._last_event:
                log.info("Last Event: {}".format(self._last_event.type))
            # if we've never gotten an event, register
            if self._last_event is None:
                self._last_event = self._client.register_simulator(self.get_interface())

            # ...use the last event to request the next event
            else:
                event_request = SimulatorEventRequest()
                event_request.sessionId = self._last_event.sessionId
                event_request.sequenceId = self._last_event.sequenceId
                event_request.halted = self.halted()
                event_request.state = self.get_state()
                log.debug("Event Request: {}".format(event_request.__dict__))
                self._last_event = self.get_next_event(event_request)

            # if we have an event, dispatch it
            if self._last_event:
                keep_going = self._dispatch_event(self._last_event)

                # clear the last event if we should not keep going
                if keep_going is False:
                    self._last_event = None

            return keep_going
        except KeyboardInterrupt:
            unregister = True
        except ServiceError as err:
            unregister = True
            log.error(err)
        except RetryTimeoutError as err:
            unregister = True
            log.error(err)
        except Exception as err:
            unregister = True
            log.error("Exiting due to the following error: {}".format(err))
            raise err
        finally:
            if self._last_event is not None and unregister:
                try:
                    log.debug("Attempting to unregister simulator.")
                    self._client.unregister_simulator(self._last_event.sessionId)
                    log.debug("Successfully unregistered simulator.")
                except Exception as err:
                    log.error("Unregister simulator failed with error: {}".format(err))
        return False

    # implementation
    def _event_from_json(self, json_text: str) -> SimulatorEvent:
        """Converts a json string into a SimulatorEvent."""
        event_dict = jsons.loads(json_text)
        log.debug("Event Response: {}".format(event_dict))
        return SimulatorEvent(event_dict)

    def get_next_event(self, event_request: SimulatorEventRequest) -> SimulatorEvent:
        """Requests the next event in the simulation.

        Parameters
        ----------
        event_request: SimulatorEventRequest

        Returns
        -------
        SimulatorEvent
        """
        return self._client.get_next_event(event_request)

    def _dispatch_event(self, event: SimulatorEvent) -> bool:
        """
            Examines the SimulatorEvent and calls one of the
            dispatch functions for the appropriate event.

            return false if there are no more events.
        """

        if event.type == SimulatorEventType.Registered.name:
            self.registered()

        elif event.type == SimulatorEventType.EpisodeStart.name and event.episodeStart:
            self.episode_start(event.episodeStart.config)

        elif event.type == SimulatorEventType.EpisodeStep.name and event.episodeStep:
            self.episode_step(event.episodeStep.action)

        elif (
            event.type == SimulatorEventType.EpisodeFinish.name and event.episodeFinish
        ):
            self.episode_finish(event.episodeFinish.reason)

        elif event.type == SimulatorEventType.Idle.name and event.idle:
            try:
                self.idle(event.idle.callbackTime)
            except AttributeError:
                # callbacktime is always 0. Sometimes the attribute is missing.
                # Idle for 0 seconds if attribute is missing.
                self.idle(0)

        elif event.type == SimulatorEventType.Unregister.name and event.unregister:
            self.unregistered(event.unregister.reason)
            return False

        return True
