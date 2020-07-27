# Bonsai Gym

Bonsai Gym is an open-source interface library, which gives us access to OpenAI Gym standardized set of environments while using Microsoft Bonsai platform.

## Basics

There are two basic concepts in reinforcement learning: the environment (namely, the outside world) and the agent (namely, the algorithm you are writing). The agent sends actions to the environment, and the environment replies with observations and rewards (that is, a score).

OpenAI Gym is a toolkit for developing and comparing reinforcement learning algorithms. The gym open-source library, gives us access to a standardized set of environments. Environments come as is with no predefined agent. 

Link to Open AI environments: https://github.com/openai

Bonsai is the machine teaching service in the Autonomous Systems suite from Microsoft. It builds on innovations in reinforcement learning to simplify AI development.
we use Bonsai to create agents (brains) that control and optimize complex systems. No neural net design required.

Full documentation for Bonsai's Platform can be found at https://docs.bons.ai.

## Set Up

Bonsai need two environment variables set to be able to attach to the platform.

The first is SIM_ACCESS_KEY. You can create one from the Account Settings page.
The second is SIM_WORKSPACE. You can find this in the URL after /workspaces/ once you are logged in to the platform.



You will need to install support libraries prior to running locally. 
Our environment depend on microsoft_bonsai_api package and on our gym_connectors

```
cd connectors
pip3 install .
pip3 install microsoft_bonsai_api
```

## Environments

### Classic Controls

#### Pendulum

![Alt Text](assets/pendulum_bonsai_training.jpg)

##### Trained:

![Alt Text](assets/pendulum.gif)

#### Mountain Car

![Alt Text](assets/mountain_car.jpg)

##### Trained:

![Alt Text](assets/mountain_car.gif)

### PyBullet

Coming Soon
