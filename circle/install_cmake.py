
"""
Usage::

    import install_cmake
    install_cmake.install()

"""

import os
import subprocess
import sys

from subprocess import CalledProcessError, check_output

DEFAULT_CMAKE_VERSION = "3.5.0"


def _log(*args):
    script_name = os.path.basename(__file__)
    print("[circle:%s] " % script_name + " ".join(args))
    sys.stdout.flush()


def install(cmake_version=DEFAULT_CMAKE_VERSION):
    """Download and install CMake into ``/usr/local``."""

    if "CIRCLE_STAGE" in os.environ:
        _log("add-on not supoorted on CircleCI 2.0")
        return

    cmake_directory = "/usr/local"

    cmake_exe = os.path.join(cmake_directory, 'bin/cmake')

    if os.path.exists(cmake_exe):
        output = check_output([cmake_exe, '--version']).decode("utf-8")
        if output.strip() == cmake_version:
            _log("Skipping download: Found %s (v%s)" % (
                cmake_exe, cmake_version))
            return

    _log("Looking for cmake", cmake_version, "in PATH")
    try:
        output = check_output(
            "cmake --version", shell=True).decode("utf-8")
        current_cmake_version = output.splitlines()[0]
        if cmake_version in current_cmake_version:
            _log("  ->", "found %s:" % current_cmake_version,
                 "skipping download: version matches expected one")
            return
        else:
            _log("  ->", "found %s:" % current_cmake_version,
                 "not the expected version")
    except (OSError, CalledProcessError):
        _log("  ->", "not found")
        pass

    name = "cmake-{}-Linux-x86_64".format(cmake_version)
    cmake_package = "{}.tar.gz".format(name)

    _log("Downloading", cmake_package)

    download_dir = os.environ["HOME"] + "/downloads"
    downloaded_package = os.path.join(download_dir, cmake_package)

    if not os.path.exists(downloaded_package):

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        cmake_version_major = cmake_version.split(".")[0]
        cmake_version_minor = cmake_version.split(".")[1]

        check_output([
            "wget", "--no-check-certificate", "--progress=dot",
            "https://cmake.org/files/v{}.{}/{}".format(cmake_version_major, cmake_version_minor, cmake_package),
            "-O", downloaded_package
        ], stderr=subprocess.STDOUT)
        _log("  ->", "done")
    else:
        _log("  ->", "skipping download: found", downloaded_package)

    _log("Extracting", downloaded_package)
    check_output(["tar", "xzf", downloaded_package])
    _log("  ->", "done")

    _log("Installing", name, "into", cmake_directory)
    check_output([
        "sudo", "rsync", "-avz", name + "/", cmake_directory
    ])
    _log("  ->", "done")


if __name__ == '__main__':
    install(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CMAKE_VERSION)
