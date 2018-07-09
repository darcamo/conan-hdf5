#include <iostream>
#include <hdf5.h>

int main(int argc, char* argv[]) {
    hid_t file_id = H5Fcreate("sample.h5", H5F_ACC_TRUNC, H5P_DEFAULT, H5P_DEFAULT);
    herr_t status = H5Fclose(file_id);

    std::cout << status << std::endl;

    return 0;
}
