#include <iostream>
#include <cstdarg>
#include <Windows.h>

using namespace std;

// а) Перевантаження функцій (для 3 аргументів)
// Повернення через посилання
int& sumOverload(int& first, int second, int third) {
	std::cout << "[Проміжне] Виклик перевантаження. Початковий перший: " << first << "\n";
	first = first + second + third;
	return first;
}

// б) Функція з параметрами за замовчуванням (максимум 4 аргументи)
// Повернення через вказівник
int* sumDefault(int* first, int second = 0, int third = 0, int fourth = 0) {
	std::cout << "[Проміжне] Виклик функції з default-параметрами.\n";
	*first = *first + second + third + fourth;
	return first;
}

// в) Функція зі змінною кількістю параметрів (перший параметр - кількість НАСТУПНИХ аргументів)
int& sumVariadic(int& first, int count, ...) {
	std::cout << "[Проміжне] Виклик variadic функціі. Кількість додаткових доданків: " << count << "\n";
	va_list args;
	va_start(args, count);

	int total = first;
	for (int i = 0; i < count; ++i) {
		total += va_arg(args, int);
	}
	va_end(args);

	first = total;
	return first;
}

int main()
{
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);

	// Тест А: Перевантаження (посилання)
	int a1, b1, c1;
	std::cout << "Тест А. Введіть три числа: "; std::cin >> a1 >> b1 >> c1;
	int& resRef = sumOverload(a1, b1, c1);
	std::cout << "Кінцеве значення змінної a1: " << a1 << "\n";
	std::cout << "Значення повернуте через посилання: " << resRef << "\n\n";

	// Тест Б: Параметри за замовчуванням (вказівник)
	int a2, b2;
	std::cout << "Тест Б. Введіть два числа (для першого та другого аргументу): "; std::cin >> a2 >> b2;
	int* resPtr = sumDefault(&a2, b2); // Інші два за замовчуванням = 0
	std::cout << "Кінцеве значення змінної a2: " << a2 << "\n";
	std::cout << "Значення за адресою з вказівника: " << *resPtr << "\n\n";

	// Тест В: Змінна кількість аргументів f(int&, count, ...)
	int a3;
	std::cout << "Тест В. Введіть початкове значення першого аргументу: "; std::cin >> a3;
	// Додамо 4 фіксованих доданки: 10, 20, 30, 40
	sumVariadic(a3, 4, 10, 20, 30, 40);
	std::cout << "Кінцеве значення після додавання (10+20+30+40): " << a3 << "\n";

	return 0;
}
