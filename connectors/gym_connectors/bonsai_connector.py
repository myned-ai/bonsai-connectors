#!/usr/bin/env python3
import logging
import time
import sys
import signal
from typing import Any, Dict
from types import FrameType

from microsoft_bonsai_api.simulator.client import BonsaiClient, BonsaiClientConfig
from microsoft_bonsai_api.simulator.generated.models import (SimulatorInterface,
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

        unregister(reason: str) -> None
    """

    def __init__(self, simulator, enable_api_logging = False):
        """ Initialize the BonsaiConnector and accepts the simulator
        """
        self.simulator = simulator
        self.enable_api_logging = enable_api_logging

        self.workspace = None
        self.session =  None
        self.session_id = None

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

    def unregister(self, reason: str) -> None:
        """ Called when the simulator should stop 
        """
        self.simulator.unregister(reason)        

    def run(self):
        """ Connects to the Bonsai service processes the command and passes them to the simulator
        """
        config_client = BonsaiClientConfig(enable_logging=self.enable_api_logging)
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

        self.workspace = config_client.workspace
        self.session =  client.session
        self.session_id = session.session_id

        log.info("Registered simulator.")
        sequence_id = 1

        try:
            while True:
                # Advance by the new state depending on the event type

                simulator_state = SimulatorState(
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
                    try:
                        log.info('Idling for {} seconds'.format(event.idle.callback_time))
                        time.sleep(event.idle.callback_time)
                    except AttributeError:
                        # based on MS code, callbacktime is always 0. Sometimes the attribute is missing.
                        # Idle for 0 seconds if attribute is missing.
                        log.info('Received Idle event with missing attribute')
                elif event.type == 'EpisodeStart':
                    self.episode_start(event.episode_start.config)
                elif event.type == 'EpisodeStep':
                    self.episode_step(event.episode_step.action)
                elif event.type == 'EpisodeFinish':
                    self.episode_finish("")
                elif event.type == 'Unregister':
                    log.info("Unregister event received - deleting session")
                    try:
                        client.session.delete(
                            workspace_name = config_client.workspace,
                            session_id = session.session_id)
                    except Exception as err:
                        log.info("An error occured while trying to delete session {}".format(err))
                        
                    log.info("Unregistered simulator.")
                    break
                else:
                    log.info("Unknown event received - type {}".format(event.type))
                    pass
        except KeyboardInterrupt:
            # Gracefully unregister with keyboard interrupt
            self.unregister_simulator("Keyboard interrupt")
            log.info("Unregistered simulator because of keyboard interrupt.")
        except Exception as err:
            log.error("Exception occured: {}. Trying to delete session".format(err))
            # Gracefully unregister for any other exceptions
            self.unregister_simulator("Exception")

        return False
    
    def unregister_simulator(self, reason:str) -> None:
        ''' Called when received Unregister event, keyboard interrupt or SIGTERM
            It will try to delete the session and call the simulator's unregister method
        '''
        log.info("Unregister event received - deleting session")
        try:
            self.session.delete(
                workspace_name = self.workspace,
                session_id = self.session_id)

            #tell simulator to unregister
            self.unregister(reason)

        except Exception as err:
            log.info("An error occured while trying to delete session {}".format(err))


def handle_SIGTERM(signalType: int, frame: FrameType, bonsaiConnector: BonsaiConnector) -> None:
    """Unregisters the simulator when a SIGTERM signal is detected """
    bonsaiConnector.unregister("Unregistering because SIGTERM signal")
    sys.exit()