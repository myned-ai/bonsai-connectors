
import sys
from bonsai3 import SimulatorSession, SimulatorInterface, ServiceConfig, Schema

class SimModel(SimulatorSession):
        
    def attach(self, simulator_session):
        self.simulator_session = simulator_session

    def get_state(self) -> Schema:
       return self.simulator_session.get_state()

    def get_interface(self) -> SimulatorInterface:
        return self.simulator_session.get_interface()

    def halted(self)->bool:
        """
        Should return weather the episode is halted, and
        no further action will result in a state.
        """
        return self.simulator_session.halted()

    def episode_start(self, config: Schema):
        """ 
        Called at the start of each episode 
        """
        self.simulator_session.episode_start(config)

    def episode_step(self, action: Schema):
        """ 
        Called for each step of the episode 
        """
        self.simulator_session.episode_step(action)