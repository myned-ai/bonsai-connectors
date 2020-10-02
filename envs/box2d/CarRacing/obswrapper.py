import gym
import numpy as np
import cv2

import tflite_runtime.interpreter as tflite

from gym.spaces import Box
from gym import ObservationWrapper



class ObsWrapper(gym.ObservationWrapper):
    def __init__(self, env):
        super().__init__(env)

        self.observation_space = Box(low=np.finfo(np.float32).min, high=np.finfo(
            np.float32).max, shape=(1, 256,), dtype=np.float32)

        self.interpreter = None
        # self.loaded_model.summary()

    def reset(self, **kwargs):
        #load the model when the first rest method is called
        if self.interpreter is None:
            self.interpreter = tflite.Interpreter(model_path='autoencoder_model.tflite')

        observation = self.env.reset(**kwargs)
        return self.observation(observation)

    def observation(self, obs):
        # modify obs
        grass_driving_r = np.mean(obs[:, :, 0])
        grass_driving_g = np.mean(obs[:, :, 1])# > 185.0
        grass_driving_b = np.mean(obs[:, :, 2])
        
        obs = cv2.cvtColor(obs, cv2.COLOR_RGB2GRAY)
        obs = np.array(obs).astype(np.float32)
        obs = obs / 255.0
        obs = obs.reshape(-1, 96, 96, 1)

        #encoded = self.loaded_model.encoder(obs).numpy()

        self.interpreter.allocate_tensors()

        # Get input and output tensors.
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()

        # Test the model on random input data.
        #input_shape = input_details[0]['shape']
        # input_data = np.array(np.random.random_sample(
        #   input_shape), dtype=np.float32)
        self.interpreter.set_tensor(input_details[0]['index'], obs)

        self.interpreter.invoke()

        # The function `get_tensor()` returns a copy of the tensor data.
        # Use `tensor()` in order to get a pointer to the tensor.
        encoded = self.interpreter.get_tensor(
            output_details[0]['index'])

        return {'obs': encoded, 'grass_driving_r': grass_driving_r,
        'grass_driving_g': grass_driving_g,'grass_driving_b': grass_driving_b}
