.. _code_directive:

-------------------------------------

Save and Load
''''''''''''''

Saving and loading models is desired as the learning proces of a model for ``pyd3`` can take up to hours.
In order to accomplish this, we created two functions: function :func:`pyd3.save` and function :func:`pyd3.load`
Below we illustrate how to save and load models.


Saving
----------------

Saving a learned model can be done using the function :func:`pyd3.save`:

.. code:: python

    import pyd3

    # Load example data
    X,y_true = pyd3.load_example()

    # Learn model
    model = pyd3.fit_transform(X, y_true, pos_label='bad')

    Save model
    status = pyd3.save(model, 'learned_model_v1')



Loading
----------------------

Loading a learned model can be done using the function :func:`pyd3.load`:

.. code:: python

    import pyd3

    # Load model
    model = pyd3.load(model, 'learned_model_v1')

.. raw:: html

	<hr>
	<center>
		<script async type="text/javascript" src="//cdn.carbonads.com/carbon.js?serve=CEADP27U&placement=erdogantgithubio" id="_carbonads_js"></script>
	</center>
	<hr>
