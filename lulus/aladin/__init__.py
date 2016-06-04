#!/usr/bin/env python
#coding=utf-8

import os
import logging
import logging.config

from flask import Flask

def create_app(config=None, modules=None, default_app_name='aladin'):
    
    app = Flask(default_app_name)
    
    # config
    if config is not None:
        app.config.from_pyfile(config)
    
    # register module
    if modules is not None:
        for module, url_prefix in modules:
            app.register_blueprint(module, url_prefix=url_prefix)

    # logging
    log_config = os.path.join(app.root_path, 'logging.ini')
    if os.path.isfile(log_config):
        logging.config.fileConfig(log_config)

    return app
