#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "arith/arith.h"

#include <stdlib.h>

static PyObject* arith_exception = NULL;

static PyObject* status_to_exception(arith_status status) {
    const char* message = arith_status_string(status);

    switch (status) {
        case ARITH_ERR_DIV_BY_ZERO:
            PyErr_SetString(PyExc_ZeroDivisionError, message);
            break;
        case ARITH_ERR_OVERFLOW:
            PyErr_SetString(PyExc_OverflowError, message);
            break;
        case ARITH_ERR_INVALID_ARGUMENT:
        case ARITH_ERR_SIZE_MISMATCH:
        case ARITH_ERR_NEGATIVE_INPUT:
            PyErr_SetString(PyExc_ValueError, message);
            break;
        case ARITH_ERR_NULL_POINTER:
            PyErr_SetString(PyExc_RuntimeError, message);
            break;
        default:
            PyErr_SetString(arith_exception != NULL ? arith_exception : PyExc_RuntimeError, message);
            break;
    }

    return NULL;
}

static int parse_double_sequence(PyObject* obj, double** out_values, Py_ssize_t* out_count) {
    PyObject* seq = NULL;
    Py_ssize_t count;
    Py_ssize_t i;
    double* values = NULL;

    seq = PySequence_Fast(obj, "expected a sequence of numbers");
    if (seq == NULL) {
        return 0;
    }

    count = PySequence_Fast_GET_SIZE(seq);
    values = (double*)malloc((size_t)count * sizeof(double));
    if (values == NULL && count > 0) {
        Py_DECREF(seq);
        PyErr_NoMemory();
        return 0;
    }

    for (i = 0; i < count; ++i) {
        PyObject* item = PySequence_Fast_GET_ITEM(seq, i);
        double value = PyFloat_AsDouble(item);
        if (PyErr_Occurred()) {
            free(values);
            Py_DECREF(seq);
            return 0;
        }
        values[i] = value;
    }

    Py_DECREF(seq);
    *out_values = values;
    *out_count = count;
    return 1;
}

static PyObject* build_list_from_array(const double* values, Py_ssize_t count) {
    PyObject* list = PyList_New(count);
    Py_ssize_t i;

    if (list == NULL) {
        return NULL;
    }

    for (i = 0; i < count; ++i) {
        PyObject* value = PyFloat_FromDouble(values[i]);
        if (value == NULL) {
            Py_DECREF(list);
            return NULL;
        }
        PyList_SET_ITEM(list, i, value);
    }

    return list;
}

static PyObject* py_add(PyObject* self, PyObject* args) {
    double a, b, out;
    arith_status status;
    (void)self;

    if (!PyArg_ParseTuple(args, "dd", &a, &b)) {
        return NULL;
    }

    status = arith_add(a, b, &out);
    if (status != ARITH_OK) {
        return status_to_exception(status);
    }

    return PyFloat_FromDouble(out);
}

static PyObject* py_subtract(PyObject* self, PyObject* args) {
    double a, b, out;
    arith_status status;
    (void)self;

    if (!PyArg_ParseTuple(args, "dd", &a, &b)) {
        return NULL;
    }

    status = arith_subtract(a, b, &out);
    if (status != ARITH_OK) {
        return status_to_exception(status);
    }

    return PyFloat_FromDouble(out);
}

static PyObject* py_multiply(PyObject* self, PyObject* args) {
    double a, b, out;
    arith_status status;
    (void)self;

    if (!PyArg_ParseTuple(args, "dd", &a, &b)) {
        return NULL;
    }

    status = arith_multiply(a, b, &out);
    if (status != ARITH_OK) {
        return status_to_exception(status);
    }

    return PyFloat_FromDouble(out);
}

static PyObject* py_divide(PyObject* self, PyObject* args) {
    double a, b, out;
    arith_status status;
    (void)self;

    if (!PyArg_ParseTuple(args, "dd", &a, &b)) {
        return NULL;
    }

    status = arith_divide(a, b, &out);
    if (status != ARITH_OK) {
        return status_to_exception(status);
    }

    return PyFloat_FromDouble(out);
}


static PyObject* py_dot(PyObject* self, PyObject* args) {
    PyObject* left_obj;
    PyObject* right_obj;
    double* left = NULL;
    double* right = NULL;
    Py_ssize_t left_count = 0;
    Py_ssize_t right_count = 0;
    double out;
    arith_status status;
    (void)self;

    if (!PyArg_ParseTuple(args, "OO", &left_obj, &right_obj)) {
        return NULL;
    }

    if (!parse_double_sequence(left_obj, &left, &left_count)) {
        return NULL;
    }
    if (!parse_double_sequence(right_obj, &right, &right_count)) {
        free(left);
        return NULL;
    }

    if (left_count != right_count) {
        free(left);
        free(right);
        return status_to_exception(ARITH_ERR_SIZE_MISMATCH);
    }

    status = arith_dot(left, right, (size_t)left_count, &out);
    free(left);
    free(right);
    if (status != ARITH_OK) {
        return status_to_exception(status);
    }

    return PyFloat_FromDouble(out);
}

static PyObject* py_vector_add(PyObject* self, PyObject* args) {
    PyObject* left_obj;
    PyObject* right_obj;
    double* left = NULL;
    double* right = NULL;
    double* out = NULL;
    Py_ssize_t left_count = 0;
    Py_ssize_t right_count = 0;
    PyObject* list = NULL;
    arith_status status;
    (void)self;

    if (!PyArg_ParseTuple(args, "OO", &left_obj, &right_obj)) {
        return NULL;
    }

    if (!parse_double_sequence(left_obj, &left, &left_count)) {
        return NULL;
    }
    if (!parse_double_sequence(right_obj, &right, &right_count)) {
        free(left);
        return NULL;
    }

    if (left_count != right_count) {
        free(left);
        free(right);
        return status_to_exception(ARITH_ERR_SIZE_MISMATCH);
    }

    out = (double*)malloc((size_t)left_count * sizeof(double));
    if (out == NULL && left_count > 0) {
        free(left);
        free(right);
        return PyErr_NoMemory();
    }

    status = arith_vector_add(left, right, (size_t)left_count, out);
    free(left);
    free(right);
    if (status != ARITH_OK) {
        free(out);
        return status_to_exception(status);
    }

    list = build_list_from_array(out, left_count);
    free(out);
    return list;
}


static PyMethodDef simplearith_methods[] = {
    {"add", py_add, METH_VARARGS, "Add two numbers."},
    {"subtract", py_subtract, METH_VARARGS, "Subtract two numbers."},
    {"multiply", py_multiply, METH_VARARGS, "Multiply two numbers."},
    {"divide", py_divide, METH_VARARGS, "Divide two numbers."},
    {"dot", py_dot, METH_VARARGS, "Dot product of two numeric sequences."},
    {"vector_add", py_vector_add, METH_VARARGS, "Elementwise vector addition."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef simplearith_module = {
    PyModuleDef_HEAD_INIT,
    "simplearith",
    "Arithmetic library implemented in C and built with CMake.",
    -1,
    simplearith_methods
};

PyMODINIT_FUNC PyInit_simplearith(void) {
    PyObject* module = PyModule_Create(&simplearith_module);
    if (module == NULL) {
        return NULL;
    }

    arith_exception = PyErr_NewException("simplearith.Error", NULL, NULL);
    if (arith_exception == NULL) {
        Py_DECREF(module);
        return NULL;
    }

    if (PyModule_AddObject(module, "Error", arith_exception) < 0) {
        Py_DECREF(arith_exception);
        Py_DECREF(module);
        return NULL;
    }

    return module;
}

static void main(){
    printf("able to build");
    return 0;
}