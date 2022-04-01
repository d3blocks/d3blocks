.. _code_directive:

-------------------------------------

Save and Load
''''''''''''''

Saving and loading models is desired as the learning proces of a model for ``d3blocks`` can take up to hours.
In order to accomplish this, we created two functions: function :func:`d3blocks.save` and function :func:`d3blocks.load`
Below we illustrate how to save and load models.


Saving
----------------

Saving a learned model can be done using the function :func:`d3blocks.save`:

.. code:: python

    import d3blocks

    # Load example data
    X,y_true = d3blocks.load_example()

    # Learn model
    model = d3blocks.fit_transform(X, y_true, pos_label='bad')

    Save model
    status = d3blocks.save(model, 'learned_model_v1')



Loading
----------------------

Loading a learned model can be done using the function :func:`d3blocks.load`:

.. code:: python

    import d3blocks

    # Load model
    model = d3blocks.load(model, 'learned_model_v1')

.. raw:: html

	<hr>
	<center>
		<script async type="text/javascript" src="//cdn.carbonads.com/carbon.js?serve=CEADP27U&placement=erdogantgithubio" id="_carbonads_js"></script>
	</center>
	<hr>
