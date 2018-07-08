# 04

## 04-1

Hapic permit to manage error at view level and make an error response
according to it. Write a view who permit to get information about a file:

``` python
import os

from flask.json import jsonify

app = Flask('vlc control')


@app.route('/file/<file>')
def file(file):
    infos = {
        'name': file,
        'size': os.path.getsize(file),
    }

    if request.args.get('verbose'):
        infos['is_link'] = os.path.islink(file)

    return jsonify(infos)

app.run(debug=True)
```

## 04-2

Now, add `@hapic.input_path` decorator with appropriate Schema, 
`@hapic.output_body` decorator with appropriate Schema and add 
`@hapic.handle_exception(FileNotFoundError, http_code=400)` to catch
error when `os.path.getsize` function can't found the given file.

If you make a query specifying a wrong file path, eg.
`http :5000/file/foobarbaz.avi` you will get an Bad request error response.

## 04-3

Solution:

``` python
import hapic
from flask import Flask, request
import marshmallow
import os

from flask.json import jsonify
from hapic.ext.flask import FlaskContext

app = Flask('vlc control')


class FilePathSchema(marshmallow.Schema):
    file = marshmallow.fields.String(
        required=True,
        description='file path to get info',
        example='bird.avi',
    )


class FileQuerySchema(marshmallow.Schema):
    verbose = marshmallow.fields.Integer(
        required=False,
        description='Get more infos about file',
        example='1',
        default=0,
    )


class FileInfoSchema(marshmallow.Schema):
    name = marshmallow.fields.String(
        required=True,
    )
    size = marshmallow.fields.String(
        required=False,
    )
    is_link = marshmallow.fields.Boolean(
        required=False,
        allow_none=True,
    )


@hapic.with_api_doc()
@app.route('/file/<file>')
@hapic.handle_exception(FileNotFoundError, http_code=400)
@hapic.input_path(FilePathSchema())
@hapic.input_query(FileQuerySchema())
@hapic.output_body(FileInfoSchema())
def file(file, hapic_data):
    infos = {
        'name': hapic_data.path['file'],
        'size': os.path.getsize(file),
    }

    if hapic_data.query.get('verbose'):
        infos['is_link'] = os.path.islink(hapic_data.path['file'])

    return jsonify(infos)


context = FlaskContext(app)
hapic.set_context(context)
hapic.add_documentation_view('/api/doc')

app.run(debug=True)
```

## 04-4

`@hapic.handle_exception` decorator permit to personalize error response.
Take this view:

``` python
from os.path import isfile

from flask import Flask
import vlc
import hapic
import marshmallow
from hapic.ext.flask import FlaskContext

app = Flask('vlc control')


class VlcPlayProblem(Exception):
    def __init__(self, message, detail=None):
        super().__init__(message)
        self.error_detail = detail


class PlayFilePathSchema(marshmallow.Schema):
    file = marshmallow.fields.String(
        required=True,
        description='file path to play',
        example='bird.avi',
    )


class EmptyResponseSchema(marshmallow.Schema):
    pass


@hapic.with_api_doc()
@app.route('/play/<file>')
@hapic.handle_exception(VlcPlayProblem)
@hapic.input_path(PlayFilePathSchema())
@hapic.output_body(EmptyResponseSchema(), default_http_code=204)
def play_file(file, hapic_data):
    file_name = hapic_data.path['file']
    player = vlc.MediaPlayer(file_name)

    if not isfile(file_name):
        raise VlcPlayProblem(
            'Error when trying to read "{}": file not exist'.format(
                file_name,
            ),
            detail=dict(
                file_path=file_name,
            )
        )

    player.play()
    return '', 204


# doc view
context = FlaskContext(app)
hapic.set_context(context)
hapic.add_documentation_view('/api/doc')

# run server
app.run(debug=True)
```

Write a child class of `hapic.error.ErrorBuilderInterface`: It is a
Marshmallow Schema with to methods to implement:

``` python
class ErrorBuilderInterface(marshmallow.Schema):
    """
    ErrorBuilder is a class who represent a Schema (marshmallow.Schema) and
    can generate a response content from exception (build_from_exception)
    """
    def build_from_exception(
        self,
        exception: Exception,
        include_traceback: bool = False,
    ) -> dict:
        """
        Build the error response content from given exception
        :param exception: Original exception who invoke this method
        :return: a dict representing the error response content
        """
        raise NotImplementedError()

    def build_from_validation_error(
        self,
        error: ProcessValidationError,
    ) -> dict:
        """
        Build the error response content from given process validation error
        :param error: Original ProcessValidationError who invoke this method
        :return: a dict representing the error response content
        """
        raise NotImplementedError()
```

Then add it to `@hapic.handle_exception` decorator with `error_builder`
parameter.

Now, when making a request with a wrong file path, error structure is yours.

# 04-5

Solution:


``` python
from os.path import isfile

from flask import Flask
import vlc
import hapic
import marshmallow
from hapic.ext.flask import FlaskContext

app = Flask('vlc control')


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


class VlcPlayProblem(Exception):
    def __init__(self, message, detail=None):
        super().__init__(message)
        self.error_detail = detail


class PlayFilePathSchema(marshmallow.Schema):
    file = marshmallow.fields.String(
        required=True,
        description='file path to play',
        example='bird.avi',
    )


class EmptyResponseSchema(marshmallow.Schema):
    pass


@hapic.with_api_doc()
@app.route('/play/<file>')
@hapic.handle_exception(VlcPlayProblem)
@hapic.input_path(PlayFilePathSchema())
@hapic.output_body(EmptyResponseSchema(), default_http_code=204)
def play_file(file, hapic_data):
    file_name = hapic_data.path['file']
    player = vlc.MediaPlayer(file_name)

    if not isfile(file_name):
        raise VlcPlayProblem(
            'Error when trying to read "{}": file not exist'.format(
                file_name,
            ),
            detail=dict(
                file_path=file_name,
            )
        )

    player.play()
    return '', 204


# doc view
context = FlaskContext(app)
hapic.set_context(context)
hapic.add_documentation_view('/api/doc')

# run server
app.run(debug=True)
```

## 04-6

You can parametrize hapic to always use your `ErrorBuilder` class. Simply
add `context.default_error_builder = ErrorBuilder()` after
`context = FlaskContext(app)` line. All `@hapic.handle_exception` will use
this error builder if no `error_builder` is specified.
