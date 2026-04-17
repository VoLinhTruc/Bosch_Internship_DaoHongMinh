#include "arith/arith.h"

arith_status arith_add(double a, double b, double* out) {
    if (out == NULL) {
        return ARITH_ERR_NULL_POINTER;
    }
    *out = a + b;
    return ARITH_OK;
}

arith_status arith_subtract(double a, double b, double* out) {
    if (out == NULL) {
        return ARITH_ERR_NULL_POINTER;
    }
    *out = a - b;
    return ARITH_OK;
}

arith_status arith_multiply(double a, double b, double* out) {
    if (out == NULL) {
        return ARITH_ERR_NULL_POINTER;
    }
    *out = a * b;
    return ARITH_OK;
}

arith_status arith_divide(double a, double b, double* out) {
    if (out == NULL) {
        return ARITH_ERR_NULL_POINTER;
    }
    if (b == 0.0) {
        return ARITH_ERR_DIV_BY_ZERO;
    }
    *out = a / b;
    return ARITH_OK;
}
