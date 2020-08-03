import logging
from collections import namedtuple
import numpy as np
from tensorboardX import SummaryWriter

import torch
import torch.nn as nn
import torch.optim as optim


HIDDEN_SIZE = 128
BATCH_SIZE = 16
PERCENTILE = 70

from cartpole import CartPole

class Net(nn.Module):
    def __init__(self, obs_size, hidden_size, n_actions):
        super(Net, self).__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, n_actions)
        )

    def forward(self, x):
        return self.net(x)

class CartPoleTraining:
    """ Training cartpole using cross entropy agoritham based on the code from the book
    'Deep Reinforcement Learning Hands-On'
    """
    Episode = namedtuple('Episode', field_names=['reward', 'steps'])
    EpisodeStep = namedtuple('EpisodeStep', field_names=['observation', 'action'])

    def __init__(self) -> None:
        self.cartpole = CartPole()

    def iterate_batches(self, net, batch_size):
        batch = []
        episode_reward = 0.0
        episode_steps = []

        #start the episode
        self.cartpole.episode_start()
        state = self.cartpole.get_state()

        obs = self.cartpole.state_to_gym(state)

        sm = nn.Softmax(dim=1)
        while True:
            obs_v = torch.FloatTensor([obs])
            act_probs_v = sm(net(obs_v))
            act_probs = act_probs_v.data.numpy()[0]
            action = np.random.choice(len(act_probs), p=act_probs)
            
            bonsai_action = self.cartpole.gym_to_action(action)

            self.cartpole.episode_step(bonsai_action)

            is_done = self.cartpole.halted()
            reward = self.cartpole.get_last_reward()
            next_obs = self.cartpole.state_to_gym(self.cartpole.get_state())

            episode_reward += reward
            step = self.EpisodeStep(observation=obs, action=action)
            episode_steps.append(step)
            if is_done:
                e = self.Episode(reward=episode_reward, steps=episode_steps)
                batch.append(e)
                episode_reward = 0.0
                episode_steps = []
                self.cartpole.episode_finish("")

                self.cartpole.episode_start()
                state = self.cartpole.get_state()

                next_obs = self.cartpole.state_to_gym(state)

                if len(batch) == batch_size:
                    yield batch
                    batch = []
            obs = next_obs

    def filter_batch(self, batch, percentile):
        rewards = list(map(lambda s: s.reward, batch))
        reward_bound = np.percentile(rewards, percentile)
        reward_mean = float(np.mean(rewards))

        train_obs = []
        train_act = []
        for reward, steps in batch:
            if reward < reward_bound:
                continue
            train_obs.extend(map(lambda step: step.observation, steps))
            train_act.extend(map(lambda step: step.action, steps))

        train_obs_v = torch.FloatTensor(train_obs)
        train_act_v = torch.LongTensor(train_act)
        return train_obs_v, train_act_v, reward_bound, reward_mean

    def train(self):
        obs_size = self.cartpole._env.unwrapped.observation_space.shape[0]
        n_actions = self.cartpole._env.unwrapped.action_space.n

        net = Net(obs_size, HIDDEN_SIZE, n_actions)
        objective = nn.CrossEntropyLoss()
        optimizer = optim.Adam(params=net.parameters(), lr=0.01)
        writer = SummaryWriter(comment="-cartpole")

        for iter_no, batch in enumerate(self.iterate_batches(net, BATCH_SIZE)):
            obs_v, acts_v, reward_b, reward_m = self.filter_batch(batch, PERCENTILE)
            optimizer.zero_grad()
            action_scores_v = net(obs_v)
            loss_v = objective(action_scores_v, acts_v)
            loss_v.backward()
            optimizer.step()
            
            #env.render()
            
            print("%d: loss=%.3f, reward_mean=%.1f, rw_bound=%.1f" % (
                iter_no, loss_v.item(), reward_m, reward_b))
            writer.add_scalar("loss", loss_v.item(), iter_no)
            writer.add_scalar("reward_bound", reward_b, iter_no)
            writer.add_scalar("reward_mean", reward_m, iter_no)
            if reward_m > 199:
                print("Solved!")
                break
        writer.close()

if __name__ == '__main__':
    logging.basicConfig()
    log = logging.getLogger("cartpole")
    log.setLevel(level='INFO')

    cross_entropy_agent = CartPoleTraining()
    cross_entropy_agent.train()
    
    #TODO  save the model after training and load it in agent 

    # we will use our environment (wrapper of OpenAI env)
    cartpole = CartPole()
