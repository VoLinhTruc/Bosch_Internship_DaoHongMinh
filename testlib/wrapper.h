// Wrapper.h
#pragma once

#include "manager.h"
#include "operator.h"

class Wrapper{
public:
  Wrapper();
  ~Wrapper();

  void useOperator();
  void useManager();  

private:
  Operator m_operator;
  Manager m_manager;
};