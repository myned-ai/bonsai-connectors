import logging
from typing import Any, Dict
import gym
import numpy as np

from obswrapper import ObsWrapper
from gym_connectors import BonsaiConnector, GymSimulator

log = logging.getLogger("carracing")


class CarRacing(GymSimulator):
    """ Implements the methods specific to Open AI Gym CarRacing environment 
    """

    environment_name = 'CarRacing-v0'      # Environment name, from openai-gym

    def __init__(self, iteration_limit=200, skip_frame=1):
        """ Initializes the CarRacing environment
        """
        self.bonsai_state = {"obs": [],
                        "x": 0.0,
                        "y": 0.0,
                        "length": 0,
                        "progress": 0.0,
                        "grass_driving_r": 0.0,
                        "grass_driving_g": 0.0,
                        "grass_driving_b": 0.0}
        self.prev_count = None

        super().__init__(iteration_limit, skip_frame)

    def make_environment(self, headless):

        self._env = ObsWrapper(gym.make(self.environment_name))

    def gym_to_state(self, state):
        """ Converts openai environment observation to Bonsai state, as defined in inkling
        """
        x, y = self._env.unwrapped.car.hull.position

        grass_driving_r = state['grass_driving_r']
        grass_driving_g = state['grass_driving_g']
        grass_driving_b = state['grass_driving_b']

        obs = state['obs'].reshape(-1) / 255.0

        length = len(self._env.unwrapped.track)

        count = self._env.unwrapped.tile_visited_count

        progress = count - self.prev_count

        self.bonsai_state = {"obs": obs.tolist(),
                             "x": x,
                             "y": y,
                             "length": length,
                             "progress": progress,
                             "grass_driving_r": grass_driving_r,
                             "grass_driving_g": grass_driving_g,
                             "grass_driving_b": grass_driving_b}

        self.prev_count = count

        return self.bonsai_state

    def action_to_gym(self, action):
        """ Converts Bonsai action type into openai environment action.       
        """
        j1 = action['steer']
        j2 = action['gas']
        j3 = action['break']

        return [j1, j2, j3]

    def get_state(self) -> Dict[str, Any]:
        """ Returns the current state of the environment 
        """
        log.debug('get_state: {}'.format(self.bonsai_state))
        return self.bonsai_state

    def episode_start(self, config: Dict[str, Any] = None) -> None:

        self.prev_count = 0
        super().episode_start(config)


if __name__ == "__main__":
    """ Creates a CarRacing environment, passes it to the BonsaiConnector 
        that connects to the Bonsai service that can use it as a simulator  
    """
    logging.basicConfig()
    log = logging.getLogger("carracing")
    log.setLevel(level='DEBUG')

    # if more information is needed, uncomment this
    gymlog = logging.getLogger("GymSimulator")
    gymlog.setLevel(level='DEBUG')

    gymlog = logging.getLogger("BonsaiConnector")
    gymlog.setLevel(level='DEBUG')

    carracing = CarRacing()
    connector = BonsaiConnector(carracing, True)

    while connector.run():
        continue
