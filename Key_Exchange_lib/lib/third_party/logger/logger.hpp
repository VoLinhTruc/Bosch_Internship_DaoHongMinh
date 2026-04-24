#ifndef LOGGER_HPP
#define LOGGER_HPP

/**
 * @file logger.hpp
 * @brief Logger Header File
 *
 * This file defines the Logger for handling send communication with the System

 * @SWMajorVersion              1
 * @SWMinorVersion              0
 * @SWPatchVersion              0
 */

// Common Handler version definitions
#define LOGGER_SW_MAJOR_VERSION             1U
#define LOGGER_SW_MINOR_VERSION             0U
#define LOGGER_SW_PATCH_VERSION             0U

#include <string>
#include <mutex>
#include <iostream>

/**
 * @brief A simple thread-safe logger.
 *
 * This Logger class provides functionality to output log messages with different
 * severity levels. It is designed to be thread-safe by using a mutex to protect
 * the output stream.
 */
class Logger {
public:
    /**
     * @brief Logging levels for categorizing log messages.
     */
    enum class Level {
        DEBUG,   /**< Debug-level messages for detailed troubleshooting. */
        INFO,    /**< Informational messages that highlight the progress of the application. */
        WARNING, /**< Warnings about potential issues or unexpected events. */
        ERROR    /**< Error messages indicating a failure in the application. */
    };

    /**
     * 
     * @brief Logs a message at a given logging level.
     *
     * This static method outputs the log message to the standard output (console),
     * prefixed with the corresponding logging level. Thread-safety is ensured via
     * a mutex.
     *
     * @param level The severity level of the log message.
     * @param message The message text to log.
     */
    static void log(Level level, const std::string &message);

private:
    /**
     * @brief Converts a logging level to its string representation.
     *
     * This helper function is used internally to format log messages.
     *
     * @param level The logging level to convert.
     * @return A string representing the logging level.
     */
    [[nodiscard]] static std::string levelToString(Level level) noexcept;

    /**
     * @brief Provides access to a static mutex for thread-safe logging.
     *
     * @return A reference to a static std::mutex used to synchronize log output.
     */
    [[nodiscard]] static std::mutex& getMutex() noexcept ;
};

#endif // LOGGER_HPP
