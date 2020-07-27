# This sample demonstrates how to teach a policy for controlling
# a pendulum device.

inkling "2.0"

using Goal
using Number
using Math

type SimConfig{
    initial_theta: number,
    iteration_limit: Number.UInt64
}

# Type that represents the per-iteration state returned by simulator
type SimState {
    # Cos Theta
    cos_theta: number<-1.0 .. 1.0>,

    # Sin Theta
    sin_theta: number<-1.0 .. 1.0>,

    # Angular Velocity
    angular_velocity: number<-8.0 .. 8.0>,
}

# Type that represents the per-iteration action accepted by the simulator
type SimAction {
    # Amount of force in x direction to apply to the pendulum.
    command: number<-2.0 .. 2.0>
}

# Define a concept graph with a single concept
graph (input: SimState): SimAction {
    concept PendulumBalance(input): SimAction {
        curriculum {
            source simulator (Action: SimAction, Config: SimConfig): SimState {
            }

            reward GetReward

            algorithm {
                Algorithm: "SAC"
            }
            training {
                # Limit the number of iterations per episode to 120. The default
                # is 1000, which makes it much tougher to succeed.
                EpisodeIterationLimit: 200
            }

            lesson easy{
              scenario {
                    initial_theta: number<-0.873 .. 0.873>
                }
                training{
                    LessonRewardThreshold: -600
                }
            }

            lesson hard{
              scenario {
                    initial_theta: number<-Math.Pi .. Math.Pi>
                }
                training{
                    LessonRewardThreshold: -200
                }

            }
        }
        
    }
}


function GetReward(State: SimState, Action: SimAction) {
    var u = Action.command
    var th = Math.ArcCos(State.cos_theta)
    var rew = ((((th + Math.Pi) % (2 * Math.Pi)) - Math.Pi) ** 2) + 0.1 * (State.angular_velocity ** 2) + 0.001 * (u ** 2)

    return -rew
}

# Special string to hook up the simulator visualizer
# in the web interface.
const SimulatorVisualizer = "/pendulumviz/"