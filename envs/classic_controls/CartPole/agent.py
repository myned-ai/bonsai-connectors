import logging
from os import write
import requests
from typing import Any, Dict
from cartpole import CartPole
from tensorboardX import SummaryWriter

class BonsaiAgent(object):
    """ The agent that gets the action from the trained brain exported as docker image and started locally
    """

    def act(self, state) -> Dict[str, Any]:
        action = self.predict(state)
        #simulator expects action to be integer
        action["command"] = int(action["command"])
        return action

    def predict(self, state):
        #local endpoint when running trained brain locally in docker container
        url = "http://localhost:5000/v1/prediction"

        response = requests.get(url, json=state)
        action = response.json()

        return action


class RandomAgent(object):
    """The world's simplest agent!"""

    def __init__(self, cartpole: CartPole):
        self.cartpole = cartpole

    def act(self, state):
        return cartpole.gym_to_action(cartpole._env.action_space.sample())


if __name__ == '__main__':
    logging.basicConfig()
    log = logging.getLogger("cartpole")
    log.setLevel(level='INFO')

    writer = SummaryWriter()
    # we will use our environment (wrapper of OpenAI env)
    cartpole = CartPole()

    # specify which agent you want to use,
    # BonsaiAgent that uses trained Brain or
    # RandomAgent that randomly selects next action
    agent = BonsaiAgent()

    episode_count = 100

    try:
        for i in range(episode_count):
            #start a new episode and get the new state
            cartpole.episode_start()
            state = cartpole.get_state()
            cum_reward = 0

            while True:
                #get the action from the agent (based on the current state)
                action = agent.act(state)

                #do the next step of the simulation and get the new state
                cartpole.episode_step(action)
                state = cartpole.get_state()

                #get the last reward and add it the episode reward 
                reward = cartpole.get_last_reward()
                cum_reward += reward

                if cartpole.halted():
                    writer.add_scalar("reward", cum_reward, i )
                    break
                writer.flush()
            cartpole.episode_finish("")

        writer.close()    
    except KeyboardInterrupt:
        print("Stopped")
