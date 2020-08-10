import logging
from typing import Any, Dict
import json
import gym
import pybulletgym

import numpy as np
from gym_connectors import BonsaiConnector, PyBulletSimulator

log = logging.getLogger("hopper")


class Hopper(PyBulletSimulator):
    """ Implements the methods specific to Hopper environment
    """

    environment_name = 'HopperPyBulletEnv-v0'  # Environment name, from openai-gym

    def __init__(self, iteration_limit=200, skip_frame=1):
        """ Initializes the Hopper environment
        """

        self.bonsai_state = {"obs": [0.0]}

        super().__init__(iteration_limit, skip_frame)

    def gym_to_state(self, state) -> Dict[str, Any]:
        """ Converts openai environment state to Bonsai state, as defined in inkling
        """
        self.bonsai_state = {"obs": state.tolist(),
                             "rew": self.get_last_reward()}

        return self.bonsai_state

    def action_to_gym(self, action: Dict[str, Any]):
        """ Converts Bonsai action type into openai environment action.
        """
        j1 = action['j1']
        j2 = action['j2']
        j3 = action['j3']

        # Hopper environment expects an array of actions
        return [j1, j2, j3]

    def get_state(self) -> Dict[str, Any]:
        """ Returns the current state of the environment
        """
        log.debug('get_state: {}'.format(self.bonsai_state))
        return self.bonsai_state


if __name__ == "__main__":
    """ Creates a Pendulum environment, passes it to the BonsaiConnector 
        that connects to the Bonsai service that can use it as a simulator  
    """
    logging.basicConfig()
    log = logging.getLogger("hopper")
    log.setLevel(level='DEBUG')

    # TO DO: Issue With Uncommending The DEBUG on Hopper Environmnet
    # Bonsai returns: INFO:BonsaiConnector:Unregistered simulator because: 'HopperBulletEnv' object has no attribute 'state'

    # if more information is needed, uncomment this
    # gymlog = logging.getLogger("GymSimulator")
    # gymlog.setLevel(level='DEBUG')

    hopper = Hopper()
    connector = BonsaiConnector(hopper)

    while connector.run():
        continue
