import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager

#创建一个类继承Flask类
class Application(Flask):
    def __init__(self,import_name,template_folder = None,root_path=None):
        super(Application, self).__init__(import_name,template_folder=template_folder,root_path=root_path)
        """
        if "ops_config" in os.environ:
           config_url = "../config/"+os.environ['ops_config']+"_settings.py"
            print(config_url)
            self.config.from_pyfile( "../config/%s_settings.py"%os.environ['ops_config'])
            """
        self.config.from_pyfile('../config/base_settings.py')
        db.init_app(self)


db = SQLAlchemy()
app = Application(__name__,template_folder=os.getcwd()+"/templates/",root_path=os.getcwd())
manager = Manager(app)

"""
函数模板
"""
from common.UrlManager import UrlManager
app.add_template_global(UrlManager.buildStaticUrl,'buildStaticUrl')
app.add_template_global(UrlManager.buildUrl,'buildUrl')
