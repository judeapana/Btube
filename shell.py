from wsgi import app

# push app context
shell = app.app_context()
shell.push()
