#include <iostream>
#include <iomanip>
#include <Windows.h>

using namespace std;

// ==========================
// Структури
// ==========================

struct Krol
{
	int id;
	int voz;
	int massa;
};

struct A
{
	int x;
	int y;
};

// ==========================
// Прототипи функцій
// ==========================

void task1();
void task2();
void task3();
void task4();
void task5();
void task6();
void task7();
void task8();
void task9();
void task10();

void writeArray(char* name, int* mas);
void readArray(char* name, int* S, int* P);

// ==========================
// MAIN
// ==========================

int main()
{
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);

	cout << "\nЗадача 1\n";
	task1();
	cout << "\nЗадача 2\n";
	task2();
	cout << "\nЗадача 3\n";
	task3();
	cout << "\nЗадача 4\n";
	task4();
	cout << "\nЗадача 5\n";
	task5();
	cout << "\nЗадача 6\n";
	task6();
	cout << "\nЗадача 7\n";
	task7();
	cout << "\nЗадача 8\n";
	task8();
	cout << "\nЗадача 9\n";
	task9();
	cout << "\nЗадача 10\n";
	task10();

	return 0;
}

// ======================================================
// Задача 1
// ======================================================

void task1()
{
	FILE* f;

	fopen_s(&f, "task1.txt", "w");

	cout << "\nВведіть символи (# - завершення):\n";

	char ch = getchar();

	while (ch != '#')
	{
		fputc(ch, f);
		ch = getchar();
	}

	fclose(f);

	fopen_s(&f, "task1.txt", "r");

	cout << "\nДані з файлу:\n";

	ch = fgetc(f);

	while (!feof(f))
	{
		putchar(ch);
		ch = fgetc(f);
	}

	fclose(f);

	cout << endl;
}

// ======================================================
// Задача 2
// ======================================================

void task2()
{
	FILE* f;

	int n;

	cout << "\nВведіть кількість рядків -> ";
	cin >> n;

	cin.ignore();

	fopen_s(&f, "task2.txt", "w");

	char* s = new char[100];

	for (int i = 0; i < n; i++)
	{
		cout << "Рядок " << i + 1 << " -> ";

		cin.getline(s, 100);

		fputs(s, f);
		fputs("\n", f);
	}

	fclose(f);

	fopen_s(&f, "task2.txt", "r");

	cout << "\nДані з файлу:\n";

	for (int i = 0; i < n; i++)
	{
		fgets(s, 100, f);
		cout << s;
	}

	fclose(f);

	delete[] s;
}

// ======================================================
// Задача 3
// ======================================================

void task3()
{
	FILE* f1;
	FILE* f2;

	fopen_s(&f1, "task3_1.txt", "w");

	int x;
	int sum = 0;

	cout << "\nЧисла:\n";

	for (int i = 0; i < 20; i++)
	{
		x = rand() % 100 + 1;

		cout << x << " ";

		fprintf(f1, "%d ", x);
	}

	fclose(f1);

	fopen_s(&f1, "task3_1.txt", "r");
	fopen_s(&f2, "task3_2.txt", "w");

	for (int i = 0; i < 20; i++)
	{
		fscanf_s(f1, "%d", &x);

		fprintf(f2, "%d ", x);

		sum += x;
	}

	fclose(f1);
	fclose(f2);

	double sa = (double)sum / 20;

	cout << "\nСереднє арифметичне = " << sa << endl;
}

// ======================================================
// Задача 4
// ======================================================

void task4()
{
	FILE* f;

	char name[20];

	cout << "\nВведіть ім'я файлу -> ";
	cin.getline(name, 20);

	fopen_s(&f, name, "wb");

	int x;

	for (int i = 0; i < 10; i++)
	{
		x = rand() % 50;

		fwrite(&x, sizeof(int), 1, f);
	}

	fclose(f);

	fopen_s(&f, name, "rb");

	int max = 0;

	cout << "\nЧисла з файлу:\n";

	for (int i = 0; i < 10; i++)
	{
		fread(&x, sizeof(int), 1, f);

		cout << x << " ";

		if (x > max)
			max = x;
	}

	cout << "\nМаксимальне число = " << max << endl;

	fclose(f);
}

// ======================================================
// Задача 5
// ======================================================

void task5()
{
	FILE* f;

	int mas[5] = { 1,2,3,4,5 };

	fopen_s(&f, "task5.dat", "wb");

	fwrite(mas, sizeof(int), 5, f);

	fclose(f);

	int mas2[5];

	fopen_s(&f, "task5.dat", "rb");

	fread(mas2, sizeof(int), 5, f);

	fclose(f);

	cout << "\nМасив після читання:\n";

	for (int i = 0; i < 5; i++)
	{
		cout << mas2[i] << " ";
	}

	cout << endl;
}

// ======================================================
// Задача 6
// ======================================================

void task6()
{
	FILE* f;

	int mas[11] = { 0,11,22,33,44,55,66,77,88,99,100 };

	fopen_s(&f, "task6.dat", "wb");

	fwrite(mas, sizeof(int), 11, f);

	fclose(f);

	fopen_s(&f, "task6.dat", "rb");

	int x;

	fseek(f, 5 * sizeof(int), SEEK_SET);

	fread(&x, sizeof(int), 1, f);

	cout << "\nП'ятий елемент = " << x << endl;

	fclose(f);
}

// ======================================================
// Задача 7
// ======================================================

void task7()
{
	FILE* f;

	int mas[10];

	cout << "\nМасив:\n";

	for (int i = 0; i < 10; i++)
	{
		mas[i] = rand() % 30;

		cout << setw(4) << mas[i];
	}

	fopen_s(&f, "task7.dat", "wb");

	fwrite(mas, sizeof(int), 10, f);

	fclose(f);

	fopen_s(&f, "task7.dat", "r+b");

	int x;
	int max = 0;
	int imax = 0;

	for (int i = 0; i < 10; i++)
	{
		fread(&x, sizeof(int), 1, f);

		if (x > max)
		{
			max = x;
			imax = i;
		}
	}

	cout << "\nМаксимум = " << max << endl;

	int zero = 0;

	fseek(f, imax * sizeof(int), SEEK_SET);

	fwrite(&zero, sizeof(int), 1, f);

	fclose(f);

	fopen_s(&f, "task7.dat", "rb");

	cout << "\nМасив після зміни:\n";

	for (int i = 0; i < 10; i++)
	{
		fread(&x, sizeof(int), 1, f);

		cout << setw(4) << x;
	}

	fclose(f);

	cout << endl;
}

// ======================================================
// Задача 8
// ======================================================

void task8()
{
	FILE* f;

	Krol dat, max;

	int n;

	cout << "\nКількість кроликів -> ";
	cin >> n;

	fopen_s(&f, "krol.dat", "wb");

	for (int i = 0; i < n; i++)
	{
		cout << "Введіть id вік масу -> ";

		cin >> dat.id >> dat.voz >> dat.massa;

		fwrite(&dat, sizeof(Krol), 1, f);
	}

	fclose(f);

	fopen_s(&f, "krol.dat", "rb");

	fread(&max, sizeof(Krol), 1, f);

	while (fread(&dat, sizeof(Krol), 1, f))
	{
		if (dat.voz > max.voz)
		{
			max = dat;
		}
		else if (dat.voz == max.voz &&
			dat.massa > max.massa)
		{
			max = dat;
		}
	}

	fclose(f);

	cout << "\nПотрібний кролик:\n";

	cout << "ID = " << max.id << endl;
	cout << "Вік = " << max.voz << endl;
	cout << "Маса = " << max.massa << endl;

	cin.ignore();
}

// ======================================================
// Задача 9
// ======================================================

void task9()
{
	FILE* f;

	A spis[4];

	fopen_s(&f, "task9.dat", "wb");

	for (int i = 0; i < 3; i++)
	{
		cout << "Введіть x y -> ";

		cin >> spis[i].x >> spis[i].y;

		fwrite(&spis[i], sizeof(A), 1, f);
	}

	fclose(f);

	A dat;

	dat.x = 9;
	dat.y = 99;

	fopen_s(&f, "task9.dat", "ab");

	fwrite(&dat, sizeof(A), 1, f);

	fclose(f);

	fopen_s(&f, "task9.dat", "rb");

	cout << "\nДані з файлу:\n";

	for (int i = 0; i < 4; i++)
	{
		fread(&spis[i], sizeof(A), 1, f);

		cout << spis[i].x << " "
			<< spis[i].y << endl;
	}

	fclose(f);

	cin.ignore();
}

// ======================================================
// Задача 10
// ======================================================

#define N 5

void writeArray(char* name, int* mas)
{
	FILE* f;

	fopen_s(&f, name, "wb");

	fwrite(mas, sizeof(int), N, f);

	fclose(f);
}

void readArray(char* name, int* S, int* P)
{
	FILE* f;

	fopen_s(&f, name, "rb");

	int x;

	for (int i = 0; i < N; i++)
	{
		fread(&x, sizeof(int), 1, f);

		if (x > 0)
			*P *= x;
		else
			*S += x;
	}

	fclose(f);
}

void task10()
{
	int mas[N];

	cout << "\nМасив:\n";

	for (int i = 0; i < N; i++)
	{
		mas[i] = rand() % 11 - 5;

		cout << mas[i] << " ";
	}

	int S = 0;
	int P = 1;

	char name[] = "task10.dat";

	writeArray(name, mas);

	readArray(name, &S, &P);

	cout << "\nСума негативних = " << S << endl;
	cout << "Добуток позитивних = " << P << endl;
}
