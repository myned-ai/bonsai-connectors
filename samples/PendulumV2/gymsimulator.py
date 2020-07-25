import argparse
import gym
import logging as log
import os
import json

from time import sleep, time
from typing import Dict, Any, Optional

#log = Logger()
#log.setLevel(0)

class GymSimulator():
    """ GymSimulator class

        End users should subclass GymSimulator to interface OpenAI Gym
        environments to the Bonsai platform. A minimal subclass must
        implement `gym_to_state()` and `action_to_gym()`, as well as
        specify the `simulator_name` and `environment_name`.

        To start the simulation for training, call `run_gym()`.
    """
    environment_name = ''  # name of the OpenAI Gym environment

    def __init__(self, sim_model,iteration_limit=200, skip_frame=1):
        """ initialize the GymSimulator with a bonsai.Config,
            the class variables will be used to setup the environment
            and simulator name as specified in inkling
        """
        self.sim_model = sim_model

        # create the gym environment
        self._env = gym.make(self.environment_name)

        self.finished = False
        self.episode_count = 0
        self.episode_reward = 0
        self.iteration_count = 0

        # parse optional command line arguments
        cli_args = self._parse_arguments()
        if cli_args is not None:
            self._headless = cli_args.headless

        # optional parameters for controlling the simulation
        self._iteration_limit = iteration_limit    
        self._skip_frame = skip_frame    # default is to process every frame

        # random seed
        self._env.seed(20)
        self._env.reset()

        # book keeping for rate status
        self._log_interval = 10.0  # seconds
        self._last_status = time()

    def run(self) -> bool:
        return self.sim_model.run()

    # convert openai gym observation to our state schema
    def gym_to_state(self, observation):
        """Convert a gym observation into an Inkling state

        Example:
            state = {'position': observation[0],
                     'velocity': observation[1],
                     'angle':    observation[2]}
            return state

        :param observation: gym observation, see specific gym
            environment for details.

        :return A dictionary matching the Inkling state schema.
        """
        return None

    # convert our action schema into openai gym action
    def action_to_gym(self, action):
        """Convert an Inkling action schema into a gym action.

        Example:
            return action['command']

        :param action: A dictionary as defined in the Inkling schema.
        :return A gym action as defined in the gym environment
        """
        return action['command']

    def gym_episode_start(self, config: Dict[str, Any]):
        """
        called during episode_start() to return the initial observation
        after reseting the gym environment. clients can override this
        to provide additional initialization.
        """
        observation = self._env.reset()

        return observation

    def episode_start(self, config: Dict[str, Any]):
        """ called at the start of each new episode
        """
        log.info("- - - - - - - - - - - - - - - - - - -- - - - - -- ")
        log.info("--EPISODE {} START-- ".format(self.episode_count))

        self._iteration_limit = config.get(
            "episode_iteration_limit", self._iteration_limit)

        self.finished = False
        self.iteration_count = 0
        self.episode_reward = 0

        # initial observation
        observation = self.gym_episode_start(config)
        self.gym_to_state(observation)

    def gym_simulate(self, gym_action):
        """
        called during simulate to single step the gym environment
        and return (observation, reward, done, info).
        clients can override this method to provide additional
        reward shaping.
        """
        observation, reward, done, info = self._env.step(gym_action)
        return observation, reward, done, info

    def simulate(self, action):
        """ step the simulation, optionally rendering the results
        """
        gym_action = self.action_to_gym(action)
        log.debug('simulating - action {}    gym_action {} state {}'.format(action, gym_action, self._env.env.state))

        rwd_accum = 0
        done = False
        i = 0
        observation = None

        for i in range(self._skip_frame):
            observation, reward, done, info = self.gym_simulate(gym_action)
            self.finished = done
            log.debug('gym_simulate returned reward {} done {}  info {}'.format(reward, done, info))
            self.episode_reward += reward
            rwd_accum += reward

            # episode limits
            if (self._iteration_limit > 0):
                if (self.iteration_count >= self._iteration_limit):
                    self.finished = True
                    log.info("--BREAKING-- iteration {} > {}".format(self.iteration_count, self._iteration_limit))
                    break

         # renderif not headless
         #   if not self._headless:
         #       if 'human' in self._env.metadata['render.modes']:
         #           self._env.render()

        # print a periodic status of iterations and episodes
        self._periodic_status_update()

        reward = rwd_accum / (i + 1)

        # convert state and return to the server
        state_after_simulation = self.gym_to_state(observation)

        log.debug("simulation returning observation {}".format(
            state_after_simulation))

        return state_after_simulation, reward, done

    def episode_step(self, action: Dict[str, Any]):
        log.debug("-- EPISODE STEP {}-- - command {}".format(self.iteration_count, action))
        self.iteration_count += 1
        self.simulate(action)
        log.debug("-------------------------------------")

    def episode_finish(self, reason: str):
        log.info("-- EPISODE FINISH --")
        log.info("-- iteration {} episode {} reward {} reason {}".format(
            self.iteration_count, self.episode_count, self.episode_reward, reason))
        self._last_status = time()
        self.episode_count += 1

    def standby(self, reason):
        """ report standby messages from the server
        """
        log.info('standby: {}'.format(reason))
        sleep(1)
        return True

    def run_gym(self):
        """ runs the simulation until cancelled or finished
        """
        while self.run():
            continue

        # success
        log.info('Finished running the simulator')

    def _periodic_status_update(self):
        """ print a periodic status update showing iterations/sec
        """
        if time() - self._last_status > self._log_interval:
            log.info("Episode {} is still running, reward so far is {}".format(
                     self.episode_count, self.episode_reward))
            self._last_status = time()

    def halted(self):
        return self.finished

    def get_interface(self) -> Dict[str, Any]:
        interface_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)
                            ), "simulator_interface.json"
        )
        with open(interface_file_path) as file:
            interface = json.load(file)
        return interface
		
    def _parse_arguments(self):
        """ parses command line arguments and returns them as a list
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
            print('')
            return None
        return args
