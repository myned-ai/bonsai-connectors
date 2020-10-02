# this is one of the cached base images available for ACI
FROM python:3.8.3

# Install libraries and dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  && apt-get install -y python-opengl \
  && apt-get install -y libgl1-mesa-glx \
  && apt-get install -y xvfb \
  && rm -rf /var/lib/apt/lists/*

# Install SDK3 Python
COPY connectors ./connectors
RUN cd connectors \
  && pip3 install . \
  setuptools \
  gym \
  numpy \
  pyglet==1.5.0 \
  Box2D \
  opencv-python \
  microsoft-bonsai-api==0.1.2 \
  https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp38-cp38-linux_x86_64.whl

# Set up the simulator
WORKDIR /sim

# Copy simulator files to /sim
COPY envs/box2d/CarRacing/carracing.py \
  envs/box2d/CarRacing/obswrapper.py \
  envs/box2d/CarRacing/simulator_interface.json \
  /sim/ 
COPY envs/box2d/CarRacing/autoencoder_model.tflite /sim/autoencoder_model.tflite 


# This will be the command to run the simulator
CMD xvfb-run --auto-servernum python carracing.py --headless --verbose
