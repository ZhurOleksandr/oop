#include <iostream>
#include <Windows.h>

using namespace std;

template <typename T>
class DynamicArray2D {
private:
	T** data;
	int rows;
	int cols;

	void allocate(int r, int c) {
		rows = r; cols = c;
		data = new T*[rows];
		for (int i = 0; i < rows; ++i) {
			data[i] = new T[cols]{};
		}
	}

	void clear() {
		if (data) {
			for (int i = 0; i < rows; ++i) delete[] data[i];
			delete[] data;
			data = nullptr;
		}
	}

public:
	DynamicArray2D(int r, int c) { allocate(r, c); }
	~DynamicArray2D() { clear(); }

	// Потокове введення
	friend std::istream& operator>>(std::istream& in, DynamicArray2D& arr) {
		for (int i = 0; i < arr.rows; ++i) {
			for (int j = 0; j < arr.cols; ++j) {
				std::cout << "Елемент [" << i << "][" << j << "]: ";
				in >> arr.data[i][j];
			}
		}
		return in;
	}

	// Потокове виведення
	friend std::ostream& operator<<(std::ostream& out, const DynamicArray2D& arr) {
		for (int i = 0; i < arr.rows; ++i) {
			for (int j = 0; j < arr.cols; ++j) {
				out << arr.data[i][j] << "\t";
			}
			out << "\n";
		}
		return out;
	}

	// Повна копія
	DynamicArray2D(const DynamicArray2D& other) {
		allocate(other.rows, other.cols);
		copyAll(other);
	}

	void copyAll(const DynamicArray2D& other) {
		for (int i = 0; i < rows; ++i)
			for (int j = 0; j < cols; ++j)
				data[i][j] = other.data[i][j];
	}

	// Копіювання за рядками (реверс чи звичайне зміщення — для прикладу просто копіюємо зміщені дані)
	void copyByRows(const DynamicArray2D& other) {
		std::cout << "[Процес] Порядкове копіювання...\n";
		for (int i = 0; i < rows && i < other.rows; ++i) {
			for (int j = 0; j < cols && j < other.cols; ++j) {
				this->data[i][j] = other.data[i][j];
			}
		}
	}

	// Копіювання за стовпцями
	void copyByCols(const DynamicArray2D& other) {
		std::cout << "[Процес] Постовпчикове копіювання...\n";
		for (int j = 0; j < cols && j < other.cols; ++j) {
			for (int i = 0; i < rows && i < other.rows; ++i) {
				this->data[i][j] = other.data[i][j];
			}
		}
	}

	// Копіювання конкретного рядка
	void copySpecificRow(const DynamicArray2D& other, int srcRow, int destRow) {
		if (srcRow < other.rows && destRow < this->rows) {
			for (int j = 0; j < cols && j < other.cols; ++j) {
				this->data[destRow][j] = other.data[srcRow][j];
			}
		}
	}

	// Копіювання головної діагоналі
	void copyMainDiagonal(const DynamicArray2D& other) {
		std::cout << "[Процес] Копіювання головної діагоналі на діагональ нової матриці...\n";
		for (int i = 0; i < rows && i < other.rows && i < cols && i < other.cols; ++i) {
			this->data[i][i] = other.data[i][i];
		}
	}
};

int main()
{
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);

	int r, c;
	std::cout << "Введіть кількість рядків та стовпців: ";
	std::cin >> r >> c;

	DynamicArray2D<int> source(r, c);
	std::cout << "Заповніть початкову матрицю:\n";
	std::cin >> source;

	std::cout << "\nВведена матриця:\n" << source;

	DynamicArray2D<int> target1(r, c);
	target1.copyByRows(source);
	std::cout << "Результат після copyByRows:\n" << target1;

	DynamicArray2D<int> target2(r, c);
	target2.copyMainDiagonal(source);
	std::cout << "Результат копіювання головної діагоналі:\n" << target2;

	return 0;
}
