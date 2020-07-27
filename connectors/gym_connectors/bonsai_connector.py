#!/usr/bin/env python3
import logging
import time
from typing import Any, Dict

from microsoft_bonsai_api.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.models import (SimulatorInterface,
                                                   SimulatorState)

log = logging.getLogger("BonsaiConnector")
log.setLevel(level='INFO')

class BonsaiConnector:
    """ Encapsulates the communication with Bonsai service and 
        forwards the commands to the simulator that is injected through the constructor

        The simulator class has to implement the following methods

        get_state(self) -> Dict[str, Any]:

        get_interface(self) -> Dict[str, Any]:

        halted(self) -> bool:

        episode_start(self, config: Dict[str, Any]) -> None:

        episode_step(self, action: Dict[str, Any]) -> None:

        episode_finish(self, reason: str) -> None:
    """

    def __init__(self, simulator):
        """ Initialize the BonsaiConnector and accepts the simulator
        """
        self.simulator = simulator

    def get_state(self) -> Dict[str, Any]:
        """ Returns the current state of the simulator
        """
        return self.simulator.get_state()

    def get_interface(self) -> Dict[str, Any]:
        """ Returns the dictionary of the values from the interface file
            that defines states, actions and initial values
        """
        return self.simulator.get_interface()

    def halted(self) -> bool:
        """ Returns weather the episode is halted, and
            no further action will result in a state.
        """
        return self.simulator.halted()

    def episode_start(self, config: Dict[str, Any]) -> None:
        """ Called at the start of each episode 
        """
        self.simulator.episode_start(config)

    def episode_step(self, action: Dict[str, Any]) -> None:
        """ Called for each step of the episode 
        """
        self.simulator.episode_step(action)

    def episode_finish(self, reason: str) -> None:
        """ Called at the end of each episode 
        """
        self.simulator.episode_finish(reason)

    def run(self):
        """ Connects to the Bonsai service processes the command and passes them to the simulator
        """
        config_client = BonsaiClientConfig()
        client = BonsaiClient(config_client)

        # Load json file as simulator integration config type file
        interface = self.get_interface()

        simulator_interface = SimulatorInterface(
            name = interface['name'],
            timeout = interface['timeout'],
            simulator_context = config_client.simulator_context,
        )

        # Registers a simulator with Bonsai platform
        session = client.session.create(
            workspace_name = config_client.workspace,
            body = simulator_interface
        )

        log.info("Registered simulator.")
        sequence_id = 1

        try:
            while True:
                # Advance by the new state depending on the event type

                simulator_state = SimulatorState(
                    session_id = session.session_id,
                    sequence_id =sequence_id, 
                    state = self.get_state(),
                    halted = self.halted()
                )
                event = client.session.advance(
                    workspace_name = config_client.workspace,
                    session_id = session.session_id, 
                    body = simulator_state
                )
                sequence_id = event.sequence_id
                
                log.debug("[{}] Last Event: {}".format(time.strftime('%H:%M:%S'), event.type))

                # Event loop
                if event.type == 'Idle':
                    time.sleep(event.idle.callback_time)
                    log.info('Idling...')
                elif event.type == 'EpisodeStart':
                    self.episode_start(event.episode_start.config)
                elif event.type == 'EpisodeStep':
                    self.episode_step(event.episode_step.action)
                elif event.type == 'EpisodeFinish':
                    self.episode_finish("")
                elif event.type == 'Unregister':
                    client.session.delete(
                        workspace_name = config_client.workspace,
                        session_id = session.session_id
                    )
                    log.info("Unregistered simulator.")
                else:
                    pass
        except KeyboardInterrupt:
            # Gracefully unregister with keyboard interrupt
            client.session.delete(
                workspace_name =config_client.workspace,
                session_id = session.session_id
            )
            log.info("Unregistered simulator.")
        except Exception as err:
            # Gracefully unregister for any other exceptions
            client.session.delete(
                workspace_name = config_client.workspace,
                session_id = session.session_id
            )
            log.info("Unregistered simulator because: {}".format(err))
