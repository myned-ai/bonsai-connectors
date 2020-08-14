import logging
import requests
from typing import Any, Dict
from half_cheetah import HalfCheetah


class BonsaiAgent(object):
    """ The agent that gets the action from the trained brain exported as docker image and started locally
    """

    def act(self, state) -> Dict[str, Any]:
        action = self.predict(state)

        return action

    def predict(self, state):
        # local endpoint when running trained brain locally in docker container
        url = "http://localhost:5000/v1/prediction"

        response = requests.get(url, json=state)
        action = response.json()

        return action


if __name__ == '__main__':
    logging.basicConfig()
    log = logging.getLogger("half_cheetah")
    log.setLevel(level='DEBUG')

    # we will use our environment (wrapper of OpenAI env)
    half_cheetah = HalfCheetah(iteration_limit=500)

    # specify which agent you want to use,
    # BonsaiAgent that uses trained Brain or
    # RandomAgent that randomly selects next action
    agent = BonsaiAgent()

    # half_cheetah._env.render()
    # half_cheetah._env.reset()

    episode_count = 100

    try:
        for i in range(episode_count):
            # start a new episode and get the new state
            half_cheetah.episode_start()
            state = half_cheetah.get_state()

            while True:
                # get the action from the agent (based on the current state)
                action = agent.act(state)

            # do the next step of the simulation and get the new state
                half_cheetah.episode_step(action)
                state = half_cheetah.get_state()

                if half_cheetah.halted():
                    break

            half_cheetah.episode_finish("")

    except KeyboardInterrupt:
        print("Stopped")
