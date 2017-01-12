from sys import version_info


def check_python_version():
    """
    Check the python version to ensure it is correct. PonyGE uses Python 3.

    :return: Nothing
    """

    if version_info.major < 3 and version_info.minor < 5:
        print("\nError: Python version not supported. Must use Python >= 3.5")

        quit()
