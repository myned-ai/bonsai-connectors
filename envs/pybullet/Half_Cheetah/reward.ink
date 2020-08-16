# This sample demonstrates how to teach a policy for controlling

inkling "2.0"
using Number
using Math

# Type that represents the per-iteration state returned by simulator
type SimState {
    obs:number<-5.0..5.0>[26],
    joints_at_limit_cost:number,
    progress:number
}


type SimConfig{
    episode_iteration_limit: Number.UInt64
}
# State that represents the input to the policy
type ObservableState {
    obs:number<-5.0..5.0>[26]
}

# Type that represents the per-iteration action accepted by the simulator
type SimAction {

    j1: number<-1 .. 1>,
    j2: number<-1 .. 1>,
    j3: number<-1 .. 1>,
    j4: number<-1 .. 1>,
    j5: number<-1 .. 1>,
    j6: number<-1 .. 1>

}

# Define a concept graph with a single concept
graph (input: ObservableState): SimAction {
    concept HalfCheetah(input): SimAction {
        curriculum {
            # The source of training for this concept is a simulator
            # that takes an action as an input and outputs a state.
            source simulator (Action: SimAction,Config: SimConfig): SimState {
            }
            algorithm {
                Algorithm: "PPO",
                BatchSize : 5000,
                PolicyLearningRate:0.001
            }
            
            reward GetReward

            training {
                EpisodeIterationLimit: 1100,
                TotalIterationLimit: 200000000
            }
            lesson walking{
              scenario {
                    episode_iteration_limit: 1100
                }
            }
        }
        
    }
    
}

function GetReward(State: SimState, Action: SimAction) {
    var action_sum = Action.j1 + Action.j2 + Action.j3 + Action.j4 + Action.j5 + Action.j6
    var reward_ctrl = - 0.1 * (action_sum * action_sum)
    var reward_run = State.progress
    var rew = reward_ctrl + reward_run + State.joints_at_limit_cost

    return rew
}