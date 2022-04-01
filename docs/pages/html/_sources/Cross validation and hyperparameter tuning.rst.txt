.. _code_directive:

-------------------------------------

Cross validation and hyperparameter tuning
'''''''''''''''''''''''''''''''''''''''''''

*Cross validation* and *hyperparameter tuning* are two tasks that we do together in the data pipeline.
*Cross validation* is the process of training learners using one set of data and testing it using a different set. We set a default of **5-fold crossvalidation** to evalute our results.
*Parameter tuning* is the process of selecting the values for a model’s parameters that maximize the accuracy of the model.

.. _five-fold_cross_validation:

.. figure:: ../figs/five-fold_cross_validation.png

 
Training and testing
--------------------

The model *sees* and *learns* from the data. To ensure stability in the model and results, we devide the data set into three parts with different sizes, namely: train-set, test-set and validation-set.
Each set has a different role, and is explained below.

Train dataset
    80% of the data is used to fit the model. The model sees and learns from this data.

Validation dataset
    The training data set is also split into 80% train and 20% validation set to evaluate the learned model and provide an unbiased evaluation of a model fit after tuning model hyperparameters.
    Evalution is performed in a 5-fold crossvalidation approach.

Test dataset
    20% of all the data is used only once the model is completely trained (using the train and validation sets).
    This will provide an unbiased result of the final model fit on the training dataset.


The use of training and testing is set as True by default, but can be changed with a boolean value ``train_test=True`` in the function :func:`urldetect.fit_transform` or :func:`urldetect.fit`.
You may want to set the boolean value at False ``train_test=False`` if the number of training samples is very low which would lead in a poorly trained model.


Gridsearch
----------

In ``urldetect`` we incorporated hyperparameter optimization using a gridseach :func:`urldetect._gridsearch`. The goal is to evaluate the value of the combination of parameters in the learning process.
The use of gridsearch is set True as default by a boolean value ``gridsearch=True`` in the function :func:`urldetect.fit_transform` or :func:`urldetect.fit`.
You may want to set this value at ``gridsearch=False`` if the number of samples is very low which would lead in a poorly trained model.


Hyperparameter optimization
---------------------------

In our gridsearch we evaluate the Term frequency–inverse document frequency (TF-IDF) and the logistic regression parameters.

.. code:: python

    param_grid = {
        'TfidfVectorizer__sublinear_tf': [True, False],
        'TfidfVectorizer__min_df': [5],
        'TfidfVectorizer__max_df': [0.5, 0.7],
        'TfidfVectorizer__norm': ['l1','l2'],
        'TfidfVectorizer__ngram_range': [(1,2),(1,3)],
    }


We evaluate in total **32** combination of parameters in the learning process.
To ensure stability, the 5-fold crossvalidation comes into play which leads to a total of **160** fits.
To speed up the gridsearch, we enable parallel processing. Each fit is scored based on Cohen's kappa coefficient and the parameters of the best fit are used.
With 8 cores, running at 2.8GHz (i7-7700HQ) it takes approximately **15** minutes without optimization and up to **>60** minutes to learn an optimized model. An example of the output is shown below:


.. raw:: html

	<hr>
	<center>
		<script async type="text/javascript" src="//cdn.carbonads.com/carbon.js?serve=CEADP27U&placement=erdogantgithubio" id="_carbonads_js"></script>
	</center>
	<hr>
