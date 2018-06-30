# coding: utf-8
import os

import marshmallow
import vlc
import hapic
from flask import Flask
from flask import request
from hapic.ext.flask import FlaskContext

# Flask app
app = Flask('vlc control')


# Schemas
class EmptyResponseSchema(marshmallow.Schema):
    pass


class PlayFilePathSchema(marshmallow.Schema):
    file = marshmallow.fields.String(
        required=True,
        description='file path to play',
        example='bird.avi',
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


class FileOutputSchema(marshmallow.Schema):
    name = marshmallow.fields.String(
        required=True,
    )
    size = marshmallow.fields.String(
        required=False,
    )
    is_link = marshmallow.fields.Boolean(
        required=False,
    )


# Routes
@hapic.with_api_doc()
@app.route('/bird')
@hapic.output_body(EmptyResponseSchema(), default_http_code=204)
def play_bird_avi():
    player = vlc.MediaPlayer('bird.avi')
    player.play()
    return '', 204


@hapic.with_api_doc()
@app.route('/play/<file>')
@hapic.input_path(PlayFilePathSchema())
@hapic.output_body(EmptyResponseSchema(), default_http_code=204)
def play_file(file, hapic_data):
    file_name = hapic_data.path['file']
    player = vlc.MediaPlayer(file_name)
    player.play()
    return '', 204


@hapic.with_api_doc()
@app.route('/file/<file>')
@hapic.handle_exception(FileNotFoundError, http_code=400)
@hapic.input_path(FilePathSchema())
@hapic.input_query(FileQuerySchema())
@hapic.output_body(FileOutputSchema())
def file(file, hapic_data):
    infos = {
        'name': file,
        'size': os.path.getsize(file),
    }

    if hapic_data.query.get('verbose'):
        infos['is_link'] = os.path.islink(file)

    return infos


# doc view
hapic.set_context(FlaskContext(app))
hapic.add_documentation_view('/api/doc')

# run server
app.run(debug=True)
