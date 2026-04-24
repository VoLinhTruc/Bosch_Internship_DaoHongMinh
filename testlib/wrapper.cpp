#include "wrapper.h"

Wrapper::Wrapper(){
}

Wrapper::~Wrapper(){
}

void Wrapper::useOperator(){
  m_operator.dummyFunction1();
  m_operator.dummyFunction2();
}

void Wrapper::useManager(){
  m_manager.dummyFunction1();
  m_manager.dummyFunction2();
}
