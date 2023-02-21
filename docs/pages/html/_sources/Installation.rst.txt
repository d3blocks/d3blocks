Install from Pypi (pip)
########################

.. code-block:: console

    pip install d3blocks


Install from github
#####################################

.. code-block:: console

    pip install git+https://github.com/d3blocks/d3blocks


Create environment
#####################


If desired, install ``d3blocks`` from an isolated Python environment using conda:

.. code-block:: python

    conda create -n env_d3blocks python=3.10
    conda activate env_d3blocks



Uninstall
###############

If you want to remove your ``d3blocks`` installation with your environment, it can be as following:

.. code-block:: console

   # List all the active environments. d3blocks should be listed.
   conda env list

   # Remove the d3blocks environment
   conda env remove --name d3blocks

   # List all the active environments. d3blocks should be absent.
   conda env list



.. include:: add_bottom.add