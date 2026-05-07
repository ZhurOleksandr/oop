#include <iostream>
#include <vector>

class Equation {
public:
	virtual void solve() = 0;   // віртуальна функція
	virtual ~Equation() = default;
};

class Linear : public Equation {
	double a, b;
public:
	Linear(double aa, double bb) : a(aa), b(bb) {}
	void solve() override {
		if (a == 0) std::cout << "Не рівняння\n";
		else std::cout << "x = " << -b / a << "\n";
	}
};

class Quadratic : public Equation {
	double a, b, c;
public:
	Quadratic(double aa, double bb, double cc) : a(aa), b(bb), c(cc) {}
	void solve() override {
		double d = b * b - 4 * a*c;
		if (d < 0) std::cout << "Немає коренів\n";
		else {
			std::cout << "x1 = " << (-b + sqrt(d)) / (2 * a) << "\n";
			std::cout << "x2 = " << (-b - sqrt(d)) / (2 * a) << "\n";
		}
	}
};

int main() {
	std::vector<Equation*> eqs;
	eqs.push_back(new Linear(2, -4));
	eqs.push_back(new Quadratic(1, -3, 2));

	for (auto e : eqs) {
		e->solve();   // пізнє зв’язування
		delete e;
	}
}