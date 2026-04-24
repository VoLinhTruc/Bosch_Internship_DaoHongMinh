#include "logger.hpp"

// Definition of the static function that returns the mutex.
std::mutex& Logger::getMutex() noexcept{
    static std::mutex mtx;
    return mtx;
}

// Definition of the helper function to convert logging level to string.
std::string Logger::levelToString(Level level) noexcept{
    switch (level) {
        case Level::DEBUG:   return "DEBUG";
        case Level::INFO:    return "INFO";
        case Level::WARNING: return "WARNING";
        case Level::ERROR:   return "ERROR";
        default:             return "UNKNOWN";
    }
}

// Definition of the log function.
void Logger::log(Level level, const std::string &message) {
    // Lock the mutex to prevent concurrent writes from different threads.
    std::lock_guard<std::mutex> lock(getMutex());
    std::cout << "[" << levelToString(level) << "] " << message << std::endl;
}
