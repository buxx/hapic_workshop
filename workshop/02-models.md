# 02

## 02.1

We now want write a view who return list of instances. These instances
must be converted into http response.

Write `files` endpoint. It's jobs is to return the list of `.avi` files
available. This endpoint must have a `verbose` query parameter to add some
infos in response.

## 02.2

Example of file info model:

``` python
class FileInfo(object):
    def __init__(
        self,
        name,
        size,
        is_link=None,
    ):
        self.name = name
        self.size = size
        self.is_link = is_link
```

## 02.3

You must write an associated marshmallow Schema. Example:

``` python
import marshmallow


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
```

## 02.4

And a input query schema:

``` python
import marshmallow


class FileQuerySchema(marshmallow.Schema):
    verbose = marshmallow.fields.Integer(
        required=False,
        description='Get more info about file',
        example='1',
        default=0,
    )
```

## 02.5

Use these schema with hapic decorators: `@hapic.input_query(FileQuerySchema())`
and `@hapic.output_body(FileInfoSchema(many=True))`

## 02.6

Solution:

``` python
import os
from os import listdir
from os.path import isfile
from os.path import join

from flask import Flask
import hapic
import marshmallow
from hapic.ext.flask import FlaskContext

app = Flask('vlc control')


# The file model to use
class FileInfo(object):
    def __init__(
        self,
        name,
        size,
        is_link=None,
    ):
        self.name = name
        self.size = size
        self.is_link = is_link


# Schemas
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


class FileQuerySchema(marshmallow.Schema):
    verbose = marshmallow.fields.Integer(
        required=False,
        description='Get more infos about file',
        example='1',
        default=0,
    )


@hapic.with_api_doc()
@app.route('/files')
@hapic.input_query(FileQuerySchema())
@hapic.output_body(FileInfoSchema(many=True))
def files(hapic_data):
    file_models = []

    file_paths = [
        f for f in listdir('.')
        if isfile(join('.', f)) and f.endswith('.avi')
    ]

    for file_path in file_paths:
        file_model = FileInfo(
            name=file_path,
            size=os.path.getsize(file_path),
        )

        if hapic_data.query.get('verbose'):
            file_model.is_link = os.path.islink(file_path)

        file_models.append(file_model)

    return file_models


context = FlaskContext(app)
hapic.set_context(context)
hapic.add_documentation_view('/api/doc')

app.run(debug=True)
```

If you query this endpoint with `http ':5000/files?verbose=1'` you will see
the http response with file info list. Documentation of this endpoint is also
available (at `http://127.0.0.1:5000/api/doc`).

## 02.7

Try to send a bad query, like with `http ':5000/files?verbose=abc'`. You will
see an bad request http response.

## 02.8

Try to change the output schema without changing the response view. Like adding
a required field to `FileInfoSchema`. When trying to use the endpoint, an
internal server error will be shown because endpoint d'ont respect the
specified output schema.
