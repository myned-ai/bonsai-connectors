# This sample demonstrates how to teach a policy for controlling
# a cartpole (inverted pendulum) device.

inkling "2.0"

using Goal
using Number
using Math


# Type that represents the per-iteration state returned by simulator
type SimState {
    # Cos Theta
    cos_theta: number<-1 .. 1>,

    # Sin Theta
    sin_theta: number<-1 .. 1>,

    # Angular Velocity
    angular_velocity: number<-8 .. 8>,
}

# Type that represents the per-iteration action accepted by the simulator
type SimAction {
    # Amount of force in x direction to apply to the pendulum.
    command: number<-2 .. 2>
}

# Define a concept graph with a single concept
graph (input: SimState): SimAction {
    concept BalancePendulum(input): SimAction {
        curriculum {
            # The source of training for this concept is a simulator
            # that takes an action as an input and outputs a state.
            source simulator (Action: SimAction): SimState {
            }

            # The objective of training is expressed as a goal with two
            # subgoals: don't let the pole fall over, and don't move
            # the cart off the track.
            goal (State: SimState) {
                drive `cos is zero`:
                    State.cos_theta in Goal.Range(0.707, 1.0)
            }

            training {
                # Limit the number of iterations per episode to 120. The default
                # is 1000, which makes it much tougher to succeed.
                EpisodeIterationLimit: 120
            }
        }
    }
}

# Special string to hook up the simulator visualizer
# in the web interface.
const SimulatorVisualizer = "/pendulumviz/"