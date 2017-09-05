.. OOPyCQL documentation master file, created by
   sphinx-quickstart on Mon Sep  4 19:32:00 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

OOPyCQL
=======

.. image:: https://travis-ci.org/DomWeldon/oopycql.svg?branch=master
  :target: https://travis-ci.org/DomWeldon/oopycql

.. image:: https://coveralls.io/repos/github/DomWeldon/oopycql/badge.svg?branch=master
  :target: https://coveralls.io/github/DomWeldon/oopycql?branch=master

OOPyCQL provides an object-oriented interface for working with Cypher queries in Python. It also sounds a little like the word bicycle.

.. toctree::
   :maxdepth: 2
   :caption: Contents:


What? Why?
==========

OOPyCQL is a library designed to make the handling of cypher queries easier in python by providing an object interface for a cypher query. But, wait, why?

I ❤ Cypher and I ❤ Python. But sometimes, this relationship gets a little complicated. Cypher (CQL) is a brilliant language which is expressive, intuitive and feature-rich (especially with libraries like APOC). Often a complex set of database actions can be conducted in a single transaction using just a few lines, saving lots of time and back-and-forth operations in python. In part, CQL is so expressive because it is based on the use of ASCII-art to describe patterns and relationships, making queries simple to understand by simply looking at it. Python, too, is a powerful and expressive language, and and good, 'pythonic' code is declarative and straightforward to read. Herein lies the problem: often I want to write a python program that takes a complex cypher query, runs it in my graph, and takes the results and does something with them (for example, in a Flask view). This means that my python program is reliant on a long string of CQL, which I care about and want to be able to edit and tweak, but which is a pain to put in my python script, and can make for some ugly looking code.

See the examples below.

.. code-block:: python

  q = ('CREATE (this:Style {name: "Quoted text in Parentheses"})-[:IS]->'
      '(:Judgement {value: "Just plain ugly"})')  # eugh :'-(


  q = '''// look at all this whitespace!! Plus 79 char limit is pain in the ar
      CREATE (this:Style {name: "Triple Quotes"})
             -[:IS]->
             (m:Modifier {value: "less"})
             -[:THAN]->
             (other:Style { name "Quoted text in Parentheses" })
             -[:BUT]->(:Judgement { value: "Still not great" })'''


Do your eyes hurt yet? These styles are obviously a distraction from writing good cypher: they confuse code lexers and produce weird formatting, make it a pain to spot bugs and syntax errors, and, well, just tire out my fingers sorting out all the whitespace and quotes flying around everywhere. Furthermore, if you're building queries dynamically and want to use the formatting mini-language, then you get the added bonus of having to escape parentheses (e.g. ``{{ param_name }}``) in some queries but not others (to mention just one problem).

Unfortunately the discipline and formatting required to write good python code (i.e., PEP8), makes it hard to include long and nicely formatted cypher queries directly in your code.

So just use a file, right? Sure, you could load this from a file using `open()`, but (and here's where it gets a little subjective), that just *feels* wrong. You have to decide where to keep the file relative to the code your working on (same directory, different directory, a central "queries" directory?) and figure out how to access it - something that can be a real pain if you're working in a framework like Flask or Django where ``__file__`` will have a limited relationship to ``os.getcwd()``. What's more, you probably don't want to put all your queries in files (so where do you draw the line), and if you're building a complex query that depends on a few arguments you need to decide whether to split them, load some parts but not others, etc., etc.

Here's where OOPyCQL comes in. Python is an object oriented language, and this library implements an object-oriented interface for CQL queries which allows you to define, load, share and run Cypher queries in an application without getting caught up worrying about strings. What's more, you can refer to cypher queries just like you would a python object.

For example, if you had one of the queries above in a file called ``src/examples/cql/style.cql``, you can reference the query using ``CypherQuery('src.examples.cql.style')``

Using CypherQuery
=================

The main feature of the library is ``oopycql.query.CypherQuery`` which can be imported directly from ``oopycql``.

.. code-block:: python

  from oopycql import CypherQuery

The default behaviour is to import queries just like one would a normal python class or object (see below), but several other methods are supported, and the class can be subclassed to produce complex dynamic queries.

Loading a Cypher Query Like an Object
-------------------------------------

Load a query from a file using the same pythonic reference notation you would to load an object.

For example, let's imagine you have an application with a directory structure like the below.

.. code-block:: text

  src/
  ├-controllers/
  │ └-login/
  │   ├-cql/
  │   │ ├─find_user_password_combination.cql
  │   │ └─create_login_event.cql
  |   ├─__init__.py
  |   └─views.py
  ├─__init__.py
  └─app.py


To load a query in ``views.py``, you could use the below:

.. code-block:: python

  from oopycql import CypherQuery

  # relative style import
  cq = CypherQuery('.cql.find_user_password')

  # absolute style import
  cq = CypherQuery('src.controllers.login.cql.create_login_event')


Loading a Cypher Query as a String
----------------------------------

Queries don't have to be loaded from a file, and can be loaded as a string by specifying ``query`` as a keyword argument to the constructor, or adjusting the ``query`` property of a CypherQuery. For example:

.. code-block:: python

  from oopycql import CypherQuery

  count_query = CypherQuery(query='MATCH (n) RETURN COUNT(n)')

  # or alternatively...
  count_query2 = CypherQuery()
  count_query2.query = 'MATCH (n) RETURN COUNT(n)'


Subclassing ``CypherQuery`` for Complex Queries
-----------------------------------------------

Sometimes you'll want to create compelx queries based on logic to do with outside values. The CypherQuery object can be subclassed to provide a handy base object for just this kind of operation. Simply store the final query value in ``self._query`` to retain parameter functions.

.. code-block:: python

  from oopycql import CypherQuery


  class MyComplexQuery(CypherQuery):
      def __init__(self):
          self._query = 'CREATE (a:Node) SET a += {a_params}'

      def set_return_node_id(self):
          """Call this method to make the query return the ``id`` of
          ``a``"""
          self._query += '\nRETURN id(a) AS a_id'

  cq = MyComplexQuery()
  cq.set_return_node_id()

  assert 'RETURN id(a) AS a_id' in str(cq)
  assert 'a_params' in cq.params


Parameters
----------

Parameters in the query are identified using a regular expression stored in ``oopycql.cypher.CypherReference.PARAM_FINDING_REGEX``. You can store values for these parameters to pass when the query is run in the ``CypherQuery.params`` property.

For example, if you are using the py2neo driver, you can do the following.

.. code-block:: python

  # import libs
  from oopycql import CypherQuery
  from py2neo import Graph

  # connect to example graph
  graph = Graph('bolt://neo4j:neo4j@localhost/db/data')

  # create query from string
  cq = CypherQuery('CREATE (a:Node) SET a += {node_params}')

  # assign a value to the parameter
  cq.params['node_params'] = {'example': True}

  # run the query
  graph.run(cq.query, parameters=cq.params)


``CypherQuery`` also supports iteration, designed for use with drivers which support a method like ``run(query, parameters)``. This style is supported by py2neo and the default neo4j python driver. This means you can use star unpacking, like the below example with py2neo.

.. code-block:: python

  # list(cq) == (cq.query, cq.params)
  # run the query
  graph.run(*cq)


API
===

.. py:currentmodule:: oopycql

.. autoclass:: AbstractCypherQuery
  :members:

.. autoclass:: CypherQuery
  :members:

.. py:currentmodule:: oopycql.oopycql_collections

.. autoclass:: ParameterSet
  :members:

.. autoclass:: ParameterMap
  :members:

.. py:currentmodule:: oopycql.errors

.. autoclass:: ParameterNotSetError
  :members:

.. py:currentmodule:: oopycql.cypher

.. autoclass:: CypherReference
  :members:





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
