import sys
import os
import numpy as np
from bonsai3 import ServiceConfig, SimulatorInterface, Schema
from bonsai3_gym import GymSimulator
from bonsai3.logger import Logger


log = Logger()


class MountainCarModel(GymSimulator):
    # Environment name, from openai-gym
    environment_name = 'MountainCar-v0'

    # Simulator name from Inkling
    ### Check how this is linked with inkling ###
    simulator_name = 'MountainCarSimulator'

    def reset(
        self,
        initial_position: float = 0,
        initial_speed: float = 0
    ):

        self.state1 = {"position": initial_position,
                       "speed": initial_speed}
    '''
    convert openai gym observation to our state type
  
    '''

    def gym_to_state(self, observation):
        self.state1 = {"position": observation[0],
                       "speed": observation[1]}

        return self.state1

    def state(self):
        return self.state1

    # convert our action type into openai gym action
    def action_to_gym(self, action):
        actionValue = action['command']
        return actionValue

    # Callbacks

    def get_state(self):
        log.info('get_state: {}   gym_state: {}'.format(
            self.state(), self._env.env.state))
        return self.state()

    def get_interface(self) -> SimulatorInterface:
        interface_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)
                            ), "mountain_car_interface.json"
        )
        return SimulatorInterface(self.get_simulator_context(), interface_file_path)


if __name__ == "__main__":
    config = ServiceConfig(argv=sys.argv)
    log.info("arguments {}".format(sys.argv))
    mountain_car = MountainCarModel(config)
    mountain_car.reset()
    while mountain_car.run():
        continue
