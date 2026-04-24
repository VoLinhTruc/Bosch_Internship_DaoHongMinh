#include "KeyExchange_Service.hpp"

#include <algorithm>
#include <chrono>
#include <cstring>

#include "AES128.hpp"
#include "cryptography.hpp"
#include "uds_typedef.hpp"

namespace crypto = cryptography::keyexchange;

namespace service {

namespace {

constexpr int kSeedOffset = 2;
constexpr int kAnchorPublicKeyOffset = 4;
constexpr int kExpectedSignatureSize = 64;
constexpr int kExpectedPublicKeySize = 64;
constexpr int kExpectedKeyPairSize = 96;
constexpr int kDefaultNoResponsePolls = 200;
constexpr auto kSecurityRetryDelay = std::chrono::milliseconds(1000);

enum class UdsSid : uint8_t {
    DiagnosticSessionControl = 0x10,
    SecurityAccess = 0x27,
    RoutineControl = 0x31
};

enum class DiagnosticSessionType : uint8_t {
    DefaultSession = 0x01,
    ExtendedSession = 0x03
};

enum class SecurityAccessSubFunction : uint8_t {
    RequestSeedInCar1 = 0x65,
    SendKeyInCar1 = 0x66
};

enum class RoutineControlType : uint8_t {
    StartRoutine = 0x01
};

enum class KeyExchangeRoutineId : uint16_t {
    PublicKeyExchange = 0xFB40,
    DeliverEncryptedKey = 0xFB41
};

constexpr uint8_t ToByte(UdsSid value) {
    return static_cast<uint8_t>(value);
}

constexpr uint8_t ToByte(DiagnosticSessionType value) {
    return static_cast<uint8_t>(value);
}

constexpr uint8_t ToByte(SecurityAccessSubFunction value) {
    return static_cast<uint8_t>(value);
}

constexpr uint8_t ToByte(RoutineControlType value) {
    return static_cast<uint8_t>(value);
}

std::vector<unsigned char> DiagnosticSessionRequest(DiagnosticSessionType sessionType) {
    return {ToByte(UdsSid::DiagnosticSessionControl), ToByte(sessionType)};
}

std::vector<unsigned char> SecurityAccessRequest(SecurityAccessSubFunction subFunction) {
    return {ToByte(UdsSid::SecurityAccess), ToByte(subFunction)};
}

std::vector<unsigned char> RoutineControlRequestPrefix(KeyExchangeRoutineId routineId) {
    const auto id = static_cast<uint16_t>(routineId);
    return {
        ToByte(UdsSid::RoutineControl),
        ToByte(RoutineControlType::StartRoutine),
        static_cast<unsigned char>((id >> 8U) & 0xFFU),
        static_cast<unsigned char>(id & 0xFFU)};
}

std::vector<unsigned char> CopyVectorFromRaw(const uint8_t* data, int len) {
    if (data == nullptr || len <= 0) {
        return {};
    }

    std::vector<unsigned char> out(static_cast<size_t>(len));
    std::memcpy(out.data(), data, static_cast<size_t>(len));
    return out;
}

int CopyOut(const std::vector<unsigned char>& src, uint8_t* dst, int maxLen) {
    if (maxLen < 0) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    if (dst == nullptr) {
        return static_cast<int>(src.size());
    }
    const int toCopy = std::min(maxLen, static_cast<int>(src.size()));
    if (toCopy > 0) {
        std::memcpy(dst, src.data(), static_cast<size_t>(toCopy));
    }
    return toCopy;
}

} // namespace

KeyExchangeService::KeyExchangeService(int anchorIdx) :
        mAnchorIdx(anchorIdx),
        mState(PythonRunState::IDLE),
        mStep(PythonStep::IDLE),
        mWaitingResponse(false),
        mNoResponsePolls(0),
        mSecurityRetryNotBefore(),
        mMaxNoResponsePolls(kDefaultNoResponsePolls),
        mDefaultSessionReq(DiagnosticSessionRequest(DiagnosticSessionType::DefaultSession)),
        mExtendedSessionReq(DiagnosticSessionRequest(DiagnosticSessionType::ExtendedSession)),
        mReqSeedReq(SecurityAccessRequest(SecurityAccessSubFunction::RequestSeedInCar1)),
        mUnlockReqPrefix(SecurityAccessRequest(SecurityAccessSubFunction::SendKeyInCar1)),
        mPublicKeyReqPrefix(RoutineControlRequestPrefix(KeyExchangeRoutineId::PublicKeyExchange)),
        mEncryptedKeyReqPrefix(RoutineControlRequestPrefix(KeyExchangeRoutineId::DeliverEncryptedKey)) {}

int KeyExchangeService::SetAnchorIdx(int anchorIdx) {
    if (anchorIdx < 0) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    mAnchorIdx = anchorIdx;
    return KEYEXCHANGE_TICK_OK;
}

int KeyExchangeService::SetFactoryPrivateKey(const uint8_t* data, int len) {
    auto value = CopyVectorFromRaw(data, len);
    if (value.empty()) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    mFactoryPrivateKey = std::move(value);
    return KEYEXCHANGE_TICK_OK;
}

int KeyExchangeService::SetSecocKey(const uint8_t* data, int len) {
    auto value = CopyVectorFromRaw(data, len);
    if (value.empty()) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    mSecocKey = std::move(value);
    return KEYEXCHANGE_TICK_OK;
}

int KeyExchangeService::SetIV(const uint8_t* data, int len) {
    auto value = CopyVectorFromRaw(data, len);
    if (value.empty()) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    mIv = std::move(value);
    return KEYEXCHANGE_TICK_OK;
}

int KeyExchangeService::SetNoResponseLimit(int maxNoResponsePolls) {
    if (maxNoResponsePolls < 0) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    mMaxNoResponsePolls = maxNoResponsePolls;
    return KEYEXCHANGE_TICK_OK;
}

int KeyExchangeService::Start() {
    if (!RequireConfiguredMaterial()) {
        return KEYEXCHANGE_TICK_NOT_CONFIGURED;
    }
    mState = PythonRunState::RUNNING;
    mStep = PythonStep::DEFAULT_SESSION;
    mWaitingResponse = false;
    mNoResponsePolls = 0;
    mSecurityRetryNotBefore = {};
    mSeed.clear();
    mSignature.clear();
    mMasterPublicKey.clear();
    mMasterPrivateKey.clear();
    mAnchorPublicKey.clear();
    mSharedSecret.clear();
    mTruncatedSharedKey.clear();
    mEncryptedKey.clear();
    mLastRequest.clear();
    mLastResponse.clear();
    mLastError.clear();
    return KEYEXCHANGE_TICK_OK;
}

int KeyExchangeService::Step(SendCanFunc sendCb, RecvCanFunc recvCb) {
    const int callbackCheck = EnsureCanCallbacks(sendCb, recvCb);
    if (callbackCheck != KEYEXCHANGE_TICK_OK) {
        return callbackCheck;
    }

    if (mState == PythonRunState::COMPLETE) {
        return KEYEXCHANGE_TICK_COMPLETE;
    }
    if (mState == PythonRunState::FAILED) {
        return KEYEXCHANGE_TICK_FAILED;
    }
    if (mState != PythonRunState::RUNNING) {
        return KEYEXCHANGE_TICK_NOT_CONFIGURED;
    }

    std::vector<unsigned char> response;
    switch (mStep) {
        case PythonStep::DEFAULT_SESSION: {
            if (!mWaitingResponse) {
                const int ret = SendRequest(sendCb, mDefaultSessionReq);
                if (ret != KEYEXCHANGE_TICK_OK) {
                    return ret;
                }
                mWaitingResponse = true;
                return KEYEXCHANGE_TICK_PENDING;
            }

            const int recvRet = PollExpectedResponse(recvCb, mDefaultSessionReq[0], response);
            if (recvRet == KEYEXCHANGE_TICK_PENDING) {
                return HandleNoResponse();
            }
            if (recvRet != KEYEXCHANGE_TICK_OK) {
                return recvRet;
            }
            if (!IsPositiveResponseFor(mDefaultSessionReq[0], response)) {
                SetFailed("Unexpected response for default session");
                return KEYEXCHANGE_TICK_FAILED;
            }
            ResetNoResponseCounter();
            mWaitingResponse = false;
            mStep = PythonStep::EXTENDED_SESSION;
            return KEYEXCHANGE_TICK_OK;
        }
        case PythonStep::EXTENDED_SESSION: {
            if (!mWaitingResponse) {
                const int ret = SendRequest(sendCb, mExtendedSessionReq);
                if (ret != KEYEXCHANGE_TICK_OK) {
                    return ret;
                }
                mWaitingResponse = true;
                return KEYEXCHANGE_TICK_PENDING;
            }

            const int recvRet = PollExpectedResponse(recvCb, mExtendedSessionReq[0], response);
            if (recvRet == KEYEXCHANGE_TICK_PENDING) {
                return HandleNoResponse();
            }
            if (recvRet != KEYEXCHANGE_TICK_OK) {
                return recvRet;
            }
            if (!IsPositiveResponseFor(mExtendedSessionReq[0], response)) {
                SetFailed("Unexpected response for extended session");
                return KEYEXCHANGE_TICK_FAILED;
            }
            ResetNoResponseCounter();
            mWaitingResponse = false;
            mStep = PythonStep::REQUEST_SEED;
            return KEYEXCHANGE_TICK_OK;
        }
        case PythonStep::REQUEST_SEED: {
            if (!mWaitingResponse) {
                if (mSecurityRetryNotBefore != std::chrono::steady_clock::time_point{} &&
                    std::chrono::steady_clock::now() < mSecurityRetryNotBefore) {
                    return KEYEXCHANGE_TICK_PENDING;
                }

                const int ret = SendRequest(sendCb, mReqSeedReq);
                if (ret != KEYEXCHANGE_TICK_OK) {
                    return ret;
                }
                mWaitingResponse = true;
                return KEYEXCHANGE_TICK_PENDING;
            }

            const int recvRet = PollResponse(recvCb, response);
            if (recvRet == KEYEXCHANGE_TICK_PENDING) {
                return HandleNoResponse();
            }
            if (recvRet != KEYEXCHANGE_TICK_OK) {
                return recvRet;
            }
            if (IsResponsePendingFor(mReqSeedReq[0], response)) {
                return HandleNoResponse();
            }
            if (IsNegativeResponseFor(mReqSeedReq[0], uds::NRC_REQUIRED_TIME_DELAY_NOT_EXPIRED, response)) {
                mWaitingResponse = false;
                mSecurityRetryNotBefore = std::chrono::steady_clock::now() + kSecurityRetryDelay;
                ResetNoResponseCounter();
                return KEYEXCHANGE_TICK_PENDING;
            }
            if (!IsPositiveResponseFor(mReqSeedReq[0], response)) {
                SetFailed("Unexpected response for seed request");
                return KEYEXCHANGE_TICK_FAILED;
            }
            if (response.size() <= kSeedOffset) {
                SetFailed("Seed response payload too short");
                return KEYEXCHANGE_TICK_FAILED;
            }
            mSeed.assign(response.begin() + kSeedOffset, response.end());
            mSignature.clear();
            if (crypto::GenerateECDSASignature(mSeed, mFactoryPrivateKey, mSignature) != kExpectedSignatureSize) {
                SetFailed("Failed to generate ECDSA signature");
                return KEYEXCHANGE_TICK_FAILED;
            }
            ResetNoResponseCounter();
            mWaitingResponse = false;
            mSecurityRetryNotBefore = {};
            mStep = PythonStep::SECURITY_UNLOCK;
            return KEYEXCHANGE_TICK_OK;
        }
        case PythonStep::SECURITY_UNLOCK: {
            if (!mWaitingResponse) {
                if (mSecurityRetryNotBefore != std::chrono::steady_clock::time_point{} &&
                    std::chrono::steady_clock::now() < mSecurityRetryNotBefore) {
                    return KEYEXCHANGE_TICK_PENDING;
                }

                std::vector<unsigned char> unlockReq = mUnlockReqPrefix;
                unlockReq.insert(unlockReq.end(), mSignature.begin(), mSignature.end());
                const int ret = SendRequest(sendCb, unlockReq);
                if (ret != KEYEXCHANGE_TICK_OK) {
                    return ret;
                }
                mWaitingResponse = true;
                return KEYEXCHANGE_TICK_PENDING;
            }

            const int recvRet = PollResponse(recvCb, response);
            if (recvRet == KEYEXCHANGE_TICK_PENDING) {
                return HandleNoResponse();
            }
            if (recvRet != KEYEXCHANGE_TICK_OK) {
                return recvRet;
            }
            if (IsResponsePendingFor(mUnlockReqPrefix[0], response)) {
                return HandleNoResponse();
            }
            if (IsNegativeResponseFor(mUnlockReqPrefix[0], uds::NRC_REQUIRED_TIME_DELAY_NOT_EXPIRED, response)) {
                mWaitingResponse = false;
                mSecurityRetryNotBefore = std::chrono::steady_clock::now() + kSecurityRetryDelay;
                ResetNoResponseCounter();
                return KEYEXCHANGE_TICK_PENDING;
            }
            if (!IsPositiveResponseFor(mUnlockReqPrefix[0], response)) {
                SetFailed("Unexpected response for security unlock");
                return KEYEXCHANGE_TICK_FAILED;
            }
            std::vector<unsigned char> masterKeyPair;
            if (crypto::ECDHKeyPairsGen_1(masterKeyPair) != kExpectedKeyPairSize ||
                masterKeyPair.size() < static_cast<size_t>(kExpectedKeyPairSize)) {
                SetFailed("Failed to generate ECDH key pair");
                return KEYEXCHANGE_TICK_FAILED;
            }
            mMasterPublicKey.assign(masterKeyPair.begin(), masterKeyPair.begin() + 64);
            mMasterPrivateKey.assign(masterKeyPair.begin() + 64, masterKeyPair.begin() + 96);
            ResetNoResponseCounter();
            mWaitingResponse = false;
            mSecurityRetryNotBefore = {};
            mStep = PythonStep::PUBLIC_KEY_EXCHANGE;
            return KEYEXCHANGE_TICK_OK;
        }

        case PythonStep::PUBLIC_KEY_EXCHANGE: {
            if (!mWaitingResponse) {
                std::vector<unsigned char> pubReq = mPublicKeyReqPrefix;
                pubReq.insert(pubReq.end(), mMasterPublicKey.begin(), mMasterPublicKey.end());
                const int ret = SendRequest(sendCb, pubReq);
                if (ret != KEYEXCHANGE_TICK_OK) {
                    return ret;
                }
                mWaitingResponse = true;
                return KEYEXCHANGE_TICK_PENDING;
            }

            const int recvRet = PollResponse(recvCb, response);
            if (recvRet == KEYEXCHANGE_TICK_PENDING) {
                return HandleNoResponse();
            }
            if (recvRet != KEYEXCHANGE_TICK_OK) {
                return recvRet;
            }

            // Positive response: 0x71 0x01 0xFB 0x40 <64-byte anchor public key>
            if (IsPositiveResponseFor(mPublicKeyReqPrefix[0], response)) {
                if (response.size() < static_cast<size_t>(kAnchorPublicKeyOffset + kExpectedPublicKeySize)) {
                    SetFailed("Anchor public key response too short");
                    return KEYEXCHANGE_TICK_FAILED;
                }

                ResetNoResponseCounter();
                mAnchorPublicKey.clear();
                mAnchorPublicKey.assign(
                    response.begin() + kAnchorPublicKeyOffset,
                    response.begin() + kAnchorPublicKeyOffset + kExpectedPublicKeySize);

                mSharedSecret = crypto::calculateSharedKey(mAnchorPublicKey, mMasterPrivateKey);
                if (mSharedSecret.empty()) {
                    SetFailed("Failed to derive shared secret");
                    return KEYEXCHANGE_TICK_FAILED;
                }

                mTruncatedSharedKey = crypto::hashAndTruncate(mSharedSecret);
                if (mTruncatedSharedKey.size() != 16U) {
                    SetFailed("Failed to derive truncated shared key");
                    return KEYEXCHANGE_TICK_FAILED;
                }

                std::vector<unsigned char> encryptedBuffer(mSecocKey.size(), 0);
                int encLen = AES128_CBCEncryption(
                    mSecocKey.data(),
                    static_cast<int>(mSecocKey.size()),
                    encryptedBuffer.data(),
                    mIv.data(),
                    mTruncatedSharedKey.data());
                if (encLen < 0) {
                    SetFailed("AES128_CBCEncryption failed");
                    return KEYEXCHANGE_TICK_FAILED;
                }
                encryptedBuffer.resize(static_cast<size_t>(encLen));
                mEncryptedKey = encryptedBuffer;

                mWaitingResponse = false;
                mStep = PythonStep::DELIVER_ENCRYPTED_KEY;
                return KEYEXCHANGE_TICK_OK;
            }

            // NRC 0x78 is treated as pending here.
            if (response.size() >= 3 &&
                response[0] == 0x7F &&
                response[1] == mPublicKeyReqPrefix[0] &&
                response[2] == 0x78) {
                return KEYEXCHANGE_TICK_PENDING;
            }

            SetFailed("Unexpected response for public key exchange");
            return KEYEXCHANGE_TICK_FAILED;
        }
        case PythonStep::DELIVER_ENCRYPTED_KEY: {
            if (!mWaitingResponse) {
                std::vector<unsigned char> encryptedReq = mEncryptedKeyReqPrefix;
                encryptedReq.insert(encryptedReq.end(), mEncryptedKey.begin(), mEncryptedKey.end());
                const int ret = SendRequest(sendCb, encryptedReq);
                if (ret != KEYEXCHANGE_TICK_OK) {
                    return ret;
                }
                mWaitingResponse = true;
                return KEYEXCHANGE_TICK_PENDING;
            }

            const int recvRet = PollExpectedResponse(recvCb, mEncryptedKeyReqPrefix[0], response);
            if (recvRet == KEYEXCHANGE_TICK_PENDING) {
                return HandleNoResponse();
            }
            if (recvRet != KEYEXCHANGE_TICK_OK) {
                return recvRet;
            }
            if (!IsPositiveResponseFor(mEncryptedKeyReqPrefix[0], response)) {
                SetFailed("Unexpected response for encrypted key delivery");
                return KEYEXCHANGE_TICK_FAILED;
            }

            ResetNoResponseCounter();
            mWaitingResponse = false;
            mStep = PythonStep::COMPLETE;
            mState = PythonRunState::COMPLETE;
            return KEYEXCHANGE_TICK_COMPLETE;
        }
        case PythonStep::COMPLETE:
            return KEYEXCHANGE_TICK_COMPLETE;
        case PythonStep::FAILED:
            return KEYEXCHANGE_TICK_FAILED;
        case PythonStep::IDLE:
        default:
            return KEYEXCHANGE_TICK_NOT_CONFIGURED;
    }
}

void KeyExchangeService::Reset() {
    mState = PythonRunState::IDLE;
    mStep = PythonStep::IDLE;
    mWaitingResponse = false;
    mNoResponsePolls = 0;
    mSecurityRetryNotBefore = {};
    mSeed.clear();
    mSignature.clear();
    mMasterPublicKey.clear();
    mMasterPrivateKey.clear();
    mAnchorPublicKey.clear();
    mSharedSecret.clear();
    mTruncatedSharedKey.clear();
    mEncryptedKey.clear();
    mLastRequest.clear();
    mLastResponse.clear();
    mLastError.clear();
}

int KeyExchangeService::GetState() const {
    return static_cast<int>(mState);
}

int KeyExchangeService::GetStep() const {
    return static_cast<int>(mStep);
}

bool KeyExchangeService::IsRunning() const {
    return mState == PythonRunState::RUNNING;
}

bool KeyExchangeService::IsComplete() const {
    return mState == PythonRunState::COMPLETE;
}

bool KeyExchangeService::IsFailed() const {
    return mState == PythonRunState::FAILED;
}

int KeyExchangeService::CopyEncryptedKey(uint8_t* outBuffer, int maxLen) const {
    return CopyOut(mEncryptedKey, outBuffer, maxLen);
}

int KeyExchangeService::CopyLastRequest(uint8_t* outBuffer, int maxLen) const {
    return CopyOut(mLastRequest, outBuffer, maxLen);
}

int KeyExchangeService::CopyLastResponse(uint8_t* outBuffer, int maxLen) const {
    return CopyOut(mLastResponse, outBuffer, maxLen);
}

const char* KeyExchangeService::GetLastError() const {
    return mLastError.empty() ? nullptr : mLastError.c_str();
}

bool KeyExchangeService::RequireConfiguredMaterial() {
    if (mFactoryPrivateKey.empty()) {
        SetFailed("Factory private key is not configured");
        return false;
    }
    if (mSecocKey.empty()) {
        SetFailed("SecOC key is not configured");
        return false;
    }
    if (mIv.empty()) {
        SetFailed("IV is not configured");
        return false;
    }
    if (mSecocKey.size() % 16U != 0U) {
        SetFailed("SecOC key size must be a multiple of 16 bytes for AES-CBC without padding");
        return false;
    }
    if (mIv.size() != 16U) {
        SetFailed("IV size must be exactly 16 bytes");
        return false;
    }
    return true;
}

void KeyExchangeService::SetFailed(const std::string& error) {
    mLastError = error;
    mState = PythonRunState::FAILED;
    mStep = PythonStep::FAILED;
    mWaitingResponse = false;
}

int KeyExchangeService::SendRequest(SendCanFunc sendCb, const std::vector<unsigned char>& request) {
    if (request.empty()) {
        SetFailed("Attempted to send empty request");
        return KEYEXCHANGE_TICK_FAILED;
    }
    mLastRequest = request;
    const int sendRet = sendCb(request.data(), static_cast<int>(request.size()));
    if (sendRet < 0) {
        SetFailed("CAN send callback returned error");
        return KEYEXCHANGE_TICK_FAILED;
    }
    return KEYEXCHANGE_TICK_OK;
}

int KeyExchangeService::PollResponse(RecvCanFunc recvCb, std::vector<unsigned char>& response) {
    constexpr int kRxBufferSize = 1024;
    uint8_t buffer[kRxBufferSize] = {0};
    const int readLen = recvCb(buffer, kRxBufferSize);
    if (readLen < 0) {
        SetFailed("CAN receive callback returned error");
        return KEYEXCHANGE_TICK_FAILED;
    }
    if (readLen == 0) {
        return KEYEXCHANGE_TICK_PENDING;
    }
    response.assign(buffer, buffer + readLen);
    mLastResponse = response;
    return KEYEXCHANGE_TICK_OK;
}

int KeyExchangeService::PollExpectedResponse(
    RecvCanFunc recvCb,
    uint8_t requestSid,
    std::vector<unsigned char>& response) {
    const int recvRet = PollResponse(recvCb, response);
    if (recvRet != KEYEXCHANGE_TICK_OK) {
        return recvRet;
    }
    if (IsResponsePendingFor(requestSid, response)) {
        return KEYEXCHANGE_TICK_PENDING;
    }
    return KEYEXCHANGE_TICK_OK;
}

bool KeyExchangeService::IsPositiveResponseFor(
    uint8_t requestSid,
    const std::vector<unsigned char>& response) {
    return !response.empty() && response[0] == static_cast<uint8_t>(requestSid + 0x40U);
}

bool KeyExchangeService::IsResponsePendingFor(
    uint8_t requestSid,
    const std::vector<unsigned char>& response) const {
    return IsNegativeResponseFor(requestSid, uds::NRC_RESPONSE_PENDING, response);
}

bool KeyExchangeService::IsNegativeResponseFor(
    uint8_t requestSid,
    uint8_t nrc,
    const std::vector<unsigned char>& response) const {
    return response.size() >= 3U &&
           response[0] == uds::SID_NEGATIVE_RESPONSE &&
           response[1] == requestSid &&
           response[2] == nrc;
}

void KeyExchangeService::ResetNoResponseCounter() {
    mNoResponsePolls = 0;
}

int KeyExchangeService::HandleNoResponse() {
    ++mNoResponsePolls;
    if (mMaxNoResponsePolls > 0 && mNoResponsePolls > mMaxNoResponsePolls) {
        SetFailed("Exceeded no-response polling limit");
        return KEYEXCHANGE_TICK_FAILED;
    }
    return KEYEXCHANGE_TICK_PENDING;
}

int KeyExchangeService::EnsureCanCallbacks(SendCanFunc sendCb, RecvCanFunc recvCb) const {
    if (sendCb == nullptr || recvCb == nullptr) {
        return KEYEXCHANGE_TICK_CAN_CALLBACK_MISSING;
    }
    return KEYEXCHANGE_TICK_OK;
}

} // namespace service
