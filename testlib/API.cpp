// API.cpp
#include "wrapper.h"

extern "C" __declspec(dllexport) void* createWrapper(){
  return static_cast<void*>(new Wrapper());
}

extern "C" __declspec(dllexport) void useOperator(void* instance){
  static_cast<Wrapper*>(instance)->useOperator();
}

extern "C" __declspec(dllexport) void useManager(void* instance){
  static_cast<Wrapper*>(instance)->useManager();
}

extern "C" __declspec(dllexport) void deleteWrapper(void* instance){
  delete static_cast<Wrapper*>(instance);
}