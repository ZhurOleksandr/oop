#include <iostream>
#include <vector>
#include <iomanip>
#include <Windows.h>

using namespace std;

// ====================== БАЗОВИЙ КЛАС ======================
class Base {
public:
	// Чисто віртуальна функція факторіалу
	virtual long long factorial(int n) = 0;

	// Віртуальний деструктор — обов'язково!
	virtual ~Base() = default;
};

// ====================== ПОХІДНИЙ КЛАС ======================
class Derived : public Base {
private:
	std::vector<int> numbers = { 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 };

public:
	// Реалізація віртуальної функції
	long long factorial(int n) override {
		if (n < 0) {
			throw std::invalid_argument("Факторіал від'ємного числа не визначено!");
		}
		if (n == 0 || n == 1) return 1;
		return n * factorial(n - 1);        // рекурсія
	}

	// Метод для обчислення факторіалів масиву
	void computeAll() {
		std::cout << "Факторіали чисел:\n";
		std::cout << "-----------------\n";
		for (int x : numbers) {
			std::cout << std::setw(2) << x << "! = "
				<< factorial(x) << "\n";
		}
	}
};

// ====================== MAIN ======================
int main() {
	SetConsoleOutputCP(1251);
	// 1. Звичайне використання через об'єкт похідного класу
	Derived d;
	d.computeAll();

	std::cout << "\n=== Демонстрація пізнього зв'язування ===\n";

	// 2. Використання через вказівник на базовий клас (поліморфізм)
	Base* basePtr = new Derived();   // вказівник на базовий клас

	std::cout << "5! = " << basePtr->factorial(5) << "\n";
	std::cout << "8! = " << basePtr->factorial(8) << "\n";

	// 3. Масив вказівників (як у завданні 3 рівня)
	Base* equations[2];
	equations[0] = new Derived();
	equations[1] = new Derived();

	std::cout << "\nЧерез масив вказівників:\n";
	for (int i = 0; i < 2; ++i) {
		std::cout << "10! = " << equations[i]->factorial(10) << "\n";
		delete equations[i];
	}

	delete basePtr;

	return 0;
}