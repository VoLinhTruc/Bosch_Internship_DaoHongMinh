# CMake generated Testfile for 
# Source directory: C:/Users/DMA8HC/Desktop/key_exchange_test/Bosch_Internship_DaoHongMinh/Key_Exchange_lib/lib
# Build directory: C:/Users/DMA8HC/Desktop/key_exchange_test/Bosch_Internship_DaoHongMinh/Key_Exchange_lib/lib/build
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
add_test(mock_keyexchange "C:/msys64/ucrt64/bin/python3.14.exe" "C:/Users/DMA8HC/Desktop/key_exchange_test/Bosch_Internship_DaoHongMinh/Key_Exchange_lib/lib/test/mock_keyexchange_test.py" "--lib" "C:/Users/DMA8HC/Desktop/key_exchange_test/Bosch_Internship_DaoHongMinh/Key_Exchange_lib/lib/build/libkey_exchange_library.dll")
set_tests_properties(mock_keyexchange PROPERTIES  _BACKTRACE_TRIPLES "C:/Users/DMA8HC/Desktop/key_exchange_test/Bosch_Internship_DaoHongMinh/Key_Exchange_lib/lib/CMakeLists.txt;96;add_test;C:/Users/DMA8HC/Desktop/key_exchange_test/Bosch_Internship_DaoHongMinh/Key_Exchange_lib/lib/CMakeLists.txt;0;")
add_test(mock_keyexchange_response_pending "C:/msys64/ucrt64/bin/python3.14.exe" "C:/Users/DMA8HC/Desktop/key_exchange_test/Bosch_Internship_DaoHongMinh/Key_Exchange_lib/lib/test/mock_keyexchange_test.py" "--lib" "C:/Users/DMA8HC/Desktop/key_exchange_test/Bosch_Internship_DaoHongMinh/Key_Exchange_lib/lib/build/libkey_exchange_library.dll" "--inject-response-pending")
set_tests_properties(mock_keyexchange_response_pending PROPERTIES  _BACKTRACE_TRIPLES "C:/Users/DMA8HC/Desktop/key_exchange_test/Bosch_Internship_DaoHongMinh/Key_Exchange_lib/lib/CMakeLists.txt;104;add_test;C:/Users/DMA8HC/Desktop/key_exchange_test/Bosch_Internship_DaoHongMinh/Key_Exchange_lib/lib/CMakeLists.txt;0;")
