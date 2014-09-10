cmake_minimum_required(VERSION 2.8)

set(CMAKE_INCLUDE_CURRENT_DIR ON)

add_definitions(
    -Werror
    -Wall
)

include(FindPkgConfig)

pkg_search_module(ZMQ REQUIRED libzmq)

if (ZMQ_FOUND)
    include_directories(${ZMQ_INCLUDE_DIRS})
    link_directories(${ZMQ_LIBRARY_DIRS})
endif()


# server example
set(SERVER_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/server.c
)

set(SERVER "server")
add_executable(${SERVER}
    ${SERVER_SOURCES}
)

target_link_libraries(${SERVER}
    ${ZMQ_LIBRARIES}
)


# client example
set(CLIENT_SOURCES
    ${CMAKE_CURRENT_SOURCE_DIR}/client.c
)

set(CLIENT "client")
add_executable(${CLIENT}
    ${CLIENT_SOURCES}
)

target_link_libraries(${CLIENT}
    ${ZMQ_LIBRARIES}
)
