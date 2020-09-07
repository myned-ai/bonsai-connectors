## Classic Controls

A collection of control theory problems from the classic RL literature.

### 1. Inverted Pendulum

The inverted pendulum swing-up problem is a classic problem in the control literature. In this version of the problem, the pendulum starts in a random position, and the goal is to swing it up so it stays upright.

We have trained the agent using a reward function, although a goal statement produced equally good results.

Reward function:
```
function GetReward(State: SimState, Action: SimAction) {
    var cmd = Action.command   #the value of the last command
    var theta = Math.ArcCos(State.cos_theta)   
    var cost = ((((theta + Math.Pi) % (2 * Math.Pi)) - Math.Pi) ** 2) + 0.1 * (State.angular_velocity ** 2) + 0.001 * (cmd ** 2)

    return -cost
}
```
Alternative Goal statement:
```
goal (State: SimState) {
    drive `upwards`:
        State.cos_theta in Goal.Range(0.707, 1.0)
}
```

- Bonsai training output:

![Alt Text](../../assets/pendulum.jpg)

- Exported agent (brain) performance:

![Alt Text](../../assets/pendulum.gif)

### 2. Mountain Car

A car is on a one-dimensional track, positioned between two "mountains". The goal is to drive up the mountain on the right; however, the car's engine is not strong enough to scale the mountain in a single pass. Therefore, the only way to succeed is to drive back and forth to build up momentum.

The environment appeared first in Andrew Moore's PhD Thesis (1990).

We have trained the agent using two  goal statements.

```
goal (State: SimState) {
    reach `car position`:
        State.position in Goal.RangeAbove(0.5)  
    maximize `speed`:
        Math.Abs(State.speed) in Goal.Range(0, 0.07)      
}
```

- Bonsai training output:

![Alt Text](../../assets/mountain_car.jpg)

- Exported agent (brain) performance:

![Alt Text](../../assets/mountain_car.gif)

### 3. Cart Pole

A pole is attached by an un-actuated joint to a cart, which moves along
a frictionless track. The pendulum starts upright, and the goal is to
prevent it from falling over by increasing and reducing the cart's
velocity.

This environment corresponds to the version of the cart-pole problem
described by Barto, Sutton, and Anderson

We have trained the agent using reward function and choosing the algorithm parameters.

```
goal (State: SimState) {
    avoid `Fall Over`:
        Math.Abs(State.pole_angle) in Goal.RangeAbove(0.15)
    avoid `Out Of Range`:
        Math.Abs(State.cart_position) in Goal.RangeAbove(1.4)
}
```

- Bonsai training output:

![Alt Text](../../assets/cart_pole.jpg)

- Exported agent (brain) performance:

![Alt Text](../../assets/cart_pole.gif)
