#include <iostream>
#include <Windows.h>

using namespace std;

class DigitalCounter {
private:
	int minVal;
	int maxVal;
	int currentVal;
public:
	DigitalCounter() : minVal(0), maxVal(9), currentVal(0) {}

	void setBounds(int minV, int maxV) {
		if (minV > maxV) {
			std::cout << "Помилка! Мінімум не може бути більшим за максимум. Встановлено за замовчуванням.\n";
			minVal = 0; maxVal = 9;
		}
		else {
			minVal = minV;
			maxVal = maxV;
		}
		currentVal = minVal;
		std::cout << "Встановлено межі: [" << minVal << "; " << maxVal << "]. Поточне значення: " << currentVal << "\n";
	}

	void increment() {
		std::cout << "Проміжне значення перед інкрементом: " << currentVal;
		if (currentVal >= maxVal) {
			currentVal = minVal; // Скидання
			std::cout << " -> Досягнуто максимум! Скидання.";
		}
		else {
			currentVal++;
		}
		std::cout << " -> Поточне значення: " << currentVal << "\n";
	}

	int getValue() const {
		return currentVal;
	}
};

int main()
{
	SetConsoleCP(1251);
	SetConsoleOutputCP(1251);

	DigitalCounter counter;
	int minB, maxB;

	std::cout << "Введіть мінімальне значення лічильника: "; std::cin >> minB;
	std::cout << "Введіть максимальне значення лічильника: "; std::cin >> maxB;

	counter.setBounds(minB, maxB);

	int steps;
	std::cout << "Скільки разів збільшити лічильник? "; std::cin >> steps;

	for (int i = 0; i < steps; ++i) {
		counter.increment();
	}

	std::cout << "\nКінцеве значення лічильника: " << counter.getValue() << std::endl;
	return 0;
}
