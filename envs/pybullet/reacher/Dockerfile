# this is one of the cached base images available for ACI
FROM python:3.8.3

# Install libraries and dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends &&\
  apt-get install -y git \
  && rm -rf /var/lib/apt/lists/* 
   
# Install SDK3 Python
COPY connectors ./connectors
RUN pip3 install -U setuptools \
  && cd connectors \
  && pip3 install . \
  && pip3 install gym \
  && pip3 install microsoft-bonsai-api \
  && git clone https://github.com/Talos-Lab/pybullet-gym.git \
  && cd pybullet-gym \
  && pip3 install -e . 

# Set up the simulator
WORKDIR /sim

# Copy simulator files to /sim
COPY envs/pybullet/reacher/reacher.py \
     envs/pybullet/reacher/simulator_interface.json \
     /sim/ 


# This will be the command to run the simulator
CMD ["python", "reacher.py", "--headless", "--verbose"]