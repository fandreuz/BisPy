from setuptools import setup, find_packages

import bisimulation_algorithms as bs_alg

setup(
    name=bs_alg.__name__,
    version=bs_alg.__version__,
    author=bs_alg.__author__,
    author_email=bs_alg.__email__,
    packages=find_packages(),
    license="MIT",
    description="Python implementation of some algorithms for the computation of the maximum bisimulation",
    install_requires=['llist', 'networkx']
)
