# This sample demonstrates how to teach a policy for controlling
# an inverted pendulum device.

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
            
            algorithm {
                Algorithm: "SAC"
            }

            goal (State: SimState) {
                drive `cos upwards`:
                    State.cos_theta in Goal.Range(0.707, 1.0)
            }

            training {
                # Limit the number of iterations per episode.
                EpisodeIterationLimit: 120
            }
        }
    }
}