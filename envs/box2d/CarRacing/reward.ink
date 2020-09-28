# This sample demonstrates how to teach a policy for controlling

inkling "2.0"
using Number
using Math


# Type that represents the per-iteration state returned by simulator
type SimState {
    obs:number[256],
    rew:number
}

# Type that represents the per-iteration action accepted by the simulator
type SimAction {

    steer: number<-1.0, 1.0,>,
    gas: number<0.0, 1.0,>,
    break: number<0.0, 1.0,>

}

# Define a concept graph with a single concept
graph (input: SimState): SimAction {
    concept CarRacing(input): SimAction {
        curriculum {
            # The source of training for this concept is a simulator
            # that takes an action as an input and outputs a state.
            source simulator (Action: SimAction): SimState {
            }
            
            reward GetReward

            }
        }
        
    }


function GetReward(State: SimState, Action: SimAction) {
   # var playfield = 2000/6.0
   # var rew = -0.1

   # if Math.Abs(State.x) > playfield or Math.Abs(State.y) > playfield {
   #     rew = -100
   # }

    return State.rew
}
