#include "pch.h"
#include <iostream>
#include <Windows.h>

using namespace std;

template <class T>
class SortArray
{
private:
	T arr[100];
	int size;

public:
	SortArray(int n)
	{
		size = n;
	}

	void input()
	{
		cout << "Введіть елементи масиву:\n";
		for (int i = 0; i < size; i++)
			cin >> arr[i];
	}

	void sort()
	{
		for (int i = 0; i < size - 1; i++)
			for (int j = i + 1; j < size; j++)
				if (arr[i] > arr[j])
				{
					T temp = arr[i];
					arr[i] = arr[j];
					arr[j] = temp;
				}
	}

	void show()
	{
		cout << "Відсортований масив:\n";
		for (int i = 0; i < size; i++)
			cout << arr[i] << " ";
		cout << endl;
	}
};

int main()
{
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);
	
	int n;

	cout << "Введіть розмір масиву: ";
	cin >> n;

	SortArray<int> a(n);
	a.input();
	a.sort();
	a.show();

	SortArray<double> b(n);
	b.input();
	b.sort();
	b.show();

	return 0;
}