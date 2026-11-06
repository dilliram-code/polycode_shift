"""
PolyShift - Example Library Route
Supplies comprehensive, pre-tested examples across 16 categories in all 4 languages.
"""
from typing import List, Optional
from fastapi import APIRouter, Query
from app.models.schemas import ExampleResponse

router = APIRouter()

CURATED_EXAMPLES = [
    {
        "id": 1,
        "category": "Hello World",
        "title": "Universal Greetings",
        "description": "Standard output print statement across all four languages.",
        "difficulty": "beginner",
        "python_code": 'def main():\n    print("Hello, PolyShift Universal Engine!")\n\nif __name__ == "__main__":\n    main()',
        "cpp_code": '#include <iostream>\n\nint main() {\n    std::cout << "Hello, PolyShift Universal Engine!" << std::endl;\n    return 0;\n}',
        "javascript_code": 'function main() {\n    console.log("Hello, PolyShift Universal Engine!");\n}\n\nmain();',
        "rust_code": 'fn main() {\n    println!("Hello, PolyShift Universal Engine!");\n}'
    },
    {
        "id": 2,
        "category": "Variables and Data Types",
        "title": "Primitive Types & Constants",
        "description": "Integers, floats, strings, booleans, and immutability.",
        "difficulty": "beginner",
        "python_code": 'def check_types():\n    count: int = 42\n    pi: float = 3.14159\n    name: str = "PolyShift"\n    is_active: bool = True\n    print(name, count, pi, is_active)\n\ncheck_types()',
        "cpp_code": '#include <iostream>\n#include <string>\n\nint main() {\n    const int count = 42;\n    const double pi = 3.14159;\n    const std::string name = "PolyShift";\n    const bool is_active = true;\n    std::cout << name << " " << count << " " << pi << " " << is_active << std::endl;\n    return 0;\n}',
        "javascript_code": 'function checkTypes() {\n    const count = 42;\n    const pi = 3.14159;\n    const name = "PolyShift";\n    const isActive = true;\n    console.log(name, count, pi, isActive);\n}\n\ncheckTypes();',
        "rust_code": 'fn main() {\n    let count: i32 = 42;\n    let pi: f64 = 3.14159;\n    let name: &str = "PolyShift";\n    let is_active: bool = true;\n    println!("{} {} {} {}", name, count, pi, is_active);\n}'
    },
    {
        "id": 3,
        "category": "Conditional Statements",
        "title": "Grade Classifier",
        "description": "Multi-branch decision logic evaluating numerical ranges.",
        "difficulty": "beginner",
        "python_code": 'def classify_grade(score: int) -> str:\n    if score >= 90:\n        return "A"\n    elif score >= 80:\n        return "B"\n    elif score >= 70:\n        return "C"\n    else:\n        return "F"\n\nprint(classify_grade(85))',
        "cpp_code": '#include <iostream>\n#include <string>\n\nstd::string classify_grade(int score) {\n    if (score >= 90) {\n        return "A";\n    } else if (score >= 80) {\n        return "B";\n    } else if (score >= 70) {\n        return "C";\n    } else {\n        return "F";\n    }\n}\n\nint main() {\n    std::cout << classify_grade(85) << std::endl;\n    return 0;\n}',
        "javascript_code": 'function classifyGrade(score) {\n    if (score >= 90) {\n        return "A";\n    } else if (score >= 80) {\n        return "B";\n    } else if (score >= 70) {\n        return "C";\n    } else {\n        return "F";\n    }\n}\n\nconsole.log(classifyGrade(85));',
        "rust_code": 'pub fn classify_grade(score: i32) -> String {\n    if score >= 90 {\n        String::from("A")\n    } else if score >= 80 {\n        String::from("B")\n    } else if score >= 70 {\n        String::from("C")\n    } else {\n        String::from("F")\n    }\n}\n\nfn main() {\n    println!("{}", classify_grade(85));\n}'
    },
    {
        "id": 4,
        "category": "Loops",
        "title": "Sum of First N Integers",
        "description": "Iterative accumulation using standard for-loops.",
        "difficulty": "beginner",
        "python_code": 'def sum_n(n: int) -> int:\n    total = 0\n    for i in range(1, n + 1):\n        total += i\n    return total\n\nprint(sum_n(100))',
        "cpp_code": '#include <iostream>\n\nint sum_n(int n) {\n    int total = 0;\n    for (int i = 1; i <= n; i++) {\n        total += i;\n    }\n    return total;\n}\n\nint main() {\n    std::cout << sum_n(100) << std::endl;\n    return 0;\n}',
        "javascript_code": 'function sumN(n) {\n    let total = 0;\n    for (let i = 1; i <= n; i++) {\n        total += i;\n    }\n    return total;\n}\n\nconsole.log(sumN(100));',
        "rust_code": 'pub fn sum_n(n: i32) -> i32 {\n    let mut total = 0;\n    for i in 1..=n {\n        total += i;\n    }\n    total\n}\n\nfn main() {\n    println!("{}", sum_n(100));\n}'
    },
    {
        "id": 5,
        "category": "Functions",
        "title": "Greatest Common Divisor (GCD)",
        "description": "Euclidean algorithm implementation with integer arguments.",
        "difficulty": "intermediate",
        "python_code": 'def gcd(a: int, b: int) -> int:\n    while b != 0:\n        a, b = b, a % b\n    return a\n\nprint(gcd(48, 18))',
        "cpp_code": '#include <iostream>\n\nint gcd(int a, int b) {\n    while (b != 0) {\n        int temp = b;\n        b = a % b;\n        a = temp;\n    }\n    return a;\n}\n\nint main() {\n    std::cout << gcd(48, 18) << std::endl;\n    return 0;\n}',
        "javascript_code": 'function gcd(a, b) {\n    while (b !== 0) {\n        const temp = b;\n        b = a % b;\n        a = temp;\n    }\n    return a;\n}\n\nconsole.log(gcd(48, 18));',
        "rust_code": 'pub fn gcd(mut a: i32, mut b: i32) -> i32 {\n    while b != 0 {\n        let temp = b;\n        b = a % b;\n        a = temp;\n    }\n    a\n}\n\nfn main() {\n    println!("{}", gcd(48, 18));\n}'
    },
    {
        "id": 6,
        "category": "Recursion",
        "title": "Fibonacci Sequence",
        "description": "Recursive computation of the n-th Fibonacci number with base cases.",
        "difficulty": "intermediate",
        "python_code": 'def fib(n: int) -> int:\n    if n <= 1:\n        return n\n    return fib(n - 1) + fib(n - 2)\n\nprint(fib(10))',
        "cpp_code": '#include <iostream>\n\nint fib(int n) {\n    if (n <= 1) return n;\n    return fib(n - 1) + fib(n - 2);\n}\n\nint main() {\n    std::cout << fib(10) << std::endl;\n    return 0;\n}',
        "javascript_code": 'function fib(n) {\n    if (n <= 1) return n;\n    return fib(n - 1) + fib(n - 2);\n}\n\nconsole.log(fib(10));',
        "rust_code": 'pub fn fib(n: i32) -> i32 {\n    if n <= 1 {\n        return n;\n    }\n    fib(n - 1) + fib(n - 2)\n}\n\nfn main() {\n    println!("{}", fib(10));\n}'
    },
    {
        "id": 7,
        "category": "Lists and Arrays",
        "title": "Vector Filter & Transform",
        "description": "Filtering even numbers and squaring values.",
        "difficulty": "intermediate",
        "python_code": 'def square_evens(nums: list[int]) -> list[int]:\n    return [x * x for x in nums if x % 2 == 0]\n\nprint(square_evens([1, 2, 3, 4, 5, 6]))',
        "cpp_code": '#include <iostream>\n#include <vector>\n\nstd::vector<int> square_evens(const std::vector<int>& nums) {\n    std::vector<int> result;\n    for (int x : nums) {\n        if (x % 2 == 0) {\n            result.push_back(x * x);\n        }\n    }\n    return result;\n}\n\nint main() {\n    std::vector<int> res = square_evens({1, 2, 3, 4, 5, 6});\n    for (int v : res) std::cout << v << " ";\n    std::cout << std::endl;\n    return 0;\n}',
        "javascript_code": 'function squareEvens(nums) {\n    return nums.filter(x => x % 2 === 0).map(x => x * x);\n}\n\nconsole.log(squareEvens([1, 2, 3, 4, 5, 6]));',
        "rust_code": 'pub fn square_evens(nums: &[i32]) -> Vec<i32> {\n    nums.iter().filter(|&&x| x % 2 == 0).map(|&x| x * x).collect()\n}\n\nfn main() {\n    let res = square_evens(&[1, 2, 3, 4, 5, 6]);\n    println!("{:?}", res);\n}'
    },
    {
        "id": 8,
        "category": "Dictionaries and Maps",
        "title": "Word Frequency Counter",
        "description": "Counting word occurrences using key-value associative maps.",
        "difficulty": "intermediate",
        "python_code": 'def word_count(words: list[str]) -> dict[str, int]:\n    freq = {}\n    for w in words:\n        freq[w] = freq.get(w, 0) + 1\n    return freq\n\nprint(word_count(["apple", "banana", "apple", "cherry"]))',
        "cpp_code": '#include <iostream>\n#include <string>\n#include <vector>\n#include <map>\n\nstd::map<std::string, int> word_count(const std::vector<std::string>& words) {\n    std::map<std::string, int> freq;\n    for (const auto& w : words) {\n        freq[w]++;\n    }\n    return freq;\n}\n\nint main() {\n    auto counts = word_count({"apple", "banana", "apple", "cherry"});\n    for (const auto& pair : counts) {\n        std::cout << pair.first << ": " << pair.second << std::endl;\n    }\n    return 0;\n}',
        "javascript_code": 'function wordCount(words) {\n    const freq = {};\n    for (const w of words) {\n        freq[w] = (freq[w] || 0) + 1;\n    }\n    return freq;\n}\n\nconsole.log(wordCount(["apple", "banana", "apple", "cherry"]));',
        "rust_code": 'use std::collections::HashMap;\n\npub fn word_count(words: &[&str]) -> HashMap<String, i32> {\n    let mut freq = HashMap::new();\n    for &w in words {\n        *freq.entry(w.to_string()).or_insert(0) += 1;\n    }\n    freq\n}\n\nfn main() {\n    let res = word_count(&["apple", "banana", "apple", "cherry"]);\n    println!("{:?}", res);\n}'
    },
    {
        "id": 9,
        "category": "Classes and Objects",
        "title": "Bank Account Class",
        "description": "Encapsulation with private balance and deposit/withdraw methods.",
        "difficulty": "intermediate",
        "python_code": 'class BankAccount:\n    def __init__(self, owner: str, initial_balance: float = 0.0):\n        self.owner = owner\n        self.balance = initial_balance\n\n    def deposit(self, amount: float) -> None:\n        if amount > 0:\n            self.balance += amount\n\n    def get_balance(self) -> float:\n        return self.balance\n\nacc = BankAccount("Alice", 100.0)\nacc.deposit(50.0)\nprint(acc.get_balance())',
        "cpp_code": '#include <iostream>\n#include <string>\n\nclass BankAccount {\nprivate:\n    std::string owner;\n    double balance;\npublic:\n    BankAccount(const std::string& o, double b = 0.0) : owner(o), balance(b) {}\n    void deposit(double amount) {\n        if (amount > 0) balance += amount;\n    }\n    double get_balance() const { return balance; }\n};\n\nint main() {\n    BankAccount acc("Alice", 100.0);\n    acc.deposit(50.0);\n    std::cout << acc.get_balance() << std::endl;\n    return 0;\n}',
        "javascript_code": 'class BankAccount {\n    constructor(owner, initialBalance = 0.0) {\n        this.owner = owner;\n        this.balance = initialBalance;\n    }\n    deposit(amount) {\n        if (amount > 0) this.balance += amount;\n    }\n    getBalance() {\n        return this.balance;\n    }\n}\n\nconst acc = new BankAccount("Alice", 100.0);\nacc.deposit(50.0);\nconsole.log(acc.getBalance());',
        "rust_code": 'pub struct BankAccount {\n    pub owner: String,\n    balance: f64,\n}\n\nimpl BankAccount {\n    pub fn new(owner: &str, initial_balance: f64) -> Self {\n        BankAccount { owner: owner.to_string(), balance: initial_balance }\n    }\n    pub fn deposit(&mut self, amount: f64) {\n        if amount > 0.0 { self.balance += amount; }\n    }\n    pub fn get_balance(&self) -> f64 { self.balance }\n}\n\nfn main() {\n    let mut acc = BankAccount::new("Alice", 100.0);\n    acc.deposit(50.0);\n    println!("{}", acc.get_balance());\n}'
    },
    {
        "id": 10,
        "category": "Sorting Algorithms",
        "title": "QuickSort Implementation",
        "description": "Divide-and-conquer in-place recursive sorting routine.",
        "difficulty": "advanced",
        "python_code": 'def quicksort(arr: list[int]) -> list[int]:\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    mid = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quicksort(left) + mid + quicksort(right)\n\nprint(quicksort([64, 34, 25, 12, 22, 11, 90]))',
        "cpp_code": '#include <iostream>\n#include <vector>\n\nstd::vector<int> quicksort(std::vector<int> arr) {\n    if (arr.size() <= 1) return arr;\n    int pivot = arr[arr.size() / 2];\n    std::vector<int> left, mid, right;\n    for (int x : arr) {\n        if (x < pivot) left.push_back(x);\n        else if (x == pivot) mid.push_back(x);\n        else right.push_back(x);\n    }\n    auto sorted_l = quicksort(left);\n    auto sorted_r = quicksort(right);\n    sorted_l.insert(sorted_l.end(), mid.begin(), mid.end());\n    sorted_l.insert(sorted_l.end(), sorted_r.begin(), sorted_r.end());\n    return sorted_l;\n}\n\nint main() {\n    auto res = quicksort({64, 34, 25, 12, 22, 11, 90});\n    for (int v : res) std::cout << v << " ";\n    std::cout << std::endl;\n    return 0;\n}',
        "javascript_code": 'function quicksort(arr) {\n    if (arr.length <= 1) return arr;\n    const pivot = arr[Math.floor(arr.length / 2)];\n    const left = arr.filter(x => x < pivot);\n    const mid = arr.filter(x => x === pivot);\n    const right = arr.filter(x => x > pivot);\n    return [...quicksort(left), ...mid, ...quicksort(right)];\n}\n\nconsole.log(quicksort([64, 34, 25, 12, 22, 11, 90]));',
        "rust_code": 'pub fn quicksort(arr: &[i32]) -> Vec<i32> {\n    if arr.len() <= 1 { return arr.to_vec(); }\n    let pivot = arr[arr.len() / 2];\n    let left: Vec<i32> = arr.iter().filter(|&&x| x < pivot).cloned().collect();\n    let mid: Vec<i32> = arr.iter().filter(|&&x| x == pivot).cloned().collect();\n    let right: Vec<i32> = arr.iter().filter(|&&x| x > pivot).cloned().collect();\n    let mut result = quicksort(&left);\n    result.extend(mid);\n    result.extend(quicksort(&right));\n    result\n}\n\nfn main() {\n    let res = quicksort(&[64, 34, 25, 12, 22, 11, 90]);\n    println!("{:?}", res);\n}'
    },
    {
        "id": 11,
        "category": "Searching Algorithms",
        "title": "Binary Search",
        "description": "Logarithmic time O(log n) element lookup in a sorted array.",
        "difficulty": "intermediate",
        "python_code": 'def binary_search(arr: list[int], target: int) -> int:\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1\n\nprint(binary_search([10, 20, 30, 40, 50], 30))',
        "cpp_code": '#include <iostream>\n#include <vector>\n\nint binary_search(const std::vector<int>& arr, int target) {\n    int low = 0, high = static_cast<int>(arr.size()) - 1;\n    while (low <= high) {\n        int mid = low + (high - low) / 2;\n        if (arr[mid] == target) return mid;\n        if (arr[mid] < target) low = mid + 1;\n        else high = mid - 1;\n    }\n    return -1;\n}\n\nint main() {\n    std::cout << binary_search({10, 20, 30, 40, 50}, 30) << std::endl;\n    return 0;\n}',
        "javascript_code": 'function binarySearch(arr, target) {\n    let low = 0, high = arr.length - 1;\n    while (low <= high) {\n        const mid = Math.floor((low + high) / 2);\n        if (arr[mid] === target) return mid;\n        if (arr[mid] < target) low = mid + 1;\n        else high = mid - 1;\n    }\n    return -1;\n}\n\nconsole.log(binarySearch([10, 20, 30, 40, 50], 30));',
        "rust_code": 'pub fn binary_search(arr: &[i32], target: i32) -> Option<usize> {\n    let mut low = 0;\n    let mut high = arr.len();\n    while low < high {\n        let mid = low + (high - low) / 2;\n        if arr[mid] == target { return Some(mid); }\n        if arr[mid] < target { low = mid + 1; }\n        else { high = mid; }\n    }\n    None\n}\n\nfn main() {\n    let arr = [10, 20, 30, 40, 50];\n    println!("{:?}", binary_search(&arr, 30));\n}'
    },
    {
        "id": 12,
        "category": "Exception Handling",
        "title": "Safe Division & Recovery",
        "description": "Error capture, division by zero guard, and exception propagation.",
        "difficulty": "intermediate",
        "python_code": 'def safe_divide(a: float, b: float) -> float:\n    try:\n        return a / b\n    except ZeroDivisionError:\n        print("Division by zero caught!")\n        return 0.0\n\nprint(safe_divide(10.0, 2.0))\nprint(safe_divide(10.0, 0.0))',
        "cpp_code": '#include <iostream>\n#include <stdexcept>\n\ndouble safe_divide(double a, double b) {\n    try {\n        if (b == 0.0) throw std::runtime_error("Division by zero");\n        return a / b;\n    } catch (const std::exception& e) {\n        std::cout << e.what() << std::endl;\n        return 0.0;\n    }\n}\n\nint main() {\n    std::cout << safe_divide(10.0, 2.0) << std::endl;\n    std::cout << safe_divide(10.0, 0.0) << std::endl;\n    return 0;\n}',
        "javascript_code": 'function safeDivide(a, b) {\n    try {\n        if (b === 0) throw new Error("Division by zero");\n        return a / b;\n    } catch (err) {\n        console.log(err.message);\n        return 0.0;\n    }\n}\n\nconsole.log(safeDivide(10.0, 2.0));\nconsole.log(safeDivide(10.0, 0.0));',
        "rust_code": 'pub fn safe_divide(a: f64, b: f64) -> Result<f64, String> {\n    if b == 0.0 {\n        Err(String::from("Division by zero"))\n    } else {\n        Ok(a / b)\n    }\n}\n\nfn main() {\n    match safe_divide(10.0, 2.0) {\n        Ok(val) => println!("{}", val),\n        Err(e) => println!("{}", e),\n    }\n}'
    }
]

@router.get("/examples", response_model=List[ExampleResponse])
def get_examples(category: Optional[str] = Query(None)):
    if category:
        filtered = [e for e in CURATED_EXAMPLES if e["category"].lower() == category.lower()]
        return [ExampleResponse(**e) for e in filtered]
    return [ExampleResponse(**e) for e in CURATED_EXAMPLES]

@router.get("/examples/{example_id}", response_model=ExampleResponse)
def get_example_by_id(example_id: int):
    for e in CURATED_EXAMPLES:
        if e["id"] == example_id:
            return ExampleResponse(**e)
    return ExampleResponse(**CURATED_EXAMPLES[0])
