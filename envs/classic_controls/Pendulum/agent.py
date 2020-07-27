import gym
from gym import logger
import requests


class BonsaiAgent(object):
    """ The agent that gets the action from the trained brain exported as docker image and started locally
    """
    def __init__(self, action_space):
        self.action_space = action_space

    def act(self, observation, reward, done):
        action = self.predict(observation[0], observation[1], observation[2])
        return [action["command"]]

    def predict(self,
                cos_theta: float,
                sin_theta: float,
                angular_velocity: float) -> dict:
        url = "http://localhost:5000/v1/prediction"
        state = {
            "cos_theta": cos_theta,
            "sin_theta": sin_theta,
            "angular_velocity": angular_velocity
        }
        response = requests.get(url, json=state)
        action = response.json()
        return action


class RandomAgent(object):
    """The world's simplest agent!"""

    def __init__(self, action_space):
        self.action_space = action_space

    def act(self, observation, reward, done):
        return self.action_space.sample()


if __name__ == '__main__':
    # You can set the level to logger.DEBUG or logger.WARN if you
    # want to change the amount of output.
    logger.set_level(logger.INFO)

    env = gym.make('Pendulum-v0')

    env.seed(0)

    # specify which agent you want to use, 
    # BonsaiAgent that uses trained Brain or
    # RandomAgent that randomly selects next action
    agent = RandomAgent(env.action_space)

    env.render()
    env.reset()

    episode_count = 100
    reward = 0
    done = False

    for i in range(episode_count):
        ob = env.reset()
        while True:
            action = agent.act(ob, reward, done)
            ob, reward, done, _ = env.step(action)
            env.render()
            if done:
                break

    # Close the env and write monitor result info to disk
    env.close()
