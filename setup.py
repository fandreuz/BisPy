import setuptools

long_description = """
![Python package](https://github.com/fAndreuzzi/BisPy/workflows/Python%20package/badge.svg?branch=master) <a href='https://coveralls.io/github/fAndreuzzi/BisPy'><img src='https://coveralls.io/repos/github/fAndreuzzi/BisPy/badge.svg' alt='Coverage Status' /></a>
 [![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE) <img src='https://img.shields.io/badge/Code%20style-Black-%23000000'/> [![Documentation Status](https://readthedocs.org/projects/bispy-bisimulation-in-python/badge/?version=latest)](https://bispy-bisimulation-in-python.readthedocs.io/en/latest/?badge=latest)

## Description
**BisPy** is a Python package for the computation of the maximum bisimulation of directed graphs. At the moment it supports the following algorithms:
- Paige-Tarjan
- Dovier-Piazza-Policriti
- Saha

An extended version of this README can be found [here](https://github.com/fAndreuzzi/BisPy).

## Authors and acknowledgements
**BisPy** is currently developed and mantained by **Francesco Andreuzzi**.
You can contact me at:
* andreuzzi.francesco at gmail.com
* fandreuz at sissa.it

## License
See the [LICENSE](LICENSE) file for license rights and limitations (MIT).
"""

setuptools.setup(
    name="BisPy",
    version="0.1.3",

    author="Francesco Andreuzzi",
    author_email="andreuzzi.francesco@gmail.com",

    description="A bisimulation library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/fAndreuzzi/BisPy",
    project_urls={
        "Bug Tracker": "https://github.com/fAndreuzzi/BisPy/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics'
    ],

    packages=setuptools.find_packages(),
    python_requires=">=3.5",

    license='MIT',

    install_requires=['networkx', 'llist'],
)
