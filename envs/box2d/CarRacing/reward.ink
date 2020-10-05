# This sample demonstrates how to teach a policy for controlling

inkling "2.0"
using Number
using Math


# Type that represents the per-iteration state returned by simulator
type SimState {
    obs:number[256],
    x:number,
    y:number,
    progress:number,
    length:number,
    grass_driving_r:number,
    grass_driving_g:number,
    grass_driving_b:number
}

# Type that represents the per-iteration action accepted by the simulator
type SimAction {

    steer: number<-1.0 .. 1.0>,
    gas: number<0.0 .. 1.0>,
    break: number<0.0 .. 1.0>,

}

type SimConfig{
    episode_iteration_limit: Number.UInt64
}
# State that represents the input to the policy
type ObservableState {
    obs:number[256]
}


# Define a concept graph with a single concept
graph (input: ObservableState): SimAction {
    concept CarRacing(input): SimAction {
        curriculum {
            # The source of training for this concept is a simulator
            # that takes an action as an input and outputs a state.
            source simulator (Action: SimAction,Config: SimConfig): SimState {
            }
            algorithm {
                Algorithm: "PPO",
                BatchSize : 5000,
                PolicyLearningRate:0.0003

            }
            reward GetReward

            training {
                EpisodeIterationLimit: 300,
                TotalIterationLimit: 200000000
            }
            lesson walking{
              scenario {
                    episode_iteration_limit: 300
                }
            }
        }
        
    }
    
}


function GetReward(State: SimState, Action: SimAction) {
   var rew = -0.2
   var playfield = 2000/6.0

    rew = rew - (0.3 * Action.steer * Action.steer) 
    rew = rew - (0.5 * Action.break * Action.break) 
    rew = rew + (0.3 * Action.gas * Action.gas) 

    if State.progress > 0 {
        rew = rew + 800 / State.length
    }

   if Math.Abs(State.x) > playfield or Math.Abs(State.y) > playfield {
        rew = rew -100
    }

    return rew
}