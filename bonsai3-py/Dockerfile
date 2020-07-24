# Dockerfile for bonsai3-py unit tests
FROM python:3.6.9-slim

RUN pip3 install -U \
      setuptools \
      aiohttp \
      pytest \
      pytest-cov \
      coverage

COPY ./ bonsai3

RUN pip3 install -e bonsai3/

WORKDIR bonsai3/

CMD ["pytest", \
     "--junit-xml", \
     "test-results/junit-linux-bonsai3-py.xml", \
     "--junit-prefix", \
     "src.sdk3.bonsai3-py",\
     "--cov"]
