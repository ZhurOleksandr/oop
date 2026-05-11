#include <iostream>
#include <string>

using namespace std;

struct Node 
{
	int data;
	Node* next;
	Node* prev;
};

Node* head = NULL;

void createList() 
{
	int n, val;
	cout << "Enter number of elements: ";
	cin >> n;

	Node* tail = NULL;

	for (int i = 0; i < n; i++) 
	{
		cout << "Enter value: ";
		cin >> val;

		Node* temp = new Node;
		temp->data = val;
		temp->next = NULL;
		temp->prev = tail;

		if (head == NULL)
			head = tail = temp;
		else 
		{
			tail->next = temp;
			tail = temp;
		}
	}
}

void showForward() 
{
	Node* temp = head;

	if (!head) 
	{
		cout << "List is empty\n";
		return;
	}

	cout << "Forward: ";
	while (temp) 
	{
		cout << temp->data << " ";
		temp = temp->next;
	}
	cout << endl;
}

void showBackward() 
{
	if (!head) return;

	Node* temp = head;

	while (temp->next)
		temp = temp->next;

	cout << "Backward: ";
	while (temp) 
	{
		cout << temp->data << " ";
		temp = temp->prev;
	}
	cout << endl;
}

void addBegin() 
{
	int val;
	cout << "Enter value: ";
	cin >> val;

	Node* temp = new Node;
	temp->data = val;
	temp->prev = NULL;
	temp->next = head;

	if (head)
		head->prev = temp;

	head = temp;
}

void addEnd() 
{
	int val;
	cout << "Enter value: ";
	cin >> val;

	Node* temp = new Node;
	temp->data = val;
	temp->next = NULL;

	if (!head) 
	{
		temp->prev = NULL;
		head = temp;
		return;
	}

	Node* t = head;
	while (t->next)
		t = t->next;

	t->next = temp;
	temp->prev = t;
}

void removeBegin() 
{
	if (!head) return;

	Node* temp = head;
	head = head->next;

	if (head)
		head->prev = NULL;

	delete temp;
}

void removeEnd() 
{
	if (!head) return;

	Node* temp = head;

	while (temp->next)
		temp = temp->next;

	if (temp->prev)
		temp->prev->next = NULL;
	else
		head = NULL;

	delete temp;
}

void removeByKey() 
{
	int key;
	cout << "Enter value to delete: ";
	cin >> key;

	Node* temp = head;

	while (temp) {
		if (temp->data == key) 
		{

			if (temp->prev)
				temp->prev->next = temp->next;
			else
				head = temp->next;

			if (temp->next)
				temp->next->prev = temp->prev;

			delete temp;
			return;
		}
		temp = temp->next;
	}

	cout << "Not found\n";
}

void addByKey() 
{
	int key, val;
	cout << "Enter key: ";
	cin >> key;

	cout << "Enter value: ";
	cin >> val;

	Node* temp = head;

	while (temp) 
	{
		if (temp->data == key) 
		{

			Node* newNode = new Node;
			newNode->data = val;

			newNode->next = temp->next;
			newNode->prev = temp;

			if (temp->next)
				temp->next->prev = newNode;

			temp->next = newNode;
			return;
		}
		temp = temp->next;
	}

	cout << "Key not found\n";
}

void clearList()
{
	while (head) {
		Node* temp = head;
		head = head->next;
		delete temp;
	}
}

int main()
{
	int choice;

	do {
		cout << "\nMENU:\n";
		cout << "1.Create\n2.Show forward\n3.Show backward\n";
		cout << "4.Remove begin\n5.Remove by key\n6.Remove end\n";
		cout << "7.Add begin\n8.Add end\n9.Add by key\n10.Exit\n";

		cin >> choice;

		switch (choice)
		{
		case 1: createList(); break;
		case 2: showForward(); break;
		case 3: showBackward(); break;
		case 4: removeBegin(); break;
		case 5: removeByKey(); break;
		case 6: removeEnd(); break;
		case 7: addBegin(); break;
		case 8: addEnd(); break;
		case 9: addByKey(); break;
		case 10: clearList(); break;
		default: cout << "Error\n";
		}

	} while (choice != 10);

	return 0;
}