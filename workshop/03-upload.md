# 03

## 03.1

To write a view with a file upload, use 
`@hapic.input_files(SendInputFilesSchema)` decorator. Example of Schema:

``` python
import marshmallow


class SendInputFilesSchema(marshmallow.Schema):
    file = marshmallow.fields.Raw(required=True)
```

## 03.2

We want give file name in api path. So, use 
`@hapic.input_path(SendInputPathSchema())` decorator with associated Schema.
Example:

``` python
import marshmallow


class SendInputPathSchema(marshmallow.Schema):
    file_name = marshmallow.fields.String(required=True)
```

## 03.3

Solution:


``` python
import flask
import vlc
import hapic
import marshmallow
from hapic.ext.flask import FlaskContext

app = Flask('vlc control')


# Schemas
class SendInputPathSchema(marshmallow.Schema):
    file_name = marshmallow.fields.String(required=True)


class SendInputFilesSchema(marshmallow.Schema):
    file = marshmallow.fields.Raw(required=True)


@hapic.with_api_doc()
@app.route('/send/<file_name>', methods=['POST'])
@hapic.input_path(SendInputPathSchema())
@hapic.input_files(SendInputFilesSchema())
@hapic.output_body(EmptyResponseSchema(), default_http_code=204)
def send(file_name, hapic_data):
    with open(file_name, 'wb+') as file:
        file.write(hapic_data.files['file'].read())

    return '', 204


context = FlaskContext(app)
hapic.set_context(context)
hapic.add_documentation_view('/api/doc')

app.run(debug=True)
```

To send a file, use `http -f :5000/send/foo.avi 'file@flame.avi'`.
