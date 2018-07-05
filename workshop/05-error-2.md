# 05

# 05.1

Hapic permit to catch non caught error at view level. Write an error view:

``` python
from flask import Flask
import hapic
from hapic.ext.flask import FlaskContext


@hapic.with_api_doc()
@app.route('/error')
@hapic.output_body(EmptyResponseSchema(), default_http_code=204)
def error():
    1/0

# doc view
context = FlaskContext(app)
hapic.set_context(context)
hapic.add_documentation_view('/api/doc')

# run server
app.run(debug=True)
```

The `handle_exception(ExceptionClass, http_code=500)` context method configure
hapic and your web framework to manage non caught errors. Add it before the
`app.run(debug=True)` line.

Try to call this endpoint with `http :5000/error`: An error response will be
returned.

# 05.2

Solution:

``` python
import hapic
from flask import Flask

from hapic.ext.flask import FlaskContext


# Flask app
app = Flask('vlc control')


@hapic.with_api_doc()
@app.route('/error')
@hapic.output_body(EmptyResponseSchema(), default_http_code=204)
def error():
    1/0


# doc view
context = FlaskContext(app)
hapic.set_context(context)
hapic.add_documentation_view('/api/doc')

# Set our error builder
context.default_error_builder = ErrorBuilder()
context.handle_exception(Exception, http_code=500)
context.handle_exception(ZeroDivisionError, http_code=500)
# Enable debug mode
context.debug = True

# run server
app.run(debug=True)
```
