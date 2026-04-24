#ifndef CRYPTOGRAPHY_CPP_H
#define CRYPTOGRAPHY_CPP_H

/*
 * @file    Cryptography.hpp
 * @brief   Cryptography functions for key generation, signing, and shared key calculation.
 * @details This module implements cryptographic functions 
 *

 * @SWMajorVersion              1
 * @SWMinorVersion              0
 * @SWPatchVersion              0
 */

// CRYPTO version definitions
#define CRYPTOGRAPHY_SW_MAJOR_VERSION             1U
#define CRYPTOGRAPHY_SW_MINOR_VERSION             0U
#define CRYPTOGRAPHY_SW_PATCH_VERSION             0U

#include <memory>
#include <string>
#include <map>
#include <vector>
#include <iostream>
#include <openssl/evp.h>
#include <openssl/ec.h>
#include <openssl/err.h>
#include <openssl/core_names.h>
#include <openssl/sha.h>
#include <openssl/pem.h>
#include <openssl/objects.h>
#include <openssl/ecdsa.h>
#include <openssl/bn.h>
#include <openssl/param_build.h>
#include <cstring>
#include <algorithm>
#include <iomanip>
#include <chrono>
#include <thread>
#include <AES128.hpp>
#include <logger.hpp>

#define CRYPTO_INPUT_ERROR -2
#define CRYPTO_FAILED -1
#define CRYPTO_SUCCESS 0
#define CRYPTO_MAX_KEY_COMPONENT_SIZE 32
#define CRYPTO_INIT_VALUE 0
#define CRYPTO_KEYPAIR_SIZE 96
#define CRYPTO_PUBLIC_KEY_SIZE 64
#define CRYPTO_PRIVATE_KEY_SIZE 32
#define PUBLIC_KEY_SIZE_WITH_PREFIX 65
#define TRUNCATED_HASH_SIZE 16
#define SHIFT_32_BYTES  32U
#define SHIFT_64_BYTES  64U
#define SHIFT_96_BYTES  96U

namespace cryptography {
namespace keyexchange {

/**
 * @brief Generates an ECDH key pair and stores the private key in a blob.
 *
 * Computes - privateKeyBlob [0:95] == pKx[0:31] || pKy[32:63] || sK[64:95]
 * PK    An ECC Public Key shall have a 256-bit (32-byte) x-component and a 256-bit (32-byte) y-component.
 * SK    An ECC Private Key shall have a 256-bit (32-byte) size.
 * Uses the domain parameters (p, a, b, G, n, h) defined by the NIST P-256 (secp256r1) curve.
 * The result is equivalent to ECDSA p256 Key derivation.
 * The 256-bit prime elliptic curve Diffie-Hellman key exchange algorithm.
 * Standard: SP800-56A
 *
 * @param[out] privateKeyBlob A vector to store the generated private key blob.
 * @return std::int32_t: 96 on success, -2 on input error, -1 on failure.
 */
[[nodiscard]] std::int32_t ECDHKeyPairsGen_1(std::vector<unsigned char> &privateKeyBlob);

/**
 * @brief Hashes the input using SHA-256 and truncates the result to 16 bytes.
 *
 * @param[in] input The input data to be hashed.
 * @return std::vector<unsigned char> A 16-byte truncated hash.
 */
[[nodiscard]] std::vector<unsigned char> hashAndTruncate(const std::vector<unsigned char> &input);

/**
 * @brief Generates an ECDSA signature from raw data and a private key blob.
 *
 * Generates signature (r[32] || s[32]) for the rawData by the input privateKeyBlob (X[32] || Y[32] || sK[32]), without padding.
 * Uses SHA256 for hashing and the appropriate ECDSA algorithm.
 * Standard: FIPS 186-2, X9.62 SECP256R1.
 * Output is in Big Endian byte order.
 *
 * @param[in] rawData The data to sign.
 * @param[in] privateKeyBlob The private key blob containing public and private keys.
 * @param[out] r_s A vector to store the generated signature (r and s components).
 * @return std::int32_t: 64 on success, -2 on input error, -1 on failure.
 */
[[nodiscard]] std::int32_t GenerateECDSASignature(const std::vector<unsigned char> &rawData, 
                           const std::vector<unsigned char> &privateKeyBlob, 
                           std::vector<unsigned char> &r_s);

/**
 * @brief Calculates the shared key using ECDH given a public key and a private key.
 *
 * Performs scalar multiplication over the secp256r1 curve.
 * Computes Q(x[0:31], y[0:31]) = k[0:31] * P(x[0:31], y[0:31]).
 * P is the public key from the other party.
 *
 * @param[in] publicKeyAnchor The public key of the other party.
 * @param[in] privateKey The private key of the local party.
 * @return std::vector<unsigned char> The computed shared key.
 */
[[nodiscard]] std::vector<unsigned char> calculateSharedKey(const std::vector<unsigned char> &publicKeyAnchor, 
                                               const std::vector<unsigned char> &privateKey);


} // namespace keyexchange
} // namespace cryptography

#endif  /*CRYPTOGRAPHY_CPP_H*/
