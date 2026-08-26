from pythonforandroid.recipe import PythonRecipe


class KivyMDRecipe(PythonRecipe):
    version = '1.1.1'
    url = 'https://github.com/kivymd/KivyMD/archive/refs/tags/{version}.tar.gz'
    depends = ['python3', 'kivy', 'setuptools', 'pillow', 'requests']
    call_hostpython_via_targetpython = False


recipe = KivyMDRecipe()
