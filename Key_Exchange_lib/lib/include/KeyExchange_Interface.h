#ifndef KEY_EXCHANGE_INTERFACE_H
#define KEY_EXCHANGE_INTERFACE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32)
#define KEY_EXCHANGE_API __declspec(dllexport)
#else
#define KEY_EXCHANGE_API
#endif

typedef int (*SendCanFunc)(const uint8_t* data, int len);
typedef int (*RecvCanFunc)(uint8_t* buffer, int max_len);

typedef void* KeyExchangeHandle;

typedef enum KeyExchangeRunState {
    KEYEXCHANGE_RUN_IDLE = 0,
    KEYEXCHANGE_RUN_RUNNING = 1,
    KEYEXCHANGE_RUN_COMPLETE = 2,
    KEYEXCHANGE_RUN_FAILED = 3
} KeyExchangeRunState;

typedef enum KeyExchangeStep {
    KEYEXCHANGE_STEP_IDLE = 0,
    KEYEXCHANGE_STEP_DEFAULT_SESSION = 1,
    KEYEXCHANGE_STEP_EXTENDED_SESSION = 2,
    KEYEXCHANGE_STEP_REQUEST_SEED = 3,
    KEYEXCHANGE_STEP_SECURITY_UNLOCK = 4,
    KEYEXCHANGE_STEP_PUBLIC_KEY_EXCHANGE = 5,
    KEYEXCHANGE_STEP_DELIVER_ENCRYPTED_KEY = 6,
    KEYEXCHANGE_STEP_COMPLETE = 7,
    KEYEXCHANGE_STEP_FAILED = 8
} KeyExchangeStep;

typedef enum KeyExchangeTickResult {
    KEYEXCHANGE_TICK_OK = 0,
    KEYEXCHANGE_TICK_PENDING = 1,
    KEYEXCHANGE_TICK_COMPLETE = 2,
    KEYEXCHANGE_TICK_FAILED = -1,
    KEYEXCHANGE_TICK_BAD_ARGUMENT = -2,
    KEYEXCHANGE_TICK_NOT_CONFIGURED = -3,
    KEYEXCHANGE_TICK_CAN_CALLBACK_MISSING = -4
} KeyExchangeTickResult;

KEY_EXCHANGE_API void RegisterCanCallbacks(SendCanFunc sendFunc, RecvCanFunc recvFunc);
KEY_EXCHANGE_API void ClearCanCallbacks(void);

KEY_EXCHANGE_API KeyExchangeHandle KeyExchange_Create(int anchor_idx);
KEY_EXCHANGE_API void KeyExchange_Destroy(KeyExchangeHandle handle);

KEY_EXCHANGE_API int KeyExchange_SetCanCallbacks(KeyExchangeHandle handle, SendCanFunc sendFunc, RecvCanFunc recvFunc);
KEY_EXCHANGE_API int KeyExchange_ClearCanCallbacks(KeyExchangeHandle handle);

KEY_EXCHANGE_API int KeyExchange_SetAnchorIdx(KeyExchangeHandle handle, int anchor_idx);
KEY_EXCHANGE_API int KeyExchange_SetFactoryPrivateKey(KeyExchangeHandle handle, const uint8_t* data, int len);
KEY_EXCHANGE_API int KeyExchange_SetSecocKey(KeyExchangeHandle handle, const uint8_t* data, int len);
KEY_EXCHANGE_API int KeyExchange_SetIV(KeyExchangeHandle handle, const uint8_t* data, int len);
KEY_EXCHANGE_API int KeyExchange_SetNoResponseLimit(KeyExchangeHandle handle, int max_no_response_polls);

KEY_EXCHANGE_API int KeyExchange_Start(KeyExchangeHandle handle);
KEY_EXCHANGE_API int KeyExchange_Step(KeyExchangeHandle handle);
KEY_EXCHANGE_API void KeyExchange_Reset(KeyExchangeHandle handle);

KEY_EXCHANGE_API int KeyExchange_GetState(KeyExchangeHandle handle);
KEY_EXCHANGE_API int KeyExchange_GetStep(KeyExchangeHandle handle);
KEY_EXCHANGE_API int KeyExchange_IsRunning(KeyExchangeHandle handle);
KEY_EXCHANGE_API int KeyExchange_IsComplete(KeyExchangeHandle handle);
KEY_EXCHANGE_API int KeyExchange_IsFailed(KeyExchangeHandle handle);

KEY_EXCHANGE_API int KeyExchange_GetEncryptedKey(KeyExchangeHandle handle, uint8_t* out_buffer, int max_len);
KEY_EXCHANGE_API int KeyExchange_GetLastRequest(KeyExchangeHandle handle, uint8_t* out_buffer, int max_len);
KEY_EXCHANGE_API int KeyExchange_GetLastResponse(KeyExchangeHandle handle, uint8_t* out_buffer, int max_len);
KEY_EXCHANGE_API const char* KeyExchange_GetLastError(KeyExchangeHandle handle);

#ifdef __cplusplus
}
#endif

#endif // KEY_EXCHANGE_INTERFACE_H
