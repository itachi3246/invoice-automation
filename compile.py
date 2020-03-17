from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
ext_modules = [
    Extension("document",  ["document.py"]),
    Extension("compile",  ["compile.py"]),
    Extension("generic_response",  ["generic_response.py"]),
    Extension("get_table",  ["get_table.py"]),
    Extension("Test_unitcase",  ["Test_unitcase.py"]),
    Extension("app",  ["app.py"]),
    Extension("Lines_ocr",  ["Lines_ocr.py"]),
    Extension("extract_fromxml",  ["extract_fromxml.py"]),
    Extension("line_algorithm.__init__",  ["line_algorithm/__init__.py"]),
    Extension("line_algorithm.document",  ["line_algorithm/document.py"]),
    Extension("line_algorithm.utils",  ["line_algorithm/utils.py"])

#   ... all your modules that need be compiled ...
]
setup(
    name = 'My Program Name',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)
