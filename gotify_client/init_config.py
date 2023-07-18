import os
import configparser

config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
_ini_file_path = os.path.join(os.path.dirname(__file__), "config.ini")

with open(_ini_file_path, "r") as _config_file:
    _config_values = os.path.expandvars(_config_file.read())

config.read_string(_config_values)
