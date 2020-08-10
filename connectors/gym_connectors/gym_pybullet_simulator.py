import argparse
import json
import logging
import os
from time import sleep, time
from typing import Any, Dict

import gym
import pybulletgym
from .gym_simulator import GymSimulator

log = logging.getLogger("PyBulletSimulator")
log.setLevel(level='INFO')


class PyBulletSimulator(GymSimulator):
    """ GymSimulator class

        End users should subclass GymSimulator to interface OpenAI Gym
        environments to the Bonsai platform. The derived class should provide 
        the mapping between Bonsai and OpenAI environment's action and states and
        specify the name of the OpenAI environemnt
    """

    environment_name = ''  # name of the OpenAI Gym environment specified in derived class

    def __init__(self, iteration_limit=200, skip_frame=1):
        """ Initializes the PyBulletSimulator object
        """
        super().__init__(iteration_limit, skip_frame)

    def make_environment(self, headless):
        log.debug("Making PyBullet environment {}...".format(self.environment_name))
        self._env = gym.make(self.environment_name)
        if not headless:
            self._env.render()
            self._env.reset()
