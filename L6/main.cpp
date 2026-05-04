#include "pch.h"
#include <iostream>
#include <list>
#include <Windows.h>

using namespace std;

template <class T>
class Arr
{
	public:
		int index;
		T value;

		Arr(int i, T v)
		{
			index = i;
			value = v;
		}
};

template <class T>
class SArr
{
	private:
		list<Arr<T>> data;
		int size;

	public:
		SArr(int n = 0)
		{
			size = n;
		}

		SArr(const SArr &other)
		{
			size = other.size;
			data = other.data;
		}

		SArr& operator=(const SArr &other)
		{
			if (this != &other) {
				size = other.size;
				data = other.data;
			}
			return *this;
		}

		T& operator[](int i)
		{
			for (auto &el : data)
			{
				if (el.index == i)
				{
					return el.value;
				}
			}

			data.push_back(Arr<T>(i, T()));
			return data.back().value;
		}

		void show()
		{
			cout << "Розріджений масив:\n";
			for (auto el : data)
			{
				cout << "index: " << el.index << " value: " << el.value << endl;
			}
		}

		void showFull()
		{
			cout << "\nМасив:\n";
			for (int i = 0; i < size; i++)
			{
				bool found = false;
				for (auto el : data)
				{
					if (el.index == i)
					{
						cout << el.value << " ";
						found = true;
						break;
					}
				}
				if (!found)
				{
					cout << "0 ";
				}
			}
			cout << endl;
		}
};

int main()
{
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);

	SArr<int> arr(6);
	arr[1] = 2;
	arr[3] = 3;
	arr[5] = 21;

	arr.show();
	arr.showFull();

	cout << endl;

	SArr<double> arr2(4);
	arr2[1] = 2.56;
	arr2[2] = 5.25;
	arr2[3] = 23.57;

	arr2.show();
	arr2.showFull();
}
