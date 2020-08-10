# This sample demonstrates how to teach a policy for controlling

inkling "2.0"
using Number
using Math


# Type that represents the per-iteration state returned by simulator
type SimState {
    obs:number<-5.0..5.0>[28],
    rew:number
}


type SimConfig{
    episode_iteration_limit: Number.UInt64
}
# State that represents the input to the policy
type ObservableState {
    obs:number<-5.0..5.0>[28]
}

# Type that represents the per-iteration action accepted by the simulator
type SimAction {

    j1: number<-1 .. 1>,
    j2: number<-1 .. 1>,
    j3: number<-1 .. 1>,
    j4: number<-1 .. 1>,
    j5: number<-1 .. 1>,
    j6: number<-1 .. 1>,
    j7: number<-1 .. 1>,
    j8: number<-1 .. 1>

}

# Define a concept graph with a single concept
graph (input: ObservableState): SimAction {
    concept Ant(input): SimAction {
        curriculum {
            # The source of training for this concept is a simulator
            # that takes an action as an input and outputs a state.
            source simulator (Action: SimAction,Config: SimConfig): SimState {
            }
            algorithm {
                Algorithm : "PPO"
            }
            reward GetReward

            training {
                EpisodeIterationLimit: 500,
                TotalIterationLimit: 200000000
            }
            lesson walking{
              scenario {
                    episode_iteration_limit: 500
                }
            }
        }
        
    }
    
}

function GetReward(State: SimState, Action: SimAction) {
    return State.rew
}