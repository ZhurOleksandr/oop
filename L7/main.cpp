#include <iostream>
#include <Windows.h>

using namespace std;

class Chislo
{
	protected:
		long n;

	public:
		Chislo(long value = 0)
		{
			n = value;
		}

		virtual ~Chislo()
		{
		}

		virtual long factorial(long x)
		{
			long result = 1;
			for (long i = 1; i <= x; i++)
			{
				result *= i;
			}
			return result;
		}

		long getN()
		{
			return n;
		}
};

class Matrix : public Chislo {
public:
	int arr[100];

	Matrix(long size) : Chislo(size)
	{
	}

	~Matrix()
	{
	}

	void input()
	{
		cout << "\nВведіть " << n << " елементи масиву:\n";
		for (int i = 0; i < n; i++)
		{
			cin >> arr[i];
		}
	}

	void show()
	{
		cout << "\nМасив:\n";
		for (int i = 0; i < n; i++)
		{
			cout << arr[i] << " ";
		}
		cout << endl;
	}
};

int main()
{
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);

	long size;
	cout << "Введіть розмір масиву: ";
	cin >> size;

	Chislo* chis;
	Matrix m(size);
	chis = &m;

	m.input();
	m.show();

	cout << "\nФакторіал:\n";
	for (int i = 0; i < m.getN(); i++)
	{
		cout << m.arr[i] << "! = " << chis->factorial(m.arr[i]) << endl;
	}
}
