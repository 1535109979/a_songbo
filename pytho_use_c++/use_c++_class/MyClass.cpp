// MyClass.cpp
//#include "MyClass.h"
#include <iostream>

class MyClass {
public:
    void add();
};

void MyClass::add() {
    std::cout << "Hello, World!" << std::endl;
}


extern "C"{
MyClass obj;

void add(){
obj.add();
};

}



//  g++ -shared -o myclass.so -fPIC MyClass.cpp

