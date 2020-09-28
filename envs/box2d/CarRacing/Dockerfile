# this is one of the cached base images available for ACI
FROM python:3.7.4

# Install libraries and dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  && apt-get install -y python-opengl \
  && apt-get install -y libgl1-mesa-glx \
  && apt-get install -y xvfb \
  && rm -rf /var/lib/apt/lists/*

# Install SDK3 Python
COPY connectors ./connectors
RUN pip3 install setuptools \
  && cd connectors \
  && pip3 install . \
  && pip3 install gym
RUN pip3 install tensorflow \
  && pip3 install numpy \
  && pip install pyglet
RUN pip3 install Box2D \
  && pip3 install opencv-python \
  && pip3 install microsoft-bonsai-api

# Set up the simulator
WORKDIR /sim

# Copy simulator files to /sim
COPY envs/box2d/CarRacing/carracing.py \
  envs/box2d/CarRacing/obswrapper.py \
  envs/box2d/CarRacing/simulator_interface.json \
  /sim/ 
COPY envs/box2d/CarRacing/autoencoder_model /sim/autoencoder_model     


# This will be the command to run the simulator
CMD xvfb-run --auto-servernum python carracing.py --headless --verbose
