## PyBullet

Bullet is a physics engine which simulates collision detection, soft and rigid body dynamics.

PyBullet Gymperium is an open-source implementation of the OpenAI Gym MuJoCo environments for use with the OpenAI Gym Reinforcement Learning Research Platform in support of open research.

### 1. Hopper

Make a two-dimensional one-legged robot hop forward as fast as possible.
The robot model is based on work by Erez, Tassa, and Todorov.

T Erez, Y Tassa, E Todorov, "Infinite Horizon Model Predictive Control for Nonlinear Periodic Tasks", 2011.

We have trained the agent by reusing the reward function defined in pybullet-gym and amended the PPO algorithm parameters.

```
algorithm {
    Algorithm: "PPO",
    BatchSize : 3000,
    PolicyLearningRate:0.001
}

reward GetReward

training {
    EpisodeIterationLimit: 300
}
lesson walking{
    scenario {
        episode_iteration_limit: 300
    }
}

function GetReward(State: SimState, Action: SimAction) {
    return State.rew
}    
```

- Bonsai training output:

![Alt Text](../../assets/hopper.jpg)

- Exported agent (brain) performance:

![Alt Text](../../assets/hoppers.gif)

### 2. Reacher

Make a 2D robot reach to a randomly located target.

We have trained the agent by getting the reward function defined in pybullet-gym and amended the PPO algorithm parameters.

```
algorithm {
    Algorithm: "PPO",
    BatchSize : 10000,
    PolicyLearningRate:0.0001
}
reward GetReward

training {
    EpisodeIterationLimit: 200
}
lesson walking{
    scenario {
        episode_iteration_limit: 200
    }
}
```

- Bonsai training output:

![Alt Text](../../assets/reacher.jpg)

- Exported agent (brain) performance:

![Alt Text](../../assets/reacher.gif)
