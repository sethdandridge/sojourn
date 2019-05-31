# Sojourn
Platform for sharing your vacation home with friends and family. [View the site in action!](https://sojourn.house)

## Installation (Ubuntu)
- sudo apt-get install postgresql postgresql-contrib
- createdb book_app
- python3 -m venv env
- source env/bin/activate
- pip install -r requirements.txt
- export FLASK_APP=app
- export FLASK_ENV=development
- flask init-db
- Then create an env.sh file with the following lines:
  - export FLASK_SECRET_KEY=(random and secure string)
  - export FLASK_SECURITY_PASSWORD_SALT=(random and secure string)
  - export AWS_SES_ACCESS_KEY_ID=(AWS access key for sending emails)
  - export AWS_SES_SECRET_ACCESS_KEY=(AWS secret key for sending emails)
  - export FLASK_ENV=development
- source env.sh
- flask run

## Architectual Overview
run.sh is the startup file, it's a small shell script that tells Flask (which is the python web framework) to run the "app" package as a Flask application. This starts a web server using the logic in the app package (i.e. the app folder).

The app folder contains a `__init__.py` file that is the main starting point for the web serving logic. It contains the `create_app()` function which builds the Flask application object. `create_app` ingests configuration information (like the location of the database for example) so the config settings can be passed around and used by other parts of the application. It also sets up logging and registers the various blueprints.

Blueprints are a way to organize the application. Blueprints are packages which are like mini-application objects. All auth (login, logout, registration) is in one blueprint. Admin controls (for property owners) is its own blueprint. Most of the meaty parts of the logic (booking, reservations) is in the dashboard blueprint. You can look at the logic for each blueprint in their respective package folders. 

Each blueprint contains routes, functions that are associated with URL locations via *Flask magic* so you can, for example, define a function like

```python
@blueprint.route("/hello")
def hello_world():
  return "Hello world!"
```

This registers the function `hello_world()` to the sojourn.com/hello path so that when /hello is requested, the hello_world function runs and "Hello world!" is delivered over the Internet to the browser that made the request.

How this works internally is a mind-blowingly clever bit of design (the guy who created Flask—Armin Ronacher—has an extremely keen sense for developer ergonomics): The line `@blueprint.route("/hello")` line is a function decorator. It passes the hello_world function defined below it up to the blueprint.route method (along with the route string "/hello") and registers hello_world to the top-level application object so when a request comes in that matches the route "/hello" Flask knows which function to run to generate the response.

Anyway, the last bit of important information is how the actual HTML is generated. Flask uses a templating engine called Jinja2. Instead of writing HTML you make a .jinja2 file and then instead of returning "hello world" at the end of a route you return a rendered template like:

```python
return render_template('homepage.jinja2', user="Seth")
```

And then the Jinja2 file is just a regular HTML file with placeholders for templating. Example template:

```
<center><h1>{{ user }}</h1></center> 
```

Would yield

```
<center><h1>Seth</h1></center>
```

when it's called by the route function because the user passed to the homepage.jinja2 template is "Seth"

Emails are done the same way, except instead of returning the rendered template to the browser, it's sent to Amazon's email service.

And that's basically all... there's some additional complexity relating to access control (how to ensure certain users are only able to do certain things) and how the object that accesses the database is passed around the application, but I'll leave that as an exercise for the reader.
