# EpiBOX


This package is complementary to the mobile app EpiBOX (available at [EpiBOX](https://github.com/anascacais/rPiInterface)).

Designed for use with Raspberry Pi, it acts as an autonomous recording unit - allowing for sensor connectivity and data storage. EpiBOX mobile app provides the user interaface and the near-real time visualization of the data. 

Currently, EpiBOX supports BITalino-based equipments allowing for the recording, storage and visualization of up to 12 channels simmultaneously. Nevertheless, this package can be easily integrated with other sensors, as long as a python API is provided!

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install epibox.

```bash
pip install epibox
or 
pip install --upgrade epibox
```

## Usage

```python
from epibox import startup

# this will initiate the process - which should be continued by the user interface (EpiBOX)
startup.main() 
```

## Other info
* Licence [MIT](https://choosealicense.com/licenses/mit/)
* Documentation: https://epibox.readthedocs.io.

## Contact
For any additional information please contact me: anascacais@gmail.com
EpiBOX is a Raspberry Pi tool for easy signal acquisition.



This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


.. image:: https://img.shields.io/pypi/v/epibox.svg
        :target: https://pypi.python.org/pypi/epibox

.. image:: https://img.shields.io/travis/anascacais/epibox.svg
        :target: https://travis-ci.com/anascacais/epibox

.. image:: https://readthedocs.org/projects/epibox/badge/?version=latest
        :target: https://epibox.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status