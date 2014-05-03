#!/data/virt/flask/bin/python
from wsgiref.handlers import CGIHandler
from reader import app

CGIHandler().run(app)
