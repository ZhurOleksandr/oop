#include "pch.h"
#include <iostream>
#include <Windows.h>

using namespace std;

// ===== Task 1 =====
double power(double n, int p = 2)
{
	double res = 1.0;

	for (int i = 0; i < p; i++)
	{
		res *= n;
	}

	return res;
}

void task1()
{
	double n;
	int exp;

	cout << "Введіть число: ";
	cin >> n;

	cout << "Введіть степінь (0 - за замовчуванням 2): ";
	cin >> exp;

	if (exp == 0)
	{
		cout << "Результат: " << power(n) << endl;
	} else {
		cout << "Результат: " << power(n, exp) << endl;
	}
}

void zeroSmaller(int& a, int& b)
{
	if (a < b)
	{
		a = 0;
	} else if (b < a) {
		b = 0;
	} else {
		a = 0;
		b = 0;
	}
}

void task2()
{
	int x, y;

	cout << "Введіть два числа: ";
	cin >> x >> y;

	zeroSmaller(x, y);

	cout << "Результат:" << endl;
	cout << "x = " << x << endl;
	cout << "y = " << y << endl;
}

struct Distance
{
	int meters;
	float centimeters;
};

Distance maxDistance(Distance d1, Distance d2)
{
	float total1 = d1.meters * 100 + d1.centimeters;
	float total2 = d2.meters * 100 + d2.centimeters;

	if (total1 > total2)
	{
		return d1;
	}
	else {
		return d2;
	}
}

void task3()
{
	Distance d1, d2, result;

	cout << "Введіть першу відстань (м см): ";
	cin >> d1.meters >> d1.centimeters;

	cout << "Введіть другу відстань (м см): ";
	cin >> d2.meters >> d2.centimeters;

	result = maxDistance(d1, d2);

	cout << "Більша відстань: " << result.meters << " м " << result.centimeters << " см" << endl;
}

int main()
{
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);
	int choice;
	do {
		std::cout << "\nВиберіть завдання (1, 2, 3, 0 = вихід): ";
		std::cin >> choice;
		switch (choice) {
		case 1: task1(); break;
		case 2: task2(); break;
		case 3: task3(); break;
		}
	} while (choice != 0);

	return 0;
}
