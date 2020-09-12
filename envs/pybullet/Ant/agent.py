import logging
import requests
from typing import Any, Dict
from ant import Ant


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
    log = logging.getLogger("ant")
    log.setLevel(level='DEBUG')

    # we will use our environment (wrapper of OpenAI env)
    ant = Ant(iteration_limit=500)

    # specify which agent you want to use,
    # BonsaiAgent that uses trained Brain or
    # RandomAgent that randomly selects next action
    agent = BonsaiAgent()

    # ant._env.render()
    # ant._env.reset()

    episode_count = 100

    try:
        for i in range(episode_count):
            # start a new episode and get the new state
            ant.episode_start()
            state = ant.get_state()

            # setting initial camera position
            lookat = [0, 0, 0]
            pitch = -20
            distance = 2
            yaw = 10
            ant._env.unwrapped._p.resetDebugVisualizerCamera(
                distance, yaw, pitch, lookat)

            while True:
                # get the action from the agent (based on the current state)
                action = agent.act(state)
                ant._env.unwrapped.camera_adjust()

            # do the next step of the simulation and get the new state
                ant.episode_step(action)
                state = ant.get_state()

                if ant.halted():
                    break

            ant.episode_finish("")

    except KeyboardInterrupt:
        print("Stopped")
