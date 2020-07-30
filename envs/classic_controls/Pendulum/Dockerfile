# this is one of the cached base images available for ACI
FROM python:3.7.4

# Install libraries and dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*

# Install SDK3 Python
COPY connectors ./connectors
RUN pip3 install -U setuptools \
  && cd connectors \
  && pip3 install . \
  && pip3 install gym \
  && pip3 install microsoft-bonsai-api \
  && pip3 uninstall -y setuptools

# Set up the simulator
WORKDIR /sim

# Copy simulator files to /sim
COPY envs/classic_controls/Pendulum/pendulum.py \
     envs/classic_controls/Pendulum/simulator_interface.json \
     /sim/ 


# This will be the command to run the simulator
CMD ["python", "pendulum.py", "--headless", "--verbose"]