# hapic_workshop

Hapic workshop: Discover hapic

# Requirement

* Python3.4 or Python3.5 or Python3.4 
* vlc

# Install

Create a virtualenv

    virtualenv --no-site-packages -p /usr/bin/python3 venv

Source it

    source venv/bin/activate

Install requirements

    pip install -r requirements.txt

# Objectives

* Control input path, query and output data structure
* Generate doc about the routes
* Generate html view about the routes
* Manage exception at view level
* Manage uncatched errors
* Personalize error response
* Change the web framework

# Workshop

Read [workshop/01-start.md](workshop/01-start.md) for start. To summary:

* 01
  * Write flask view
  * Decorate with hapic to have it in generated doc
* 02
  * Write and decorate view who return list of models
  * Try to make wrong http request
  * Try to make wrong http response
* 03
  * Write and decorate a view to upload a file
* 04
  * Write and decorate a view with error handling
  * Use your own error builder
* 05
  * Manage all uncatched exceptions
* 06
  * Change web framework


File `run.py` contains compiled workshop work.
