# this is one of the cached base images available for ACI
FROM python:3.7.4

# Install libraries and dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*

# Install SDK3 Python
COPY simulator ./simulator
RUN pip3 install -U setuptools \
  && cd simulator \
  && pip3 install . \
  && pip3 install gym \
  && pip3 install microsoft-bonsai-api \
  && pip3 uninstall -y setuptools

# Set up the simulator
WORKDIR /sim

# Copy simulator files to /sim
COPY samples/Pendulum/pendulum.py \
     samples/Pendulum/simulator_interface.json \
     /sim/ 


# This will be the command to run the simulator
CMD ["python", "pendulum.py", "--verbose"]