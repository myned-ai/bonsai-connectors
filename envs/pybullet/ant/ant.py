import logging
from typing import Any, Dict
import json
import gym
import pybulletgym

import numpy as np
from gym_connectors import BonsaiConnector, PyBulletSimulator

log = logging.getLogger("ant")


class Ant(PyBulletSimulator):
    """ Implements the methods specific to Ant environment
    """

    environment_name = 'AntPyBulletEnv-v0'  # Environment name, from openai-gym

    def __init__(self, iteration_limit=200, skip_frame=1):
        """ Initializes the Ant environment
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
        j4 = action['j4']
        j5 = action['j5']
        j6 = action['j6']
        j7 = action['j7']
        j8 = action['j8']

        # Reacher environment expects an array of actions
        return [j1, j2, j3, j4, j5, j6, j7, j8]

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
    log = logging.getLogger("ant")
    log.setLevel(level='DEBUG')

    # TO DO: Issue With Uncommending The DEBUG on Reacher Environmnet
    # Bonsai returns: INFO:BonsaiConnector:Unregistered simulator because: 'ReacherBulletEnv' object has no attribute 'state'

    # if more information is needed, uncomment this
    # gymlog = logging.getLogger("GymSimulator")
    # gymlog.setLevel(level='DEBUG')

    ant = Ant()
    connector = BonsaiConnector(ant)

    while connector.run():
        continue
