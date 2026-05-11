#include <iostream>
#include <string>

using namespace std;

struct List
{
	int x;
	List* next;
};

List* head = NULL;

void CreateList()
{
	int n, value;
	cout << "Enter number of elements: ";
	cin >> n;

	List* temp, *tail = NULL;

	for (int i = 0; i < n; i++)
	{
		cout << "Enter value: ";
		cin >> value;

		temp = new List;
		temp->x = value;
		temp->next = NULL;

		if (head == NULL)
		{
			head = tail = temp;
		}
		else
		{
			tail->next = temp;
			tail = temp;
		}
	}
}

void DisplayList()
{
	if (head == NULL) 
	{
		cout << "List is empty\n";
		return;
	}

	List* temp = head;
	cout << "List: ";

	while (temp != NULL) 
	{
		cout << temp->x << " ";
		temp = temp->next;
	}
	cout << endl;
}

void RemoveBegin() 
{
	if (head == NULL) return;

	List* temp = head;
	head = head->next;
	delete temp;
}

void RemoveEnd() 
{
	if (head == NULL) return;

	if (head->next == NULL) 
	{
		delete head;
		head = NULL;
		return;
	}

	List* temp = head;
	while (temp->next->next != NULL)
		temp = temp->next;

	delete temp->next;
	temp->next = NULL;
}

void RemoveByKey()
{
	int key;
	cout << "Enter value to delete: ";
	cin >> key;

	List* temp = head;
	List* prev = NULL;

	while (temp != NULL) 
	{
		if (temp->x == key) 
		{
			if (prev == NULL) 
			{
				head = temp->next;
				delete temp;
				temp = head;
			}
			else 
			{
				prev->next = temp->next;
				delete temp;
				temp = prev->next;
			}
		}
		else 
		{
			prev = temp;
			temp = temp->next;
		}
	}
}

void AddBegin() 
{
	int value;
	cout << "Enter value: ";
	cin >> value;

	List* temp = new List;
	temp->x = value;
	temp->next = head;
	head = temp;
}

void AddEnd()
{
	int value;
	cout << "Enter value: ";
	cin >> value;

	List* temp = new List;
	temp->x = value;
	temp->next = NULL;

	if (head == NULL)
	{
		head = temp;
		return;
	}

	List* t = head;
	while (t->next != NULL)
		t = t->next;

	t->next = temp;
}

void AddByKey()
{
	int key, value;
	cout << "Enter key: ";
	cin >> key;

	cout << "Enter value to insert: ";
	cin >> value;

	List* temp = head;

	while (temp != NULL) 
	{
		if (temp->x == key) 
		{
			List* newNode = new List;
			newNode->x = value;

			newNode->next = temp->next;
			temp->next = newNode;
			return;
		}
		temp = temp->next;
	}

	cout << "Key not found!\n";
}

void FreeList() 
{
	while (head != NULL) 
	{
		List* temp = head;
		head = head->next;
		delete temp;
	}
}

int main() 
{

	int choice;

	do {
		cout << "\nMENU:\n";
		cout << "1 - Create list\n";
		cout << "2 - Display list\n";
		cout << "3 - Remove from begin\n";
		cout << "4 - Remove by key\n";
		cout << "5 - Remove from end\n";
		cout << "6 - Add to begin\n";
		cout << "7 - Add to end\n";
		cout << "8 - Add by key\n";
		cout << "9 - Exit\n";

		cin >> choice;

		switch (choice)
		{
		case 1: CreateList(); break;
		case 2: DisplayList(); break;
		case 3: RemoveBegin(); break;
		case 4: RemoveByKey(); break;
		case 5: RemoveEnd(); break;
		case 6: AddBegin(); break;
		case 7: AddEnd(); break;
		case 8: AddByKey(); break;
		case 9: FreeList(); break;
		default: cout << "Error!\n";
		}

	} while (choice != 9);

}
