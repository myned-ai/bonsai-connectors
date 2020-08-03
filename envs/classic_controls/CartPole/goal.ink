# This sample demonstrates how to teach a policy for controlling
# a cartpole (inverted pendulum) device.

inkling "2.0"

using Math
using Goal

# Length of the cartpole track in meters
const TrackLength = 9.6

 #   Observation:
 #       Type: Box(4)
 #       Num     Observation               Min                     Max
 #       0       Cart Position             -4.8                    4.8
 #       1       Cart Velocity             -Inf                    Inf
 #       2       Pole Angle                -0.418 rad (-24 deg)    0.418 rad (24 deg)
 #       3       Pole Angular Velocity     -Inf                    Inf


# Type that represents the per-iteration state returned by simulator
type SimState {
    # Position of cart in meters
    cart_position: number<-TrackLength / 2 .. TrackLength / 2>,

    # Velocity of cart in meters/sec
    cart_velocity: number,

    # Current angle of pole in radians
    pole_angle: number<-Math.Pi .. Math.Pi>,

    # Angular velocity of the pole in radians/sec
    pole_angular_velocity: number,
}

# Type that represents the per-iteration action accepted by the simulator
type SimAction {
    # Amount of force in x direction to apply to the cart.
    command: number<Left = 0.0, Right = 1.0>
}

# Define a concept graph with a single concept
graph (input: SimState): SimAction {
    concept BalancePole(input): SimAction {
        curriculum {
            # The source of training for this concept is a simulator
            # that takes an action as an input and outputs a state.
            source simulator (Action: SimAction): SimState {
            }

            # The objective of training is expressed as a goal with two
            # subgoals: don't let the pole fall over, and don't move
            # the cart off the track.
            goal (State: SimState) {
                avoid `Fall Over`:
                    Math.Abs(State.pole_angle) in Goal.RangeAbove(0.15) # 0.15 is 0.05 less than the maximum angle of pole in radians before it has fallen
                avoid `Out Of Range`:
                    Math.Abs(State.cart_position) in Goal.RangeAbove(1.4) # 1.4 reduces the space the cartpole is allowed to move while balancing
            }

            training {
                # Limit the number of iterations per episode to 200
                EpisodeIterationLimit: 200
            }
        }
    }
}

# Special string to hook up the simulator visualizer
# in the web interface.
const SimulatorVisualizer = "/cartpoleviz/"