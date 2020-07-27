import argparse
import json
import logging
import os
from time import sleep, time
from typing import Any, Dict

import gym

log = logging.getLogger("GymSimulator")
log.setLevel(level='INFO')

class GymSimulator:
    """ GymSimulator class

        End users should subclass GymSimulator to interface OpenAI Gym
        environments to the Bonsai platform. The derived class should provide 
        the mapping between Bonsai and OpenAI environment's action and states and
        specify the name of the OpenAI environemnt
    """

    environment_name = ''  # name of the OpenAI Gym environment specified in derived class

    def __init__(self, iteration_limit=200, skip_frame=1):
        """ Initializes the GymSimulator object
        """
        # create the gym environment
        log.info("Creating {} environment".format(self.environment_name))

        self._env = gym.make(self.environment_name)

        self.finished = False
        self.episode_count = 0
        self.episode_reward = 0
        self.iteration_count = 0

        # parse optional command line arguments
        cli_args = self.parse_arguments()
        if cli_args is not None:
            self._headless = cli_args.headless

        # optional parameters for controlling the simulation
        self._iteration_limit = iteration_limit    

        # default is to process every frame
        self._skip_frame = skip_frame    

        # random seed
        self._env.seed(20)
        self._env.reset()

        # book keeping for rate status
        self._log_interval = 10.0  # seconds
        self._last_status = time()

    def gym_to_state(self, observation) -> None:
        """Convert an openai environment observation into an Bonsai state

        Example:
            state = {'position': observation[0],
                     'velocity': observation[1],
                     'angle':    observation[2]}
            return state
        """
        return None

    def action_to_gym(self, action):
        """Converts an Bonsai action into a openai environemnt action type and returns it
        """
        return action['command']

    def gym_episode_start(self, config: Dict[str, Any]):
        """ Called during episode_start() to return the initial observation
        after reseting the gym environment. clients can override this
        to provide additional initialization.
        """
        observation = self._env.reset()

        return observation

    def episode_start(self, config: Dict[str, Any]) -> None:
        """ Called at the start of each new episode
            Initializes the iteration count, reward, finished variables 
            and the initial state of the simulator (environment)

            If the episode_iteration_limit was set in the lesson, 
            its value would be used to limit the iteration count in this episode
        """
        log.info("- - - - - - - - - - - - - - - - - - -- - - - - -- ")
        log.info("--EPISODE {} START-- ".format(self.episode_count))

        self._iteration_limit = config.get(
            "episode_iteration_limit", self._iteration_limit)

        self.finished = False
        self.iteration_count = 0
        self.episode_reward = 0

        # reset the environment and set the initial observation
        observation = self.gym_episode_start(config)
        self.gym_to_state(observation)

    def gym_simulate(self, gym_action):
        """Called during 'simulate' to advance a single step the gym environment
            and return (observation, reward, done, info).
        """
        observation, reward, done, info = self._env.step(gym_action)
        return observation, reward, done, info

    def simulate(self, action):
        """ Do a step of the simulation, optionally rendering the results
        """
        #convert the Bonsai actions to openai environemnt action type 
        gym_action = self.action_to_gym(action)
        
        log.debug('simulating - gym action {}   state {}'.format(gym_action, self._env.unwrapped.state))

        rwd_accum = 0
        done = False
        i = 0
        observation = None

        for i in range(self._skip_frame):
            observation, reward, done, info = self.gym_simulate(gym_action)
            self.finished = done

            log.debug('gym_simulate returned observation{} reward {} done {}  info {}'.format(observation, reward, done, info))

            self.episode_reward += reward
            rwd_accum += reward

            # episode limits
            if (self._iteration_limit > 0):
                if (self.iteration_count >= self._iteration_limit):
                    self.finished = True
                    log.info("--STOPPING EPISODE -- iteration {} > limit {}".format(self.iteration_count, self._iteration_limit))
                    break

         # render if not headless
            if not self._headless:
                if 'human' in self._env.metadata['render.modes']:
                    self._env.render()

        # log a periodic status of iterations and episodes
        self.periodic_status_update()

        reward = rwd_accum / (i + 1)

        # convert state and return to the server
        state_after_simulation = self.gym_to_state(observation)

        log.debug("simulation returning state {}".format(state_after_simulation))

        return state_after_simulation, reward, done

    def episode_step(self, action: Dict[str, Any]) -> None :
        """Increases the iteration count and run a simulation for given actions
        """
        log.debug("-- EPISODE STEP {}-- - action {}".format(self.iteration_count, action))
        
        self.iteration_count += 1
        self.simulate(action)
        
        log.debug("-------------------------------------")

    def episode_finish(self, reason: str) -> None:
        """ Called when the episode has finished
        """
        log.info("-- EPISODE FINISH --")
        log.info("-- iteration {} episode {} reward {} reason {}".format(
            self.iteration_count, self.episode_count, self.episode_reward, reason))

        self._last_status = time()
        self.episode_count += 1
        self.finished = True

    def periodic_status_update(self) -> None:
        """ Logs a periodic status update showing current reward
            Useful when logging level is set to info and 
            we don't want to see the logs for each step
        """
        if time() - self._last_status > self._log_interval:
            log.info("Episode {} is still running, reward so far is {}".format(
                     self.episode_count, self.episode_reward))
            self._last_status = time()

    def halted(self) -> bool:
        """ Returns True if the simulator has finished the episode
        """
        return self.finished

    def get_interface(self) -> Dict[str, Any]:
        """ Reads the content of the simulator_interface.json file 
            and converts it to a dictionary of values

            Override it in derived class to use non-generic file name
        """ 
        interface_file_path ="simulator_interface.json"
        
        with open(interface_file_path) as file:
            interface = json.load(file)
        return interface

    def parse_arguments(self):
        """ Parses command line arguments and returns them as a list
        """
        headless_help = (
            "The simulator can be run with or without the graphical "
            "environment. By default the graphical environment is shown. "
            "Using --headless will run the simulator without graphical "
            "output. This may be set as BONSAI_HEADLESS in the environment.")
        parser = argparse.ArgumentParser()
        parser.add_argument('--headless',
                            help=headless_help,
                            action='store_true',
                            default=os.environ.get('BONSAI_HEADLESS', False))
        try:
            args, unknown = parser.parse_known_args()
        except SystemExit:
            log.error('An error occured while trying to parse the args')
            return None
        return args
