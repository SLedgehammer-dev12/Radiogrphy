import os
from pythonforandroid.recipe import PythonRecipe
from pythonforandroid.logger import info


class ReportlabRecipe(PythonRecipe):
    version = '4.4.1'
    url = 'https://files.pythonhosted.org/packages/7b/d8/c3366bf10a5a5fcc3467eefa9504f6aa24fcda5817b5b147eabd37a385e1/reportlab-{version}.tar.gz'
    depends = ['setuptools']
    call_hostpython_via_targetpython = False

    def get_recipe_env(self, arch=None):
        env = super().get_recipe_env(arch)
        env['NO_RL_ACCEL'] = '1'
        return env


recipe = ReportlabRecipe()
