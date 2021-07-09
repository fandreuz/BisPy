"""A Python package for computing the maximal bisimulation of directed graphs

.. moduleauthor:: Francesco Andreuzzi <andreuzzi.francesco@gmail.com>

"""

__author__ = "Francesco Andreuzzi"
__copyright__ = "Copyright 2020"
__credits__ = ["Francesco Andreuzzi"]
__license__ = "MIT"
__release__ = "0.0"
__subrelease__ = "1"
__version__ = __release__ + "." + __subrelease__
__maintainer__ = "Francesco Andreuzzi"
__email__ = "andreuzzi.francesco@gmail.com"
__status__ = "Development"
__name__ = "bispy"

from .paige_tarjan.paige_tarjan import rscp as paige_tarjan
from .dovier_piazza_policriti.dovier_piazza_policriti import rscp as dovier_piazza_policriti
from .saha.saha import update_rscp as saha
