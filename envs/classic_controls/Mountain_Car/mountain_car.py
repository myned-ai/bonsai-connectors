import numpy as np
import logging as log

from typing import Dict, Any

from gym_connectors import BonsaiConnector
from gym_connectors import GymSimulator

#log = Logger()


class MountainCar(GymSimulator):
    # Environment name, from openai-gym
    environment_name = 'MountainCar-v0'

    def __init__(self, iteration_limit=200, skip_frame=1):

        self.bonsai_state = {"position": 0.0,
                             "speed": 0.0}

        super().__init__(iteration_limit, skip_frame)

    # convert openai gym observation to our state type

    def gym_to_state(self, observation):
        self.bonsai_state = {"position": float(observation[0]),
                             "speed": float(observation[1])}

        return self.bonsai_state

    def state(self):
        return self.bonsai_state

    # convert our action type into openai gym action
    def action_to_gym(self, action: Dict[str, Any]):
        actionValue = action['command']
        return actionValue

    # Callbacks

    def get_state(self):
        log.info('get_state: {}   gym_state: {}'.format(
            self.state(), self._env.env.state))
        return self.state()


if __name__ == "__main__":
  #  config = ServiceConfig(argv=sys.argv)
  #  log.info("arguments {}".format(sys.argv))
    mountain_car = MountainCar()
    connector = BonsaiConnector(mountain_car)
    while connector.run():
        continue
