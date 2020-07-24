Bonsai SDK
==========

A python library for integrating data sources with Bonsai BRAIN.


Installation
------------
Install this library from source (assuming you are in this directory)
    `$ pip install .`

Usage
-----
Clients will subclass `bonsai3.SimulatorSession` and implement the required methods.

Example:
```python

    #!/usr/bin/env python3

    import sys
    from bonsai3 import SimulatorSession, SimulatorInterface, ServiceConfig, Schema

    class SimModel(SimulatorSession):
        def get_state(self) -> Schema:
        """ Called to retrieve the current state of the simulator. """
            pass

        def get_interface(self) -> SimulatorInterface:
        """ Called to retrieve the simulator interface during registration. """
            pass
        
        def halted(self) -> bool
            """
            Should return weather the episode is halted, and
            no further action will result in a state.
            """
            pass

        def episode_start(self, config: Schema):
        """ Called at the start of each episode """
            pass
        
        def episode_step(self, action: Schema):
        """ Called for each step of the episode """
            pass
```

Then, the simulator is configured and run. The ServiceConfig class takes care of
argument and environment variable parsing.

```python

    if __name__ == "__main__":
        config = ServiceConfig(argv=sys.argv)
        sim = SimModel(config)
        while sim.run():
            continue
```

Example of how to run simulator from a local machine.
    `python mysim.py --workspace <WORKSPACE> --accesskey <ACCESSKEY>`

You can also set these in your unix shell with:
```sh
export SIM_ACCESS_KEY=<your-access-key>
export SIM_WORKSPACE=<your-workspace>
export SIM_API_HOST=<your-api-host>
```

When a simulator is run on the platform, the environment variables will be set and picked up by ServiceConfig.

Running tests using Dockerfile
------------------------------
To build dockerfile:
    `docker build -t testbonsai3 -f Dockerfile ./`

To run tests:
    `docker run testbonsai3`


Microsoft Open Source Code of Conduct
==========

This repository is subject to the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct).
