from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("jora")
except PackageNotFoundError:
    __version__ = "unknown"
