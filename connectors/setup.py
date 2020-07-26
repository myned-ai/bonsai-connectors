import logging
from setuptools import setup, find_packages

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
log.debug('Running setup...')

version = {}
with open("./gym_connectors/version.py") as fp:
    exec(fp.read(), version)
setup(
    name="gym_connectors",
    version=version['__version__'],
    description="Simulator interface library",
    long_description="Simulator interface library for Open AI Gym and Microsoft Bonsai AI",
    url="https://github.com/Talos-Lab",
    author="Talos-Lab",
    author_email='goran.jakovljevic@parallax-solutions.co.uk',
    license="BSD",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English'
    ],
    keywords="gym_connectors",
    install_requires=[
        'wheel>=0.31.0',
        'requests>=2.18',
        'jsons==1.0.0',
    ],
    python_requires='>=3.6',
    packages=find_packages(),
)
