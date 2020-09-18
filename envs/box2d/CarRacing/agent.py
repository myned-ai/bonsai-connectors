import logging
from os import write
import requests
from typing import Any, Dict
from carracing import CarRacing
from tensorboardX import SummaryWriter


class BonsaiAgent(object):
    """ The agent that gets the action from the trained brain exported as docker image and started locally
    """

    def act(self, state) -> Dict[str, Any]:
        action = self.predict(state)
        # simulator expects action to be integer
        action["command"] = int(action["command"])
        return action

    def predict(self, state):
        # local endpoint when running trained brain locally in docker container
        url = "http://localhost:5000/v1/prediction"

        response = requests.get(url, json=state)
        action = response.json()

        return action


class RandomAgent(object):
    """The world's simplest agent!"""

    def __init__(self, carracing: CarRacing):
        self.carracing = carracing

    def act(self, state):
        return carracing.gym_to_action(carracing._env.action_space.sample())


if __name__ == '__main__':
    logging.basicConfig()
    log = logging.getLogger("carracing")
    log.setLevel(level='INFO')

    writer = SummaryWriter()
    # we will use our environment (wrapper of OpenAI env)
    carracing = CarRacing()

    # specify which agent you want to use,
    # BonsaiAgent that uses trained Brain or
    # RandomAgent that randomly selects next action
    agent = BonsaiAgent()

    episode_count = 100

    try:
        for i in range(episode_count):
            # start a new episode and get the new state
            carracing.episode_start()
            state = carracing.get_state()
            cum_reward = 0

            while True:
                # get the action from the agent (based on the current state)
                action = agent.act(state)

                # do the next step of the simulation and get the new state
                carracing.episode_step(action)
                state = carracing.get_state()

                # get the last reward and add it the episode reward
                reward = carracing.get_last_reward()
                cum_reward += reward

                if carracing.halted():
                    writer.add_scalar("reward", cum_reward, i)
                    break
                writer.flush()
            carracing.episode_finish("")

        writer.close()
    except KeyboardInterrupt:
        print("Stopped")
