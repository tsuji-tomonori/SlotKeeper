"""srcとrepository直下に分かれたtoolsを同じパッケージとして公開する。"""

from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)
