from robot.version import get_version

robot_version = get_version()

# Handle difference between Robot 3.x and 4.x
try:
    # noinspection PyUnresolvedReferences
    from robot.libdocpkg.htmlutils import DocToHtml
except ModuleNotFoundError:
    # noinspection PyUnresolvedReferences
    from robot.libdocpkg.htmlwriter import DocToHtml
