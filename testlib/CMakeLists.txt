cmake_minimum_required(VERSION 3.10)

project(MyWrapper)

# Set the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add the source files to the project
set(SOURCE_FILES
    Operator.cpp
    Manager.cpp
    Wrapper.cpp
    API.cpp
)

# Add the header files to the project
set(HEADER_FILES
    Operator.h
    Manager.h
    Wrapper.h
)

# Create the shared library (DLL)
add_library(OperatorManagerWrapper SHARED ${HEADER_FILES} ${SOURCE_FILES})