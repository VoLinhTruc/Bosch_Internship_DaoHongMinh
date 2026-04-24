cmake_minimum_required(VERSION 3.16)

project(key_exchange_standalone
    VERSION 1.0.0
    LANGUAGES CXX
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

find_package(OpenSSL REQUIRED)
find_package(Python3 COMPONENTS Interpreter REQUIRED)

function(set_flat_output_dirs target)
    set_target_properties(${target} PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
        LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
        ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}
    )

    if(CMAKE_CONFIGURATION_TYPES)
        foreach(config ${CMAKE_CONFIGURATION_TYPES})
            string(TOUPPER ${config} config_upper)
            set_target_properties(${target} PROPERTIES
                RUNTIME_OUTPUT_DIRECTORY_${config_upper} ${CMAKE_BINARY_DIR}
                LIBRARY_OUTPUT_DIRECTORY_${config_upper} ${CMAKE_BINARY_DIR}
                ARCHIVE_OUTPUT_DIRECTORY_${config_upper} ${CMAKE_BINARY_DIR}
            )
        endforeach()
    endif()
endfunction()

add_library(keyexchange_logger STATIC
    third_party/logger/logger.cpp
)
set_target_properties(keyexchange_logger PROPERTIES
    POSITION_INDEPENDENT_CODE ON
)
set_flat_output_dirs(keyexchange_logger)
target_include_directories(keyexchange_logger
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/third_party/logger
)

add_library(keyexchange_crypto STATIC
    third_party/cryptography/AES128.cpp
    third_party/cryptography/cryptography.cpp
)
set_target_properties(keyexchange_crypto PROPERTIES
    POSITION_INDEPENDENT_CODE ON
)
set_flat_output_dirs(keyexchange_crypto)
target_include_directories(keyexchange_crypto
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/third_party/cryptography
        ${CMAKE_CURRENT_SOURCE_DIR}/third_party/logger
)
target_link_libraries(keyexchange_crypto
    PUBLIC
        keyexchange_logger
        OpenSSL::Crypto
)

add_library(key_exchange_library SHARED
    src/KeyExchange_Service.cpp
    src/KeyExchange_Interface.cpp
)
set_target_properties(key_exchange_library PROPERTIES
    OUTPUT_NAME key_exchange_library
    POSITION_INDEPENDENT_CODE ON
)
set_flat_output_dirs(key_exchange_library)
target_include_directories(key_exchange_library
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
        ${CMAKE_CURRENT_SOURCE_DIR}/third_party/uds
)
target_link_libraries(key_exchange_library
    PRIVATE
        keyexchange_crypto
)

install(TARGETS key_exchange_library
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
    ARCHIVE DESTINATION lib
)
install(FILES include/KeyExchange_Interface.h
    DESTINATION include/key_exchange
)

enable_testing()
add_test(
    NAME mock_keyexchange
    COMMAND
        ${Python3_EXECUTABLE}
        ${CMAKE_CURRENT_SOURCE_DIR}/test/mock_keyexchange_test.py
        --lib $<TARGET_FILE:key_exchange_library>
)

add_test(
    NAME mock_keyexchange_response_pending
    COMMAND
        ${Python3_EXECUTABLE}
        ${CMAKE_CURRENT_SOURCE_DIR}/test/mock_keyexchange_test.py
        --lib $<TARGET_FILE:key_exchange_library>
        --inject-response-pending
)