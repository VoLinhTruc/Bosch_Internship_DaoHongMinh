#include "arith/arith.h"

const char* arith_status_string(arith_status status) {
    switch (status) {
        case ARITH_OK:
            return "ok";
        case ARITH_ERR_DIV_BY_ZERO:
            return "division by zero";
        case ARITH_ERR_NEGATIVE_INPUT:
            return "negative input";
        case ARITH_ERR_SIZE_MISMATCH:
            return "size mismatch";
        case ARITH_ERR_NULL_POINTER:
            return "null pointer";
        case ARITH_ERR_OVERFLOW:
            return "overflow";
        case ARITH_ERR_INVALID_ARGUMENT:
            return "invalid argument";
        default:
            return "unknown error";
    }
}
