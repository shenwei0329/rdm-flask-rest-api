# -*- coding: utf-8 -*-
"""
    2015.7.17 by shenwei @ChengDu

        利用FLASK做一个RESTful API接口

"""

from flask import Flask

def create_app():
    """
        创建flask应用

    :param config_name:
    :return:
    """
    app = Flask(__name__)

    from .api_1_0 import api as api_1_0_blueprint
    """
        注册一个入口
    """
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return app
