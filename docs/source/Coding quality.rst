
Coding quality
'''''''''''''''''''''

I value software quality. Higher quality software has fewer defects, better security, and better performance, which leads to happier users who can work more effectively. Code reviews are an effective method for improving software quality. 

This library is therefore developed with several techniques, such as coding styling, low complexity, docstrings.
Such conventions are helpfull to improve the quality, make the code cleaner and more understandable but alos to trace future bugs, and spot syntax errors.


library
-------

The file structure of the generated package looks like:


.. code-block:: bash

    path/to/d3blocks/
    ├── .editorconfig
    ├── .gitignore
    ├── .pre-commit-config.yml
    ├── .prospector.yml
    ├── CHANGELOG.rst
    ├── docs
    │   ├── conf.py
    │   ├── index.rst
    │   └── ...
    ├── LICENSE
    ├── MANIFEST.in
    ├── NOTICE
    ├── d3blocks
    │   ├── __init__.py
    │   ├── __version__.py
    │   └── d3blocks.py
    ├── README.md
    ├── requirements.txt
    ├── setup.cfg
    ├── setup.py
    └── tests
        ├── __init__.py
        └── test_d3blocks.py


Style
-----

This library is compliant with the PEP-8 standards.
PEP stands for Python Enhancement Proposal and sets a baseline for the readability of Python code.
Each public function contains a docstring that is based on numpy standards.
    

Complexity
----------

Developing software with low(er) technical dept may take extra development time, but has many advantages:

* Higher quality code
* easier maintanable
* Less prone to bugs and errors
* Higher security




.. include:: add_bottom.add