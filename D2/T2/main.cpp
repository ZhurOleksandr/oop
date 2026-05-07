#include <iostream>
#include <vector>
#include <string>
#include <stdexcept>
#include <algorithm>
#include <clocale>
#include "windows.h"

using namespace std;

template<typename T = std::string>
class Stack {
private:
	std::vector<T> data;

public:
	void push(const T& value) {
		data.push_back(value);
	}

	T pop() {
		if (data.empty()) {
			throw std::runtime_error("Stack is empty!");
		}
		T topElement = data.back();
		data.pop_back();
		return topElement;
	}

	const T& top() const {
		if (data.empty()) {
			throw std::runtime_error("Stack is empty!");
		}
		return data.back();
	}

	bool empty() const {
		return data.empty();
	}

	size_t size() const {
		return data.size();
	}

	void clear() {
		data.clear();
	}
};

std::string findLongest(const Stack<std::string>& st) {
	if (st.empty()) return "";

	// Створюємо копію, бо stack не дозволяє ітерацію напряму
	Stack<std::string> temp = st;   // потребує конструктора копії
	std::string longest = temp.pop();

	while (!temp.empty()) {
		std::string current = temp.pop();
		if (current.length() > longest.length()) {
			longest = current;
		}
	}
	return longest;
}

int main() {
	SetConsoleOutputCP(1251);

	Stack<std::string> st;        // Створюємо стек рядків

	// 1. Додавання елементів у стек (push)
	st.push("Привіт");
	st.push("Світ");
	st.push("C++");
	st.push("Об'єктно-орієнтоване програмування");
	st.push("Найдовший рядок у цьому стеку!!!");

	std::cout << "Кількість елементів у стеку: " << st.size() << "\n\n";

	// 2. Читання верхнього елемента без видалення
	std::cout << "Верхній елемент: " << st.top() << "\n\n";
	// 4. 
	std::cout << "Найдовший рядок: " << findLongest(st) << "\n\n";

	// 3. Витягування елементів зі стеку (pop)
	std::cout << "Витягуємо елементи зі стеку:\n";
	while (!st.empty()) {
		std::cout << st.pop() << "\n";
	}

	std::cout << "\nСтек порожній: " << (st.empty() ? "Так" : "Ні") << "\n";

	return 0;
}