#include <iostream>
#include <Windows.h>

using namespace std;

class Vect {
public:
	Vect(char);
	~Vect();

	int& operator[](int i);
	void Print();

private:
	int* p;
	char size;
};

Vect::Vect(char n) : size(n)
{
	try
	{
		if (n <= 0)
		{
			throw "Invalid size";
		}

		p = new int[(unsigned char)size];

		if (!p)
		{
			throw "Memory allocation error";
		}

		for (int i = 0; i < (unsigned char)size; ++i)
			p[i] = 0;
	}
	catch (const char* msg)
	{
		cerr << "Error of Vect constructor: " << msg << endl;
		p = nullptr;
		size = 0;
	}
}

Vect::~Vect()
{
	try
	{
		if (p)
		{
			delete[] p;
		}
	}
	catch (...)
	{
		cerr << "Error of Vect destructor" << endl;
	}
}

int& Vect::operator[](int i)
{
	if (i < 0 || i >= (unsigned char)size)
	{
		throw out_of_range("Index out of range");
	}
	return p[i];
}

void Vect::Print()
{
	if (!p)
	{
		cout << "Vector is empty\n";
		return;
	}

	for (int i = 0; i < (unsigned char)size; ++i)
		cout << p[i] << " ";

	cout << endl;
}

int main()
{
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);
	
	try
	{
		cout << "Масиву розміром 3:" << endl;
		Vect a(3);

		a[0] = 0;
		a[1] = 1;
		a[2] = 2;

		a.Print();

		cout << "Масиву розміром 125:" << endl;
		Vect a1(125);

		a1[5] = 5;
		a1[10] = 10;
		a1[15] = 15;
		a1.Print();

		cout << "Масиву розміром 200:" << endl;
		Vect a2(200);

		a2[10] = 5;
		a2.Print();
	}
	catch (const out_of_range& e)
	{
		cerr << "Index error: " << e.what() << endl;
	}
	catch (...)
	{
		cerr << "Unknown error!" << endl;
	}

	return 0;
}

