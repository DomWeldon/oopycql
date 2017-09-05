What? Why?
==========

OOPyCQL is a library designed to make the handling of cypher queries easier in python by providing an object interface for a cypher query. Wait, but why?

I ❤ Cypher and I ❤ Python. But sometimes, this relationship gets a little complicated. Cypher (CQL) is a brilliant language which is expressive, intuitive and feature-rich (especially with libraries like APOC), and often a complex set of database actions can be conducted in a single transaction using just a few lines, saving lots of time and back-and-forth operations in python. In part, CQL is so expressive because it is based on the use of ASCII-art to describe patterns and relationships, which makes queries simple to understand by simply looking at it. Python, too, is a powerful and expressive language, and what makes good code 'pythonic' is often well-formatted (PEP8 compliant) code which is declarative and straightforward to read. Herein lies the problem: often I want to write a python program that takes a complex cypher query, runs it in my graph, and takes the results and does something with them (for example, in a Flask view). This means that my python program is reliant on a long string of CQL, which I care about and want to be able to edit and tweak, but which is a pain to put in my python script, and can make for some ugly looking code.

See the examples below.

    q = ('CREATE (this:Style { name: "Quoted text in Parentheses" })-[:IS]->'
         '(:Jugement {
         '  value: "Just plain ugly"'  # look at this ambiguous whitespace :-(
         '})')

    q = '''  // look at all this whitespace!! and 79 ch limit is pain in the..
        CREATE (this:Style { name: "Triple Quotes" })-[:IS]->(m:Modifier {
            value: "less"
        })-[:THAN]->(other:Style { name "Quoted text in Parentheses" })
        -[:BUT]->(:Jugement { value: "Still not great" })'''

Do your eyes hurt yet? These styles are obviously a distraction from writing good cypher: they confuse code lexers and produce weird formatting, make it a pain to spot bugs and syntax errors, and, well, just tire out my fingers sorting out all the whitespace and quotes flying around everywhere. Furthermore, if you're building queries dynamically and want to use the formatting mini-language, then you get the added bonus of having to escape parentheses (e.g. ``{{ param_name }}``) in some queries but not others.

So just use a file, right? Sure, you could load this from a file using `open()`, but (and here's where it gets a little subjective) that just feels wrong. You have to decide where to keep the file relative to the code your working on (same directory, different directory, a central "queries" directory?) and figure out how to access it - something that can be a real pain if you're working in a framework like Flask or Django where ``__file__`` will have a limited relationship to ``os.getcwd()``. What's more, you probably don't want to put all your queries in files (so where do you draw the line), and if you're building a complex query that depends on a few arguments you need to decide whether to split them, load some parts but not others, etc., etc.

Python is an object oriented language, and OOPyCQL aims to implement an object-oriented interface for CQL queries which allows you to define, load, share and run Cypher queries in an application without getting caught up worrying about strings. 
