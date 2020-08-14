# This sample demonstrates how to teach a policy for controlling

inkling "2.0"
using Number
using Math
using Goal

# Type that represents the per-iteration state returned by simulator
type SimState {
    obs:number<-5.0..5.0>[15],
    rew:number,
    episode_rew:number,
    body_x:number,
    body_y:number,
    body_z:number,
    prev_body_x:number,
    prev_body_y:number,
    prev_body_z:number,
    progress:number
}


type SimConfig{
    episode_iteration_limit: Number.UInt64
}
# State that represents the input to the policy
type ObservableState {
    obs:number<-5.0..5.0>[15],
}

# Type that represents the per-iteration action accepted by the simulator
type SimAction {

    j1: number<-1.0 .. 1.0>,
    j2: number<-1.0 .. 1.0>,
    j3: number<-1.0 .. 1.0>,
}

# Define a concept graph with a single concept
graph (input: ObservableState): SimAction {
    concept Cheetah(input): SimAction {
        curriculum {
            # The source of training for this concept is a simulator
            # that takes an action as an input and outputs a state.
            source simulator (Action: SimAction,Config: SimConfig): SimState {
            }
            algorithm {
                Algorithm : "SAC",
            #    PolicyLearningRate:0.008
            }
            #reward GetReward
            goal (State: SimState) {
                #uncomment for staying alive goals
                #avoid `floor`   :
                #    State.body_z in Goal.RangeBelow(0.81)  
                #avoid `rotation`   :
                #    Math.Abs(State.obs[7]) in Goal.RangeAbove(0.99)  
                maximize `progress` :   
                    State.progress in Goal.RangeAbove(0.5)
                 
      
  
            }
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

