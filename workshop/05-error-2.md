# 05

# 05.1

Hapic permit to catch non caught error at view level. Write an error view:

``` python
from flask import Flask
import hapic
import marshmallow
from hapic.ext.flask import FlaskContext


class EmptyResponseSchema(marshmallow.Schema):
    pass


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
from flask import Flask
import hapic
from hapic.error import ErrorBuilderInterface
import marshmallow
from hapic.ext.flask import FlaskContext


class EmptyResponseSchema(marshmallow.Schema):
    pass


class ErrorBuilder(ErrorBuilderInterface):
    msg = marshmallow.fields.String(required=True)
    utc_datetime = marshmallow.fields.DateTime(required=False)
    traceback = marshmallow.fields.String(
        required=False,
        allow_none=True,
    )
    details = marshmallow.fields.Dict(
        required=False,
        allow_none=True,
    )

    def build_from_exception(
        self,
        exception: Exception,
        include_traceback: bool = False,
    ) -> dict:
        return {
            'msg': str(exception),
            'utc_datetime': datetime.utcnow(),
            'details': getattr(exception, 'error_detail', None),
            'traceback': traceback.format_exc() if include_traceback else None
        }

    def build_from_validation_error(
        self,
        error: ProcessValidationError,
    ) -> dict:
        return {
            'msg': error.message,
            'utc_datetime': datetime.utcnow(),
            'details': error.details,
        }


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
