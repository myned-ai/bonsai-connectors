# This sample demonstrates how to teach a policy for controlling

inkling "2.0"
using Number
using Math


# Type that represents the per-iteration state returned by simulator
type SimState {
    obs:<0..255>[H][W][3],
    rew:number
}

# Type that represents the per-iteration action accepted by the simulator
type SimAction {

    steer: number<-1.0, 1.0>,
    gas: number<0.0, 1.0>,
    break: number<0.0, 1.0>

}

# Define a concept graph with a single concept
graph (input: ObservableState): SimAction {
    concept CarRacer(input): SimAction {
        curriculum {
            # The source of training for this concept is a simulator
            # that takes an action as an input and outputs a state.
            source simulator (Action: SimAction,Config: SimConfig): SimState {
            }
            
            reward GetReward

            }
        }
        
    }
    
}

function GetReward(State: SimState, Action: SimAction) {
    return State.rew
}