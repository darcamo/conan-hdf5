# pylint: disable=C0111

import os
import shutil
from conans import ConanFile, CMake, tools


class Hdf5Conan(ConanFile):
    name = "HDF5"
    version = "1.12.0"
    license = "BSD-style Open Source or Comercial"
    url = "https://github.com/darcamo/conan-hdf5"
    author = "Darlan Cavalcante Moreira (darcamo@gmail.com)"
    description = ("HDF5 is a data model, library, and file format for "
                   "storing and managing data.")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": True}
    generators = "cmake"
    requires = "zlib/1.2.11"

    def source(self):
        git = tools.Git(folder="sources")
        tag_name = "hdf5-{0}".format(self.version.replace(".", "_"))
        git.clone("https://github.com/HDFGroup/hdf5.git",
                  tag_name)

        tools.replace_in_file("sources/CMakeLists.txt", "project (HDF5 C)",
                              '''project (HDF5 C)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def configure(self):
        # We are not building the C++ binding thus libcxx does not matter
        del self.settings.compiler.libcxx
        if self.options.shared:
            self.options["zlib"].shared = True
        else:
            self.options["zlib"].shared = False

    def build(self):
        cmake = CMake(self)

        cmake.definitions["HDF5_BUILD_EXAMPLES"] = "OFF"
        cmake.definitions["HDF5_BUILD_TOOLS"] = "ON"
        cmake.definitions["HDF5_BUILD_HL_LIB"] = "OFF"
        cmake.definitions["HDF5_BUILD_CPP_LIB"] = "OFF"
        cmake.definitions["HDF5_ENABLE_Z_LIB_SUPPORT"] = "ON"
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.package_folder
        os.mkdir("build")
        shutil.move("conanbuildinfo.cmake", "build/")
        cmake.configure(source_folder="sources", build_folder="build")
        cmake.build()
        cmake.install()

    def package_info(self):
        # The HDF5 library has different names depending if it is a release
        # of a debug build
        if self.settings.build_type == "Release":
            self.cpp_info.libs = ["hdf5"]
        else:
            self.cpp_info.libs = ["hdf5_debug"]

        # It seems we need to link with the dl library even when shared
        # libraries are not build (maybe because of dependencies)
        self.cpp_info.libs.append("dl")
