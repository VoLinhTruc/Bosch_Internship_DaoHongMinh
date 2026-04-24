#include "KeyExchange_Interface.h"

#include <memory>
#include <mutex>

#include "KeyExchange_Service.hpp"

namespace {

std::mutex g_callbackMutex;
SendCanFunc g_sendCb = nullptr;
RecvCanFunc g_recvCb = nullptr;

struct KeyExchangeContext {
    explicit KeyExchangeContext(int anchorIdx) : core(anchorIdx) {}

    service::KeyExchangeService core;
    SendCanFunc sendCb = nullptr;
    RecvCanFunc recvCb = nullptr;
};

KeyExchangeContext* ToContext(KeyExchangeHandle handle) {
    return reinterpret_cast<KeyExchangeContext*>(handle);
}

service::KeyExchangeService* ToCore(KeyExchangeHandle handle) {
    auto* context = ToContext(handle);
    if (context == nullptr) {
        return nullptr;
    }
    return &context->core;
}

int CopyUsing(
    KeyExchangeHandle handle,
    uint8_t* outBuffer,
    int maxLen,
    int (service::KeyExchangeService::*fn)(uint8_t*, int) const) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    return (core->*fn)(outBuffer, maxLen);
}

} // namespace

extern "C" {

void RegisterCanCallbacks(SendCanFunc sendFunc, RecvCanFunc recvFunc) {
    std::lock_guard<std::mutex> lock(g_callbackMutex);
    g_sendCb = sendFunc;
    g_recvCb = recvFunc;
}

void ClearCanCallbacks(void) {
    std::lock_guard<std::mutex> lock(g_callbackMutex);
    g_sendCb = nullptr;
    g_recvCb = nullptr;
}

KeyExchangeHandle KeyExchange_Create(int anchor_idx) {
    auto context = std::make_unique<KeyExchangeContext>(anchor_idx);
    return reinterpret_cast<KeyExchangeHandle>(context.release());
}

void KeyExchange_Destroy(KeyExchangeHandle handle) {
    auto* context = ToContext(handle);
    delete context;
}

int KeyExchange_SetCanCallbacks(KeyExchangeHandle handle, SendCanFunc sendFunc, RecvCanFunc recvFunc) {
    auto* context = ToContext(handle);
    if (context == nullptr) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    context->sendCb = sendFunc;
    context->recvCb = recvFunc;
    return KEYEXCHANGE_TICK_OK;
}

int KeyExchange_ClearCanCallbacks(KeyExchangeHandle handle) {
    auto* context = ToContext(handle);
    if (context == nullptr) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    context->sendCb = nullptr;
    context->recvCb = nullptr;
    return KEYEXCHANGE_TICK_OK;
}

int KeyExchange_SetAnchorIdx(KeyExchangeHandle handle, int anchor_idx) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    return core->SetAnchorIdx(anchor_idx);
}

int KeyExchange_SetFactoryPrivateKey(KeyExchangeHandle handle, const uint8_t* data, int len) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    return core->SetFactoryPrivateKey(data, len);
}

int KeyExchange_SetSecocKey(KeyExchangeHandle handle, const uint8_t* data, int len) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    return core->SetSecocKey(data, len);
}

int KeyExchange_SetIV(KeyExchangeHandle handle, const uint8_t* data, int len) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    return core->SetIV(data, len);
}

int KeyExchange_SetNoResponseLimit(KeyExchangeHandle handle, int max_no_response_polls) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    return core->SetNoResponseLimit(max_no_response_polls);
}

int KeyExchange_Start(KeyExchangeHandle handle) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }
    return core->Start();
}

int KeyExchange_Step(KeyExchangeHandle handle) {
    auto* context = ToContext(handle);
    if (context == nullptr) {
        return KEYEXCHANGE_TICK_BAD_ARGUMENT;
    }

    SendCanFunc localSend = context->sendCb;
    RecvCanFunc localRecv = context->recvCb;
    if (localSend == nullptr || localRecv == nullptr) {
        std::lock_guard<std::mutex> lock(g_callbackMutex);
        if (localSend == nullptr) {
            localSend = g_sendCb;
        }
        if (localRecv == nullptr) {
            localRecv = g_recvCb;
        }
    }
    return context->core.Step(localSend, localRecv);
}

void KeyExchange_Reset(KeyExchangeHandle handle) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return;
    }
    core->Reset();
}

int KeyExchange_GetState(KeyExchangeHandle handle) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return KEYEXCHANGE_RUN_FAILED;
    }
    return core->GetState();
}

int KeyExchange_GetStep(KeyExchangeHandle handle) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return KEYEXCHANGE_STEP_FAILED;
    }
    return core->GetStep();
}

int KeyExchange_IsRunning(KeyExchangeHandle handle) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return 0;
    }
    return core->IsRunning() ? 1 : 0;
}

int KeyExchange_IsComplete(KeyExchangeHandle handle) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return 0;
    }
    return core->IsComplete() ? 1 : 0;
}

int KeyExchange_IsFailed(KeyExchangeHandle handle) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return 1;
    }
    return core->IsFailed() ? 1 : 0;
}

int KeyExchange_GetEncryptedKey(KeyExchangeHandle handle, uint8_t* out_buffer, int max_len) {
    return CopyUsing(handle, out_buffer, max_len, &service::KeyExchangeService::CopyEncryptedKey);
}

int KeyExchange_GetLastRequest(KeyExchangeHandle handle, uint8_t* out_buffer, int max_len) {
    return CopyUsing(handle, out_buffer, max_len, &service::KeyExchangeService::CopyLastRequest);
}

int KeyExchange_GetLastResponse(KeyExchangeHandle handle, uint8_t* out_buffer, int max_len) {
    return CopyUsing(handle, out_buffer, max_len, &service::KeyExchangeService::CopyLastResponse);
}

const char* KeyExchange_GetLastError(KeyExchangeHandle handle) {
    auto* core = ToCore(handle);
    if (core == nullptr) {
        return "Invalid handle";
    }
    return core->GetLastError();
}

} // extern "C"
