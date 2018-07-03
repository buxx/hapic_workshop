# coding: utf-8
import os
import traceback
from datetime import datetime

import marshmallow
import vlc
import hapic
from flask import Flask

from os import listdir
from os.path import isfile
from os.path import join

from hapic.error import ErrorBuilderInterface
from hapic.ext.flask import FlaskContext

# Flask app
from hapic.processor import ProcessValidationError

app = Flask('vlc control')


# Schemas
class EmptyResponseSchema(marshmallow.Schema):
    pass


class SendInputPathSchema(marshmallow.Schema):
    file_name = marshmallow.fields.String(required=True)


class SendInputFilesSchema(marshmallow.Schema):
    file = marshmallow.fields.Raw(required=True)


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


class PlayFilePathSchema(marshmallow.Schema):
    file = marshmallow.fields.String(
        required=True,
        description='file path to play',
        example='bird.avi',
    )


# Models
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


# Exceptions
class VlcPlayProblem(Exception):
    def __init__(self, message, detail=None):
        super().__init__(message)
        self.error_detail = detail


# Error builders
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


# Routes
@hapic.with_api_doc()
@app.route('/bird')
@hapic.output_body(EmptyResponseSchema(), default_http_code=204)
def play_bird_avi():
    player = vlc.MediaPlayer('bird.avi')
    player.play()
    return '', 204


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


@hapic.with_api_doc()
@app.route('/send/<file_name>', methods=['POST'])
@hapic.input_path(SendInputPathSchema())
@hapic.input_files(SendInputFilesSchema())
@hapic.output_body(EmptyResponseSchema(), default_http_code=204)
def send(file_name, hapic_data):
    with open(file_name, 'wb+') as file:
        file.write(hapic_data.files['file'].read())

    return '', 204


@hapic.with_api_doc()
@app.route('/file/<file>')
@hapic.handle_exception(FileNotFoundError, http_code=400)
@hapic.input_path(FilePathSchema())
@hapic.input_query(FileQuerySchema())
@hapic.output_body(FileInfoSchema())
def file(file, hapic_data):
    infos = {
        'name': file,
        'size': os.path.getsize(file),
    }

    if hapic_data.query.get('verbose'):
        infos['is_link'] = os.path.islink(file)

    return infos


@hapic.with_api_doc()
@app.route('/play/<file>')
@hapic.handle_exception(VlcPlayProblem, error_builder=ErrorBuilder())
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

# Set our error builder
context.default_error_builder = ErrorBuilder()
# Enabme debug mode
context.debug = True

# run server
app.run(debug=True)
