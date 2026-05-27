#include <iostream>
#include <vector>
#include <memory>
#include <Windows.h>

using namespace std;

// Абстрактний клас
class Shape {
protected:
	double x, y;       // Координати центра
	double angle;      // Кут повороту в градусах
	double scaleFactor;// Масштабний фактор
public:
	Shape() : x(0), y(0), angle(0), scaleFactor(1.0) {}

	virtual void inputData() {
		std::cout << "Введіть x, y центра: "; std::cin >> x >> y;
		std::cout << "Введіть кут повороту (градуси): "; std::cin >> angle;
		std::cout << "Введіть масштаб: "; std::cin >> scaleFactor;
	}

	virtual void draw() const = 0;       // Чисто віртуальні функції
	virtual void hide() const = 0;

	void rotate(double deltaAngle) {
		angle += deltaAngle;
		std::cout << "Об'єкт повернуто на " << deltaAngle << " градусів. Поточний кут: " << angle << "\n";
	}

	void move(double dx, double dy) {
		x += dx; y += dy;
		std::cout << "Об'єкт переміщено на вектор (" << dx << ", " << dy << "). Новий центр: (" << x << ", " << y << ")\n";
	}

	virtual ~Shape() = default;
};

class Triangle : public Shape {
public:
	void draw() const override { std::cout << "[Екран] Відображено ТРИКУТНИК з центром (" << x << ", " << y << ")\n"; }
	void hide() const override { std::cout << "[Екран] ТРИКУТНИК тепер невидимий.\n"; }
};

class Quadrangle : public Shape {
public:
	void draw() const override { std::cout << "[Екран] Відображено ЧОТИРИКУТНИК з центром (" << x << ", " << y << ")\n"; }
	void hide() const override { std::cout << "[Екран] ЧОТИРИКУТНИК тепер невидимий.\n"; }
};

class Polygonn : public Shape {
public:
	void draw() const override { std::cout << "[Екран] Відображено МНОГОКУТНИК з центром (" << x << ", " << y << ")\n"; }
	void hide() const override { std::cout << "[Екран] МНОГОКУТНИК тепер невидимий.\n"; }
};

int main()
{
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);

	const int SIZE = 3;
	Shape* shapes[SIZE];

	shapes[0] = new Triangle();
	shapes[1] = new Quadrangle();
	shapes[2] = new Polygonn();

	for (int i = 0; i < SIZE; ++i) {
		std::cout << "\n--- Налаштування фігури " << i + 1 << " ---\n";
		shapes[i]->inputData();
	}

	std::cout << "\n=== Перевірка пізнього зв'язування (Віртуальні функції) ===\n";
	for (int i = 0; i < SIZE; ++i) {
		shapes[i]->draw();
		shapes[i]->move(5.0, -2.0);
		shapes[i]->rotate(15);
		shapes[i]->hide();
		std::cout << "-----------------------------------\n";
	}

	// Очищення пам'яті
	for (int i = 0; i < SIZE; ++i) {
		delete shapes[i];
	}

	return 0;
}
