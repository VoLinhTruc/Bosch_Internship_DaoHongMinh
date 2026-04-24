#include "AES128.hpp"

int GenerateAES_Key(uint8_t *sharedSecretKey, int len_input, uint8_t *AES_Key)
{
    int AES_Key_len = 16;
    uint8_t hashedKey[SHA256_DIGEST_LENGTH];
    SHA256(sharedSecretKey, len_input, hashedKey);
    memcpy(AES_Key, hashedKey, AES_Key_len);
    return AES_Key_len;
}

int AES128_CBCEncryption(uint8_t *AES_PlainText, int AES_PlainText_len,
                         uint8_t *AES_CipherText,
                         uint8_t *AES_IV,
                         uint8_t *AES_EncryptKey)
{
    if (!AES_PlainText || !AES_EncryptKey || !AES_IV || !AES_CipherText || AES_PlainText_len <= 0)
    {
        return -2;
    }

    EVP_CIPHER_CTX *ctx;
    int len;
    int ciphertext_len;

    /* Create and initialise the context */
    if (!(ctx = EVP_CIPHER_CTX_new()))
    {
        return -1;
    }

    /* Initialize encryption operation with AES-128 CBC mode */
    if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, NULL, NULL))
    {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }

    /* Disable padding */
    EVP_CIPHER_CTX_set_padding(ctx, 0);

    /* Initialise key and IV */
    if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, AES_EncryptKey, AES_IV))
    {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }

    // Provide the message to be encrypted and obtain the encrypted output
    if (1 != EVP_EncryptUpdate(ctx, AES_CipherText, &len, AES_PlainText, AES_PlainText_len))
    {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    ciphertext_len = len;

    // Finalize the encryption. Further ciphertext bytes may be written
    if (1 != EVP_EncryptFinal_ex(ctx, AES_CipherText + len, &len))
    {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    ciphertext_len += len;

    // Clean up
    EVP_CIPHER_CTX_free(ctx);

    // Return the number of bytes encrypted
    return ciphertext_len;
}

int AES128_CBCDecryption(uint8_t *AES_CipherText, int AES_CipherText_len,
                         uint8_t *AES_PlainText,
                         uint8_t *AES_IV,
                         uint8_t *AES_DecryptKey)
{
    if (!AES_CipherText || !AES_DecryptKey || !AES_IV || !AES_PlainText || AES_CipherText_len <= 0)
    {
        return -2;
    }

    EVP_CIPHER_CTX *ctx;
    int len;
    int plaintext_len;

    /* Create and initialise the context */
    if (!(ctx = EVP_CIPHER_CTX_new()))
    {
        return -1;
    }

    /* Initialize decryption operation with AES-128 CBC mode */
    if (1 != EVP_DecryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, NULL, NULL))
    {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }

    /* Disable padding */
    EVP_CIPHER_CTX_set_padding(ctx, 0);

    /* Initialise key and IV */
    if (1 != EVP_DecryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, AES_DecryptKey, AES_IV))
    {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }

    // Provide the message to be decrypted and obtain the decrypted output
    if (1 != EVP_DecryptUpdate(ctx, AES_PlainText, &len, AES_CipherText, AES_CipherText_len))
    {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    plaintext_len = len;

    // Finalize the decryption. Further plaintext bytes may be written
    if (1 != EVP_DecryptFinal_ex(ctx, AES_PlainText + len, &len))
    {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }
    plaintext_len += len;

    // Clean up
    EVP_CIPHER_CTX_free(ctx);

    // Return the number of bytes decrypted
    return plaintext_len;
}
