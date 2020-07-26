# This sample demonstrates how to teach a policy for controlling
# a dmountain car.

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
    # Car Position
    position: number<-1.2 .. 0.6>,

    # Car Speed
    speed: number<-0.07 .. 0.07>,
}

# Type that represents the per-iteration action accepted by the simulator
type SimAction {
    # Amount of force in x direction to apply to the Mountain Car.
    command: number< Left=0, nothing=1, Right=2 >
}

# Define a concept graph with a single concept
graph (input: SimState): SimAction {
    concept MountainCarBalance(input): SimAction {
        curriculum {
            source simulator (Action: SimAction, Config: SimConfig): SimState {
            }

            goal (State: SimState) {
                reach `car position`:
                    State.position in Goal.RangeAbove(0.5)   
                maximize `speed`:
                    State.speed in Goal.Range(0, 0.07)       
            }

            training {
                # Limit the number of iterations per episode to 120. The default
                # is 1000, which makes it much tougher to succeed.
                EpisodeIterationLimit: 200
            }
        }  
    }
}