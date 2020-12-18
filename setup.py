from setuptools import setup, find_packages

setup(
    name="bisimulation_algorithms",
    version="0.0.1",
    author="Francesco Andreuzzi",
    author_email="andreuzzi.francesco@gmail.com",
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    license="LICENSE",
    description="Python implementation of some algorithms for the computation of the maximum bisimulation",
    install_requires=['llist', 'networkx']
)
