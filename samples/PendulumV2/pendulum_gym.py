import sys
import os
import numpy as np
import logging as log

from typing import Dict, Any, Optional

from gymsimulator import SimModel
from gymsimulator import GymSimulator

#log = Logger()


class PendulumModel(GymSimulator):
    # Environment name, from openai-gym
    environment_name = 'Pendulum-v0'

    def __init__(self, sim_model, iteration_limit=200, skip_frame=1):
      #  log.set_enabled("debug", True)
        # send this class instance to the sim_model
        sim_model.attach(self)

        self.bonsai_state = {"cos_theta": 0.0,
                             "sin_theta": 0.0,
                             "angular_velocity": 0.0}

        super().__init__(sim_model, iteration_limit, skip_frame)

    # convert openai gym observation to our state type

    def gym_to_state(self, observation):
        self.bonsai_state = {"cos_theta": float(observation[0]),
                             "sin_theta": float(observation[1]),
                             "angular_velocity": float(observation[2])}

        return self.bonsai_state

    def state(self):
        return self.bonsai_state

    # convert our action type into openai gym action
    def action_to_gym(self, action: Dict[str, Any]):
        actionValue = action['command']
        return [actionValue]

    def gym_episode_start(self, config: Dict[str, Any]):
        """
        called during episode_start() to return the initial observation
        after reseting the gym environment. clients can override this
        to provide additional initialization.
        """
        super().gym_episode_start(config)

        initial_theta = config.get(
            "initial_theta", self._env.unwrapped.state[0])
        initial_angular_velocity = config.get(
            "initial_angular_velocity", self._env.unwrapped.state[1])

        # set the environment state
        self._env.unwrapped.state = np.array(
            [initial_theta, initial_angular_velocity])

        # set the bonsai state
        self.bonsai_state = {"cos_theta": float(np.cos(initial_theta)),
                             "sin_theta": float(np.sin(initial_theta)),
                             "angular_velocity": float(initial_angular_velocity)}

        # return the initial observation
        return np.array([np.cos(initial_theta), np.sin(initial_theta), initial_angular_velocity])

    # Callbacks

    def get_state(self):
        log.debug('get_state: {}'.format(self.state()))
        return self.state()


if __name__ == "__main__":
  #  config = ServiceConfig(argv=sys.argv)
  #  log.debug("arguments {}".format(sys.argv))
    simmodel = SimModel()
    pendulum = PendulumModel(simmodel)

    while pendulum.run():
        continue
