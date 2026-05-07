#include <iostream>
#include <string>
#include <stack>

using namespace std;

template <typename T>
class RingList {
private:
	struct Node {
		T data;
		Node* next;
		Node(const T& d) : data(d), next(nullptr) {}
	};

	Node* head = nullptr;
	size_t count = 0;

public:
	RingList() = default;

	~RingList() { clear(); }

	void insert(const T& val) {
		Node* newNode = new Node(val);
		if (head == nullptr) {
			head = newNode;
			newNode->next = head;
		}
		else {
			Node* temp = head;
			while (temp->next != head) {
				temp = temp->next;
			}
			temp->next = newNode;
			newNode->next = head;
		}
		++count;
	}

	bool remove(const T& val) {
		if (head == nullptr) return false;

		Node* curr = head;
		Node* prev = nullptr;

		do {
			if (curr->data == val) {
				if (curr == head) {                    // видаляємо голову
					if (count == 1) {                  // останній елемент
						delete head;
						head = nullptr;
					}
					else {
						Node* last = head;
						while (last->next != head) last = last->next;
						head = head->next;
						last->next = head;
					}
				}
				else {
					prev->next = curr->next;
				}
				delete curr;
				--count;
				return true;
			}
			prev = curr;
			curr = curr->next;
		} while (curr != head);

		return false; // не знайдено
	}

	void print() const {
		if (head == nullptr) {
			std::cout << "List is empty\n";
			return;
		}
		Node* temp = head;
		do {
			std::cout << temp->data << " ";
			temp = temp->next;
		} while (temp != head);
		std::cout << "\n";
	}

	size_t size() const { return count; }

	void clear() {
		if (head == nullptr) return;
		Node* curr = head;
		do {
			Node* next = curr->next;
			delete curr;
			curr = next;
		} while (curr != head);
		head = nullptr;
		count = 0;
	}
};

int main() {
	// Створення кільцевого списку цілих чисел
	RingList<int> list;

	// 1. Додавання елементів
	list.insert(10);
	list.insert(20);
	list.insert(30);
	list.insert(40);
	list.insert(50);

	std::cout << "List: ";
	list.print();                    // 10 20 30 40 50 

	std::cout << "Elements count: " << list.size() << "\n\n";

	// 2. Видалення елементів
	list.remove(30);                 // видаляємо 30
	list.remove(10);                 // видаляємо 10 (голову)

	std::cout << "List, after remove 30 and 10: ";
	list.print();                    // 20 40 50 

	std::cout << "Elements count: " << list.size() << "\n";

	// 3. Приклад зі рядками
	RingList<std::string> names;
	names.insert("Anna");
	names.insert("Bogdan");
	names.insert("Vyktoryia");

	std::cout << "\nName list: ";
	names.print();

	return 0;
}