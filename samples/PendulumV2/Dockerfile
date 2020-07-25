# this is one of the cached base images available for ACI
FROM python:3.7.4

# Install libraries and dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*

# Install SDK3 Python
RUN pip3 install -U setuptools \
  && pip3 install microsoft-bonsai-api \
  && pip3 install gym \
  && pip3 uninstall -y setuptools

# Set up the simulator
WORKDIR /sim

# Copy simulator files to /sim
COPY samples/PendulumV2/pendulum_gym.py \
     samples/PendulumV2/simulator_interface.json \
	 samples/PendulumV2/gymsimulator.py \
	 samples/PendulumV2/simmodel.py \
     /sim/ 


# This will be the command to run the simulator
CMD ["python", "pendulum_gym.py", "--verbose"]