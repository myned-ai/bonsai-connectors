import gym
import numpy as np
import cv2

import tensorflow as tf
from tensorflow.keras.models import Model

from gym.spaces import Box
from gym import ObservationWrapper


class ObsWrapper(gym.ObservationWrapper):
    def __init__(self, env):
        super().__init__(env)

        self.observation_space = Box(low=np.finfo(np.float32).min, high=np.finfo(
            np.float32).max, shape=(1, 256,), dtype=np.float32)
        self.loaded_model = tf.keras.models.load_model('./autoencoder_model')
        self.loaded_model.summary()

    def observation(self, obs):
        # modify obs
        obs = cv2.cvtColor(obs, cv2.COLOR_RGB2GRAY)
        obs = np.array(obs).astype(np.float32)
        obs = obs / 255.0
        obs = obs.reshape(-1, 96, 96, 1)

        encoded = self.loaded_model.encoder(obs).numpy()
        return encoded
