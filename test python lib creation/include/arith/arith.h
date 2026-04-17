#ifndef ARITH_ARITH_H
#define ARITH_ARITH_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    ARITH_OK = 0,
    ARITH_ERR_DIV_BY_ZERO = 1,
    ARITH_ERR_NEGATIVE_INPUT = 2,
    ARITH_ERR_SIZE_MISMATCH = 3,
    ARITH_ERR_NULL_POINTER = 4,
    ARITH_ERR_OVERFLOW = 5,
    ARITH_ERR_INVALID_ARGUMENT = 6
} arith_status;

const char* arith_status_string(arith_status status);

/* basic.c */
arith_status arith_add(double a, double b, double* out);
arith_status arith_subtract(double a, double b, double* out);
arith_status arith_multiply(double a, double b, double* out);
arith_status arith_divide(double a, double b, double* out);


/* vector.c */
arith_status arith_vector_add(const double* a, const double* b, size_t count, double* out);
arith_status arith_vector_subtract(const double* a, const double* b, size_t count, double* out);
arith_status arith_dot(const double* a, const double* b, size_t count, double* out);

#ifdef __cplusplus
}
#endif

#endif
