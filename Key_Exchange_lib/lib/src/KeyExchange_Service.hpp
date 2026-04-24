#ifndef KEY_EXCHANGE_SERVICE_HPP
#define KEY_EXCHANGE_SERVICE_HPP

#include <chrono>
#include <cstdint>
#include <string>
#include <vector>

#include "KeyExchange_Interface.h"

namespace service {

enum class PythonRunState : int {
    IDLE = KEYEXCHANGE_RUN_IDLE,
    RUNNING = KEYEXCHANGE_RUN_RUNNING,
    COMPLETE = KEYEXCHANGE_RUN_COMPLETE,
    FAILED = KEYEXCHANGE_RUN_FAILED
};

enum class PythonStep : int {
    IDLE = KEYEXCHANGE_STEP_IDLE,
    DEFAULT_SESSION = KEYEXCHANGE_STEP_DEFAULT_SESSION,
    EXTENDED_SESSION = KEYEXCHANGE_STEP_EXTENDED_SESSION,
    REQUEST_SEED = KEYEXCHANGE_STEP_REQUEST_SEED,
    SECURITY_UNLOCK = KEYEXCHANGE_STEP_SECURITY_UNLOCK,
    PUBLIC_KEY_EXCHANGE = KEYEXCHANGE_STEP_PUBLIC_KEY_EXCHANGE,
    DELIVER_ENCRYPTED_KEY = KEYEXCHANGE_STEP_DELIVER_ENCRYPTED_KEY,
    COMPLETE = KEYEXCHANGE_STEP_COMPLETE,
    FAILED = KEYEXCHANGE_STEP_FAILED
};

class KeyExchangeService {
public:
    explicit KeyExchangeService(int anchorIdx);

    int SetAnchorIdx(int anchorIdx);
    int SetFactoryPrivateKey(const uint8_t* data, int len);
    int SetSecocKey(const uint8_t* data, int len);
    int SetIV(const uint8_t* data, int len);
    int SetNoResponseLimit(int maxNoResponsePolls);

    int Start();
    int Step(SendCanFunc sendCb, RecvCanFunc recvCb);
    void Reset();

    int GetState() const;
    int GetStep() const;
    bool IsRunning() const;
    bool IsComplete() const;
    bool IsFailed() const;

    int CopyEncryptedKey(uint8_t* outBuffer, int maxLen) const;
    int CopyLastRequest(uint8_t* outBuffer, int maxLen) const;
    int CopyLastResponse(uint8_t* outBuffer, int maxLen) const;
    const char* GetLastError() const;

private:
    bool RequireConfiguredMaterial();
    void SetFailed(const std::string& error);
    int SendRequest(SendCanFunc sendCb, const std::vector<unsigned char>& request);
    int PollResponse(RecvCanFunc recvCb, std::vector<unsigned char>& response);
    int PollExpectedResponse(RecvCanFunc recvCb, uint8_t requestSid, std::vector<unsigned char>& response);
    static bool IsPositiveResponseFor(uint8_t requestSid, const std::vector<unsigned char>& response);
    bool IsResponsePendingFor(uint8_t requestSid, const std::vector<unsigned char>& response) const;
    bool IsNegativeResponseFor(uint8_t requestSid, uint8_t nrc, const std::vector<unsigned char>& response) const;
    void ResetNoResponseCounter();
    int HandleNoResponse();
    int EnsureCanCallbacks(SendCanFunc sendCb, RecvCanFunc recvCb) const;

    int mAnchorIdx;
    std::vector<unsigned char> mFactoryPrivateKey;
    std::vector<unsigned char> mSecocKey;
    std::vector<unsigned char> mIv;

    PythonRunState mState;
    PythonStep mStep;
    bool mWaitingResponse;
    int mNoResponsePolls;
    int mMaxNoResponsePolls;
    std::chrono::steady_clock::time_point mSecurityRetryNotBefore;

    std::vector<unsigned char> mSeed;
    std::vector<unsigned char> mSignature;
    std::vector<unsigned char> mMasterPublicKey;
    std::vector<unsigned char> mMasterPrivateKey;
    std::vector<unsigned char> mAnchorPublicKey;
    std::vector<unsigned char> mSharedSecret;
    std::vector<unsigned char> mTruncatedSharedKey;
    std::vector<unsigned char> mEncryptedKey;

    std::vector<unsigned char> mLastRequest;
    std::vector<unsigned char> mLastResponse;
    std::string mLastError;

    std::vector<unsigned char> mDefaultSessionReq;
    std::vector<unsigned char> mExtendedSessionReq;
    std::vector<unsigned char> mReqSeedReq;
    std::vector<unsigned char> mUnlockReqPrefix;
    std::vector<unsigned char> mPublicKeyReqPrefix;
    std::vector<unsigned char> mEncryptedKeyReqPrefix;
};

} // namespace service

#endif // KEY_EXCHANGE_SERVICE_HPP
