import logging
from typing import Any, Dict
import gym

from obswrapper import ObsWrapper
from gym_connectors import BonsaiConnector, GymSimulator

log = logging.getLogger("carrace")


class CarRacing(GymSimulator):
    """ Implements the methods specific to Open AI Gym CarRacing environment 
    """

    environment_name = 'CarRacing-v0'      # Environment name, from openai-gym

    def __init__(self, iteration_limit=200, skip_frame=1):
        """ Initializes the CarRacing environment
        """
        self.bonsai_state = None

        super().__init__(iteration_limit, skip_frame)

    def make_environment(self, headless):

        self._env = ObsWrapper(gym.make(self.environment_name))

    def gym_to_state(self, state):
        """ Converts openai environment observation to Bonsai state, as defined in inkling
        """
        reward = self._env.unwrapped.reward

        self.bonsai_state = {"obs": state.reshape(-1).tolist(),
                             "rew": reward}

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


if __name__ == "__main__":
    """ Creates a CarRacing environment, passes it to the BonsaiConnector 
        that connects to the Bonsai service that can use it as a simulator  
    """
    logging.basicConfig()
    log = logging.getLogger("carracing")
    log.setLevel(level='DEBUG')

    # if more information is needed, uncomment this
    #gymlog = logging.getLogger("GymSimulator")
    # gymlog.setLevel(level='DEBUG')

    carracing = CarRacing()
    connector = BonsaiConnector(carracing)

    while connector.run():
        continue
