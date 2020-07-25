#!/usr/bin/env python3
import os
import sys
import json
import time
from typing import Dict, Any, Optional
from microsoft_bonsai_api.client import BonsaiClientConfig, BonsaiClient
from microsoft_bonsai_api.simulator.models import (
    SimulatorState,
    SimulatorInterface,
)

class SimModel():
        
    def attach(self, simulator_session):
        self.simulator_session = simulator_session

    def get_state(self):
       return self.simulator_session.get_state()

    def get_interface(self) -> Dict[str, Any]:
        return self.simulator_session.get_interface()

    def halted(self)->bool:
        """
        Should return weather the episode is halted, and
        no further action will result in a state.
        """
        return self.simulator_session.halted()

    def episode_start(self, config: Dict[str, Any]):
        """ 
        Called at the start of each episode 
        """
        self.simulator_session.episode_start(config)

    def episode_step(self, action: Dict[str, Any]):
        """ 
        Called for each step of the episode 
        """
        self.simulator_session.episode_step(action)

    def run(self):
        config_client = BonsaiClientConfig(enable_logging=True)
        client = BonsaiClient(config_client)

        # Load json file as simulator integration config type file
        interface = self.get_interface()

        # Create simulator session and init sequence id
        registration_info = SimulatorInterface(
                                name=interface['name'], 
                                timeout=interface['timeout'], 
                                simulator_context=config_client.simulator_context, 
        )

        # Registers a simulator with Bonsai platform
        registered_session = client.session.create(
                                workspace_name=config_client.workspace, 
                                body=registration_info
        )
        print("Registered simulator.")
        registration_info
        sequence_id = 1
            
        try:
            while True:
                # Advance by the new state depending on the event type

                sim_state = SimulatorState(
                                session_id=registered_session.session_id,
                                sequence_id=sequence_id, state=self.get_state(), 
                                halted=self.halted()
                )
                event = client.session.advance(
                            workspace_name=config_client.workspace, 
                            session_id=registered_session.session_id, body=sim_state
                )
                sequence_id = event.sequence_id
                print("[{}] Last Event: {}".format(time.strftime('%H:%M:%S'), 
                                                event.type))

                # Event loop
                if event.type == 'Idle':
                    time.sleep(event.idle.callback_time)
                    print('Idling...')
                elif event.type == 'EpisodeStart':
                    self.episode_start(event.episode_start.config)
                elif event.type == 'EpisodeStep':
                    self.episode_step(event.episode_step.action)
                elif event.type == 'EpisodeFinish':
                    print('Episode Finishing...')
                elif event.type == 'Unregister':
                    client.session.delete(
                        workspace_name=config_client.workspace, 
                        session_id=registered_session.session_id
                    )
                    print("Unregistered simulator.")
                else:
                    pass
        except KeyboardInterrupt:
            # Gracefully unregister with keyboard interrupt
            client.session.delete(
                workspace_name=config_client.workspace, 
                session_id=registered_session.session_id
            )
            print("Unregistered simulator.")
        except Exception as err:
            # Gracefully unregister for any other exceptions
            client.session.delete(
                workspace_name=config_client.workspace, 
                session_id=registered_session.session_id
            )
            print("Unregistered simulator because: {}".format(err))  