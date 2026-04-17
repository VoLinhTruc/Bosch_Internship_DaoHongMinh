#include "arith/arith.h"

arith_status arith_vector_add(const double* a, const double* b, size_t count, double* out) {
    size_t i;

    if (a == NULL || b == NULL || out == NULL) {
        return ARITH_ERR_NULL_POINTER;
    }

    for (i = 0; i < count; ++i) {
        out[i] = a[i] + b[i];
    }

    return ARITH_OK;
}

arith_status arith_vector_subtract(const double* a, const double* b, size_t count, double* out) {
    size_t i;

    if (a == NULL || b == NULL || out == NULL) {
        return ARITH_ERR_NULL_POINTER;
    }

    for (i = 0; i < count; ++i) {
        out[i] = a[i] - b[i];
    }

    return ARITH_OK;
}

arith_status arith_dot(const double* a, const double* b, size_t count, double* out) {
    size_t i;
    double result = 0.0;

    if (a == NULL || b == NULL || out == NULL) {
        return ARITH_ERR_NULL_POINTER;
    }

    for (i = 0; i < count; ++i) {
        result += a[i] * b[i];
    }

    *out = result;
    return ARITH_OK;
}
