#include "pch.h"
#include <iostream>
#include <list>
#include <Windows.h>

using namespace std;

int main()
{

	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);

	int n;
	cout << "Введіть n: ";
	cin >> n;

	list<double> L;
	cout << "Введіть " << n << " дійсних чисел:\n";
	for (int i = 0; i < n; i++) {
		double x;
		cin >> x;
		L.push_back(x);
	}

	bool hasLessThanMinus3 = false;
	for (double x : L) {
		if (x < -3) {
			hasLessThanMinus3 = true;
			break;
		}
	}

	for (auto it = L.begin(); it != L.end(); ++it) {
		if (hasLessThanMinus3) {
			if (*it < 0)
				*it = (*it) * (*it);
		}
		else {
			*it = (*it) * 0.1;
		}
	}

	cout << "Результат (у зворотному порядку):\n";
	for (auto it = L.rbegin(); it != L.rend(); ++it) {
		cout << *it << " ";
	}

	return 0;
}
