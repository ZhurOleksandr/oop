#include <iostream>
#include <string>

using namespace std;

struct Node
{
	string data;
	Node* next;
};

Node* createList() 
{
	Node* head = NULL;
	Node* tail = NULL;

	int n;
	cout << "Enter number of elements: ";
	cin >> n;

	for (int i = 0; i < n; i++) 
	{
		Node* temp = new Node;

		cout << "Enter string: ";
		cin>>temp->data;

		temp->next = NULL;

		if (head == NULL) {
			head = tail = temp;
		}
		else {
			tail->next = temp;
			tail = temp;
		}
	}

	return head;
}

void printList(Node* head)
{
	if (head == NULL)
	{
		cout << "List is empty\n";
		return;
	}

	Node* temp = head;

	cout << "List:\n";
	while (temp != NULL)
	{
		cout<<temp->data << endl;
		temp = temp->next;
	}
}
int main()
{
	Node* head = createList();
	printList(head);
}
