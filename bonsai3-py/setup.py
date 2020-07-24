import logging
from setuptools import setup, find_packages

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
log.debug('Running setup...')

version = {}
with open("./bonsai3/version.py") as fp:
    exec(fp.read(), version)
setup(
    name="bonsai3",
    version=version['__version__'],
    description="Simulator interface library for Bonsai AI platform v3",
    long_description=open('README.md').read(),
    url="https://bons.ai",
    author="Microsoft, Inc.",
    author_email='opensource@bons.ai',
    license="BSD",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Natural Language :: English'
    ],
    keywords="bonsai",
    install_requires=[
        'wheel>=0.31.0',
        'requests>=2.18',
        'jsons==1.0.0',
    ],
    python_requires='>=3.5',
    packages=find_packages(),
)
