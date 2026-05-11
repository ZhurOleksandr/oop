#include <iostream>
#include <fstream>
#include <iomanip>
#include <vector>
#include <algorithm>
#include <string>
#include <Windows.h>

using namespace std;

class MathFunction
{
	double* x;
	double* y;
	int size;

	public:
		MathFunction() : x(nullptr), y(nullptr), size(0) {}

		~MathFunction() {
			delete[] x;
			delete[] y;
		}

		void allocate(int n)
		{
			delete[] x;
			delete[] y;
			size = n;
			x = new double[size];
			y = new double[size];
		}

		friend void showMinMax(const MathFunction& obj);

		friend ostream& operator<<(ostream& stream, const MathFunction& obj);

		void readFromFile(ifstream& file, int yColumnIndex);
};

ostream& operator<<(ostream& stream, const MathFunction& obj)
{
	stream << "\nГрафічне представлення (список точок)\n";
	for (int i = 0; i < obj.size; ++i)
	{
		stream << "X: " << setw(5) << obj.x[i] << " | ";

		int stars = static_cast<int>(obj.y[i] + 10);
		for (int j = 0; j < stars; ++j) stream << "*";
		stream << " (" << obj.y[i] << ")\n";
	}
	return stream;
}

void showMinMax(const MathFunction& obj)
{
	if (obj.size == 0) return;
	double minVal = obj.y[0];
	double maxVal = obj.y[0];
	for (int i = 1; i < obj.size; ++i)
	{
		if (obj.y[i] < minVal) minVal = obj.y[i];
		if (obj.y[i] > maxVal) maxVal = obj.y[i];
	}
	cout << "Мінімальне значення Y: " << minVal << endl;
	cout << "Максимальне значення Y: " << maxVal << endl;
}

void MathFunction::readFromFile(ifstream& file, int yColumnIndex)
{
	vector<double> tempX, tempY;
	double valX, valY1, valY2;

	file.clear();
	file.seekg(0, ios::beg);

	while (file >> valX >> valY1 >> valY2)
	{
		tempX.push_back(valX);
		tempY.push_back(yColumnIndex == 1 ? valY1 : valY2);
	}

	allocate(tempX.size());
	for (int i = 0; i < size; ++i)
	{
		x[i] = tempX[i];
		y[i] = tempY[i];
	}
}

void formatFile(const string& inputName, const string& outputName)
{
	ifstream in(inputName);
	ofstream out(outputName);

	if (!in || !out) return;

	double val;
	int count = 0;

	out << fixed << setprecision(3) << showpos;

	while (in >> val)
	{
		out << setw(10) << val;
		count++;

		if (count % 3 == 0)
		{
			out << "\n";
		}
		else {
			out << "\t";
		}
	}
	cout << "\nФайл '" << outputName << "' успішно створено з новим форматуванням.\n";
}

int main()
{
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);

	ofstream testFile("data.txt");
	testFile << "0.0 0.0 1.0\n"
		<< "1.0 2.5 -1.5\n"
		<< "2.0 4.2 0.5\n"
		<< "3.0 1.1 3.3\n"
		<< "4.0 -2.0 2.0\n";
	testFile.close();

	MathFunction func1, func2;
	ifstream dataIn("data.txt");

	if (dataIn.is_open()) {
		func1.readFromFile(dataIn, 1);
		func2.readFromFile(dataIn, 2);
		dataIn.close();
	}

	cout << "ДАНІ ФУНКЦІЇ 1\n";
	showMinMax(func1);
	cout << func1;

	cout << "\nДАНІ ФУНКЦІЇ 2\n";
	showMinMax(func2);
	cout << func2;

	formatFile("data.txt", "formatted_data.txt");

	return 0;
}
