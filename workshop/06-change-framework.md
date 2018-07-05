# 06

# 06.1

Hapic own 3 context permitting to use 3 web framework:

* `hapic.ext.flask.context.FlaskContext`
* `hapic.ext.bottle.context.BottleContext`
* `hapic.ext.pyramid.context.PyramidContext`

And you can write your own context (implement `hapic.context.BaseContext`) to
be compatible with other framework.

Now, try to write your own web server with web framework of your choice.
