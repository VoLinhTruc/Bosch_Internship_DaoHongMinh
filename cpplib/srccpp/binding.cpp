#include <pybind11/pybind11.h>
#include "math.hpp"

namespace py = pybind11;

PYBIND11_MODULE(addsub, m) {
    m.doc() = "add and subtract module";

    m.def("add", &add, "Add two integers");
    m.def("subtract", &subtract, "Subtract two integers");
}