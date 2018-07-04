# 01

## 01.0

We will setup a web server who:

* Generate it's http api documentation
* Check input data
* Check output data
* Manage errors

## 01.1

Setup your development environment: Follow README instructions, chapter "Install".
To follow next instructions, create a file named `workshop.py` and write into it.
To execute your work, execute `python workshop.py command`. Useful documentation:

* Marshmallow: https://marshmallow.readthedocs.io/en/latest/
* Flask: http://flask.pocoo.org/docs/1.0/

## 01.2

Write your 1st api endpoint:

``` python
import flask
import vlc

app = Flask('vlc control')


@app.route('/bird')
def play_bird_avi():
    player = vlc.MediaPlayer('bird.avi')
    player.play()
    return '', 204

app.run(debug=True)
```

Run this script: a flask web server start.
You are now able to start vlc video making an http request:

    http :5000/bird


## 01.3

Now, we want to generate a documentation of this http api.

## 01.3.1

Thirst, add `@hapic.with_api_doc()` decorator to your view. This decorator
must always be the first decorator.
 
## 01.3.2

To describe the http response of this endpoint (an 204 empty response),
prepare an empty marshmallow Schema

``` python
import marshmallow


class EmptyResponseSchema(marshmallow.Schema):
    pass
```

And us it with `@hapic.output_body(EmptyResponseSchema())` decorator.

## 01.4

Solution:

``` python
import flask
import vlc
import hapic
import marshmallow
from hapic.ext.flask import FlaskContext

app = Flask('vlc control')


class EmptyResponseSchema(marshmallow.Schema):
    pass


@hapic.with_api_doc()
@app.route('/bird')
@hapic.output_body(EmptyResponseSchema(), default_http_code=204)
def play_bird_avi():
    player = vlc.MediaPlayer('bird.avi')
    player.play()
    return '', 204


# This is also needed to add a Swagger ui view of api doc
context = FlaskContext(app)
hapic.set_context(context)
hapic.add_documentation_view('/api/doc')

app.run(debug=True)
```

Start your web server. You are now able to visualise api documentation at
`http://127.0.0.1:5000/api/doc`.
