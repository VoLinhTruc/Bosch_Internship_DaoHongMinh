#ifndef AES128_HPP
#define AES128_HPP

#include <cstring>
#include <openssl/sha.h>
#include <openssl/evp.h>

/**
 * @brief Generate AES key
 * 
 * @param sharedSecretKey 
 * @param len_input 
 * @param AES_Key 
 * @return int 
 */
[[nodiscard]] int GenerateAES_Key(uint8_t *sharedSecretKey, int len_input, uint8_t *AES_Key);

/**
 * @brief Encrypts data using AES-128 in CBC mode.
 *
 * This function uses AES-128 CBC encryption to encrypt the provided data.
 * It receives the number of data bytes to be encrypted (AES_PlainText) using
 * the parameter `len_input`. The function returns the number of bytes
 * encrypted (AES_CipherText). A 16-byte IV block is always considered, and
 * CCC padding (0x80, 0x00, 0x00, ...) is not applied.
 *
 * @param[in] AES_PlainText Pointer to the data to encrypt.
 * @param[in] AES_PlainText_len Number of bytes to encrypt.
 * @param[out] AES_CipherText Pointer to the buffer for the encrypted data.
 * @param[in] AES_IV Pointer to the initialization vector (IV).
 * @param[in] AES_Key Pointer to the key for encryption (must be 16 bytes - 128 bits).
 * @param[in] AES_EncryptKey Pointer to the key for encryption (must be 16 bytes - 128 bits).
 * 
 * @return Return values:
 * - >= 0: Success (number of bytes returned).
 * - -2: Input error.
 * - -1: Failure.
 */
[[nodiscard]] int AES128_CBCEncryption(uint8_t *AES_PlainText, int AES_PlainText_len,
                         uint8_t *AES_CipherText,
                         uint8_t *AES_IV,
                         uint8_t *AES_EncryptKey);

/**
 * @brief Decrypts data using AES-128 in CBC mode.
 *
 * This function uses AES-128 CBC decryption to decrypt the provided data.
 * It receives the number of data bytes to be decrypted (AES_CipherText) using
 * the parameter `AES_CipherText_len`. The function returns the number of bytes
 * decrypted (AES_PlainText). A 16-byte IV block is always considered, and
 * CCC padding (0x80, 0x00, 0x00, ...) is not applied.
 *
 * @param[in] AES_CipherText Pointer to the data to decrypt.
 * @param[in] AES_CipherText_len Number of bytes to decrypt.
 * @param[out] AES_PlainText Pointer to the buffer for the decrypted data.
 * @param[in] AES_IV Pointer to the initialization vector (IV).
 * @param[in] AES_DecryptKey Pointer to the key for decryption (must be 16 bytes - 128 bits).
 *
 * @return Return values:
 * - >= 0: Success (number of bytes returned).
 * - -2: Input error.
 * - -1: Failure.
 */
[[nodiscard]] int AES128_CBCDecryption(uint8_t *AES_CipherText, int AES_CipherText_len,
                         uint8_t *AES_PlainText,
                         uint8_t *AES_IV,
                         uint8_t *AES_DecryptKey);
#endif // AES128_HPP_
