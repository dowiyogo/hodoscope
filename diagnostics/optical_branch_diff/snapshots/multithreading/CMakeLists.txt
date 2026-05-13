#----------------------------------------------------------------------------
# CMakeLists.txt — hodoscope-g4
#
# Build system para la simulación Geant4 del hodoscopio NA64-miniaturizado
# del grupo de muografía de la Universidad de La Serena.
#
# Probado con Geant4 11.x compilado con soporte ROOT y Qt.
#
# Uso típico:
#   mkdir build && cd build
#   cmake ..
#   make -j$(nproc)
#   ./hodoscope ../macros/run_mip_central.mac
#----------------------------------------------------------------------------
cmake_minimum_required(VERSION 3.16 FATAL_ERROR)
project(hodoscope_g4 LANGUAGES CXX)

#----------------------------------------------------------------------------
# Geant4: por defecto requerimos UI + visualización (Qt/OpenGL).
# Se puede desactivar pasando -DWITH_GEANT4_UIVIS=OFF.
#----------------------------------------------------------------------------
option(WITH_GEANT4_UIVIS "Build with Geant4 UI and Vis drivers" ON)
if(WITH_GEANT4_UIVIS)
  find_package(Geant4 REQUIRED ui_all vis_all)
else()
  find_package(Geant4 REQUIRED)
endif()

include(${Geant4_USE_FILE})

#----------------------------------------------------------------------------
# Estándar C++: Geant4 11 requiere al menos C++17.
#----------------------------------------------------------------------------
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

#----------------------------------------------------------------------------
# Fuentes y headers.
#----------------------------------------------------------------------------
include_directories(${PROJECT_SOURCE_DIR}/include)

file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)
file(GLOB headers ${PROJECT_SOURCE_DIR}/include/*.hh)

#----------------------------------------------------------------------------
# Ejecutable.
#----------------------------------------------------------------------------
add_executable(hodoscope hodoscope.cc ${sources} ${headers})
target_link_libraries(hodoscope ${Geant4_LIBRARIES})

#----------------------------------------------------------------------------
# Copiar macros al directorio de build para que ./hodoscope ../macros/X.mac
# funcione tanto desde build/ como con paths relativos.
#----------------------------------------------------------------------------
set(HODOSCOPE_MACROS
  init_vis.mac
  vis.mac
  run_mip_central.mac
  scan_xy.mac
)

foreach(_mac ${HODOSCOPE_MACROS})
  configure_file(
    ${PROJECT_SOURCE_DIR}/macros/${_mac}
    ${PROJECT_BINARY_DIR}/${_mac}
    COPYONLY
  )
endforeach()

#----------------------------------------------------------------------------
# Instalación opcional.
#----------------------------------------------------------------------------
install(TARGETS hodoscope DESTINATION bin)
