#ifndef UDS_TYPEDEF_H_
#define UDS_TYPEDEF_H_

#include <stdint.h>

namespace uds
{
// -------------------------
// Service Identifier (SID)
// -------------------------
typedef enum {
    SID_DIAGNOSTIC_SESSION_CONTROL = 0x10,
    SID_ECU_RESET                  = 0x11,
    SID_CLEAR_DIAGNOSTIC_INFO      = 0x14,
    SID_READ_DTC_INFO             = 0x19,
    SID_READ_DATA_BY_IDENTIFIER    = 0x22,
    SID_READ_MEMORY_BY_ADDRESS     = 0x23,
    SID_READ_SCALING_DATA_BY_ID    = 0x24,
    SID_SECURITY_ACCESS            = 0x27,
    SID_COMMUNICATION_CONTROL      = 0x28,
    SID_READ_DATA_BY_PERIODIC_ID   = 0x2A,
    SID_DYNAMICALLY_DEFINE_DATA_ID = 0x2C,
    SID_WRITE_DATA_BY_IDENTIFIER   = 0x2E,
    SID_INPUT_OUTPUT_CONTROL       = 0x2F,
    SID_ROUTINE_CONTROL            = 0x31,
    SID_REQUEST_DOWNLOAD           = 0x34,
    SID_REQUEST_UPLOAD             = 0x35,
    SID_TRANSFER_DATA              = 0x36,
    SID_REQUEST_TRANSFER_EXIT      = 0x37,
    SID_WRITE_MEMORY_BY_ADDRESS    = 0x3D,
    SID_TESTER_PRESENT             = 0x3E,
    SID_NEGATIVE_RESPONSE          = 0x7F
} uds_sid_t;

// -------------------------
// Negative Response Code (NRC)
// -------------------------
typedef enum {
    NRC_GENERAL_REJECT                    = 0x10,
    NRC_SERVICE_NOT_SUPPORTED             = 0x11,
    NRC_SUBFUNCTION_NOT_SUPPORTED         = 0x12,
    NRC_INCORRECT_MESSAGE_LEN             = 0x13,
    NRC_RESPONSE_TOO_LONG                 = 0x14,
    NRC_BUSY_REPEAT_REQUEST               = 0x21,
    NRC_CONDITIONS_NOT_CORRECT            = 0x22,
    NRC_REQUEST_SEQUENCE_ERROR            = 0x24,
    NRC_NO_RESPONSE_FROM_SUBNET_COMPONENT = 0x25,
    NRC_FAILURE_PREVENTS_EXECUTION        = 0x26,
    NRC_REQUEST_OUT_OF_RANGE              = 0x31,
    NRC_SECURITY_ACCESS_DENIED            = 0x33,
    NRC_INVALID_KEY                       = 0x35,
    NRC_EXCEED_NUMBER_OF_ATTEMPTS         = 0x36,
    NRC_REQUIRED_TIME_DELAY_NOT_EXPIRED   = 0x37,
    NRC_UPLOAD_DOWNLOAD_NOT_ACCEPTED      = 0x70,
    NRC_TRANSFER_DATA_SUSPENDED           = 0x71,
    NRC_GENERAL_PROGRAMMING_FAILURE       = 0x72,
    NRC_WRONG_BLOCK_SEQUENCE_COUNTER      = 0x73,
    NRC_REQUEST_CORRECTLY_RX_RSP_PENDING  = 0x78,
    NRC_SUBFUNCTION_NOT_SUPPORTED_ACTIVE  = 0x7E,
    NRC_SERVICE_NOT_SUPPORTED_ACTIVE      = 0x7F,
    NRC_RESPONSE_PENDING                  = 0x78
} uds_nrc_t;

// -------------------------
// Session Types for SID 0x10
// -------------------------
typedef enum {
    SESSION_TYPE_DEFAULT     = 0x01,
    SESSION_TYPE_PROGRAMMING = 0x02,
    SESSION_TYPE_EXTENDED    = 0x03
} uds_session_type_t;

// -------------------------
// Reset Types for SID 0x11
// -------------------------
typedef enum {
    RESET_TYPE_HARD         = 0x01,
    RESET_TYPE_KEY_OFF_ON   = 0x02,
    RESET_TYPE_SOFT         = 0x03,
    RESET_TYPE_ENABLE_RAPID_POWER_SHUTDOWN = 0x04,
    RESET_TYPE_DISABLE_RAPID_POWER_SHUTDOWN = 0x05
} uds_reset_type_t;

// -------------------------
// Security Access Sub-functions for SID 0x27
// -------------------------
typedef enum {
    SECURITY_ACCESS_REQUEST_SEED = 0x01,
    SECURITY_ACCESS_SEND_KEY     = 0x02,
    SECURITY_ACCESS_REQUEST_SEED_L2 = 0x03,
    SECURITY_ACCESS_SEND_KEY_L2     = 0x04
} uds_security_access_subfunction_t;

// -------------------------
// Common Data Identifiers (DID)
// -------------------------
typedef enum {
    DID_BOOT_SOFTWARE_ID                = 0xF180,
    DID_APPLICATION_SOFTWARE_ID         = 0xF181,
    DID_APPLICATION_DATA_ID            = 0xF182,
    DID_BOOT_SOFTWARE_FINGERPRINT      = 0xF183,
    DID_APPLICATION_SOFTWARE_FINGERPRINT = 0xF184,
    DID_APPLICATION_DATA_FINGERPRINT   = 0xF185,
    DID_VIN                           = 0xF190,
    DID_VEHICLE_ID_ECU_SERIAL_NUMBER  = 0xF18C,
    DID_SYSTEM_SUPPLIER_ID            = 0xF18A,
    DID_ECU_MANUFACTURING_DATE        = 0xF18B,
    DID_ECU_SERIAL_NUMBER            = 0xF18C,
    DID_SUPPORTED_FUNCTIONAL_UNITS    = 0xF18D,
    DID_VEHICLE_MANUFACTURER_KIT_ASS  = 0xF18E,
    DID_VEHICLE_MANUFACTURER_ECU_SW_NUMBER = 0xF188,
    DID_VEHICLE_MANUFACTURER_ECU_SW_VERSION = 0xF189,
    DID_SYSTEM_SUPPLIER_ECU_SW_NUMBER = 0xF194,
    DID_SYSTEM_SUPPLIER_ECU_SW_VERSION = 0xF195,
    DID_EXHAUST_REGULATION_OR_TYPE    = 0xF196,
    DID_SYSTEM_NAME_OR_ENGINE_TYPE    = 0xF197,
    DID_REPAIR_SHOP_CODE_OR_TESTER_ID = 0xF198,
    DID_PROGRAMMING_DATE              = 0xF199,
    DID_CALIBRATION_REPAIR_SHOP_CODE  = 0xF19A,
    DID_CALIBRATION_DATE              = 0xF19B,
    DID_CALIBRATION_EQUIPMENT_SW_NUMBER = 0xF19C,
    DID_INSTALLATION_DATE             = 0xF19D,
    DID_ODX_FILE                     = 0xF19E,
    DID_ENTITY_DATA                  = 0xF19F
} uds_data_identifier_t;

// -------------------------
// UDS Constants
// -------------------------
// UDS_POSITIVE_RESPONSE_OFFSET moved to UdsService class as static constexpr
#define UDS_MAX_REQUEST_LENGTH        4095
#define UDS_MAX_RESPONSE_LENGTH       4095
#define UDS_MIN_REQUEST_LENGTH        1
#define UDS_DEFAULT_TIMEOUT_MS        5000
#define UDS_SECURITY_ACCESS_TIMEOUT_MS 10000

} // namespace uds

#endif // UDS_TYPEDEF_H_
