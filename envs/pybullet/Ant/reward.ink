# This sample demonstrates how to teach a policy for controlling

inkling "2.0"
using Number
using Math

# Type that represents the per-iteration state returned by simulator
type SimState {
    obs:number<-5.0..5.0>[28],
    joints_at_limit:number,
    progress:number,
    joint_speeds:number[8]
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
                Algorithm: "PPO",
                BatchSize : 20000,
                PolicyLearningRate:0.0005
            }
            
            reward GetReward

            training {
                EpisodeIterationLimit: 1000,
                TotalIterationLimit: 200000000
            }
            lesson walking{
              scenario {
                    episode_iteration_limit: 1000
                }
            }
        }
        
    }
    
}


function GetReward(State: SimState, Action: SimAction) {
    # electicity_cost: cost for using motors -- this parameter should be carefully tuned against reward for making progress
    var electricity = -0.55
    var stall_torque_cost = -0.01
    var a1 = Math.Abs(Action.j1 * State.joint_speeds[0])
    var a2 = Math.Abs(Action.j2 * State.joint_speeds[1])
    var a3 = Math.Abs(Action.j3 * State.joint_speeds[2])
    var a4 = Math.Abs(Action.j4 * State.joint_speeds[3])
    var a5 = Math.Abs(Action.j5 * State.joint_speeds[4])
    var a6 = Math.Abs(Action.j6 * State.joint_speeds[5])
    var a7 = Math.Abs(Action.j7 * State.joint_speeds[6])
    var a6 = Math.Abs(Action.j6 * State.joint_speeds[7])

    var electricity_cost =  ((a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8) / 8)
    electricity_cost = (electricity * electricity_cost) + (stall_torque_cost * ((Action.j1 * Action.j1 + Action.j2 * Action.j2 + Action.j3 * Action.j3 + Action.j4 * Action.j4 + Action.j5 * Action.j5 + Action.j6 * Action.j6 + Action.j7 * Action.j7 + Action.j8 * Action.j8) / 8))

    var joints_at_limit_cost = -0.01 * State.joints_at_limit
    var rew = State.progress + electricity_cost + joints_at_limit_cost

    return rew
}