#include "pch.h"
#include <iostream>
#include <Windows.h>

using namespace std;

class Shape {
public:
	virtual void draw() {
		cout << "Малюється фігура" << endl;
	}
};

class Circle : public Shape {
public:
	void draw() override {
		cout << "Малюється коло" << endl;
	}
};

void task1() {
	Shape* p;
	Circle c;

	p = &c;
	p->draw();
}

class Animal {
public:
	virtual void sound() {
		cout << "Тварина видає звук" << endl;
	}
};

class Dog : public Animal {
public:
	void sound() override {
		cout << "Собака гавкає" << endl;
	}
};

class Cat : public Animal {
public:
	void sound() override {
		cout << "Кішка нявкає" << endl;
	}
};

void makeSound(Animal* a) { 
	a->sound(); 
}

void task2() {
	Dog d;
	Cat c;

	makeSound(&d);
	makeSound(&c);
}

class Vehicle {
public:
	virtual void move() {
		cout << "Транспорт рухається" << endl;
	}
};

class Car : public Vehicle {
public:
	void move() override {
		cout << "Автомобіль їде" << endl;
	}
};

class Bike : public Vehicle {
public:
	void move() override {
		cout << "Велосипед їде" << endl;
	}
};

class Garage {
public:
	void test(Vehicle& v) { 
		v.move();           
	}
};

void task3() {
	Car car;
	Bike bike;
	Garage g;

	g.test(car);
	g.test(bike);
}

int main()
{
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);
	int choice;
	do {
		std::cout << "\nВиберіть варіант (1, 2, 3, 0 = вихід): ";
		std::cin >> choice;
		switch (choice) {
		case 1: task1(); break;
		case 2: task2(); break;
		case 3: task3(); break;
		}
	} while (choice != 0);

	return 0;
}
