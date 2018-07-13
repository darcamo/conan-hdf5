from conans import ConanFile, CMake, tools
import os
import shutil


class Hdf5Conan(ConanFile):
    name = "HDF5"
    version = "1.10.1"
    license = "BSD-style Open Source or Comercial"
    url = "https://github.com/darcamo/conan-recipes"
    author = "Darlan Cavalcante Moreira (darcamo@gmail.com)"
    description = "HDF5 is a data model, library, and file format for storing and managing data."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"
    requires = "zlib/1.2.11@conan/stable"

    def source(self):
        # https://bitbucket.hdfgroup.org/scm/hdffv/hdf5.git
        # Tag: hdf5-1_10_2
        git = tools.Git(folder="sources")
        git.clone("https://bitbucket.hdfgroup.org/scm/hdffv/hdf5.git",
                  "hdf5-{0}".format(self.version.replace(".", "_")))

        tools.replace_in_file("sources/CMakeLists.txt", "PROJECT (HDF5 C CXX)",
                              '''PROJECT(HDF5 C CXX)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

    def configure(self):
        # We are not building the C++ binding thus libcxx does not matter
        del self.settings.compiler.libcxx

        self.options["zlib"].shared = self.options.shared

    def build(self):
        cmake = CMake(self)

        # Note that static lib will always be generated according to HDF5
        # CMakeLists.txt file. The shared option here only controls if the
        # shared library will also be generated or not.
        if self.options["shared"]:
            cmake.definitions["BUILD_SHARED_LIBS"] = "ON"
        else:
            cmake.definitions["BUILD_SHARED_LIBS"] = "OFF"

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
