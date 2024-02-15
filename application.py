"""Configuration for AWS Elastic BeanStalk
    EB expects 'application.py' to expose a callable
    named 'application' in order to run the FastAPI app"""
from app.main import app

application = app