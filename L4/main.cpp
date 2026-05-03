#include "pch.h"
#include <iostream>
#include <vector>
#include <algorithm>
#include <Windows.h>

using namespace std;

template <class T>
void procVec(vector<T>& v)
{
	for (int i = 0; i < v.size(); i++)
		cin >> v[i];

	sort(v.begin(), v.end());

	cout << "Відсортовані вектори:\n";
	for (int i = 0; i < v.size(); i++)
		cout << v[i] << " ";
	cout << endl;
}

int main()
{
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);
	
	int n;

	cout << "Введіть розмір: ";
	cin >> n;

	vector<int> v(n);

	cout << "Введіть елементи:\n";
	procVec(v);

	return 0;
}
