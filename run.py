#!/usr/bin/env python
'''wrapper for whole app package'''
__author__ = "Denys Tarnavskyi"
__copyright__ = "Copyright 2018, RPD site project"
__license__ = "MIT"
__version__ = "1.0"
__email__ = "marzique@gmail.com"
__status__ = "Development"

from rpd_site import app


if __name__ == '__main__':
    app.run(debug=True)
