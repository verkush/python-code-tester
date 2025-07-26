import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import unittest
import importlib.util
import os
import sys
import datetime
import ast

APP_TITLE = "🐍 Python Code Tester"
TEST_TEMPLATE = "templates/test_template.py"
REPORT_DIR = "reports"
TEST_CASE_FILE = "tests/test_cases.py"

os.makedirs(REPORT_DIR, exist_ok=True)

class CodeTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("750x600")
        self.root.configure(bg="#f9f9f9")

        self.setup_widgets()
        self.student_file_path = ""
        self.test_results = ""

    def setup_widgets(self):
        tk.Label(self.root, text=APP_TITLE, font=("Helvetica", 20, "bold"), bg="#f9f9f9", fg="#333").pack(pady=15)

        tk.Button(self.root, text="📂 Select Python File", command=self.select_file, bg="#4CAF50", fg="white",
                  font=("Arial", 11, "bold"), relief="flat", width=25).pack(pady=5)

        tk.Button(self.root, text="🛠️ Generate Tests Automatically", command=self.generate_test_code, bg="#2196F3", fg="white",
                  font=("Arial", 11, "bold"), relief="flat", width=25).pack(pady=5)

        self.run_button = tk.Button(self.root, text="▶️ Run Tests", command=self.run_tests, state=tk.DISABLED,
                                    bg="#FF9800", fg="white", font=("Arial", 11, "bold"), relief="flat", width=25)
        self.run_button.pack(pady=5)

        tk.Button(self.root, text="💾 Export Report", command=self.export_report, bg="#9C27B0", fg="white",
                  font=("Arial", 11, "bold"), relief="flat", width=25).pack(pady=5)

        self.result_box = scrolledtext.ScrolledText(self.root, width=85, height=25, font=("Courier", 10), bg="#fff")
        self.result_box.pack(padx=10, pady=10)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if path:
            self.student_file_path = path
            self.run_button.config(state=tk.NORMAL)
            self.result_box.insert(tk.END, f"✅ Selected file: {os.path.basename(path)}\n\n")

    def parse_functions_safely(self):
        with open(self.student_file_path, 'r') as file:
            node = ast.parse(file.read(), filename=self.student_file_path)
        return [n.name for n in node.body if isinstance(n, ast.FunctionDef)]

    def generate_test_code(self):
        if not self.student_file_path:
            messagebox.showwarning("Warning", "Please select a Python file first.")
            return

        try:
            with open(self.student_file_path, "r") as f:
                tree = ast.parse(f.read())

            test_code = "import unittest\nimport student_script\n\nclass TestStudentFunctions(unittest.TestCase):\n"
            for node in tree.body:
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    arg_count = len(node.args.args)
                    dummy_args = ", ".join("1" for _ in range(arg_count)) or "1"

                    test_code += f"""
    def test_{func_name}(self):
        try:
            result = student_script.{func_name}({dummy_args})
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail("Function {func_name} crashed: " + str(e))\n"""

            with open(TEST_CASE_FILE, "w") as f:
                f.write(test_code)

            self.result_box.insert(tk.END, "✅ Test cases generated successfully!\n\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))


    def run_tests(self):
        try:
            self.result_box.delete(1.0, tk.END)

            if "student_script" in sys.modules:
                del sys.modules["student_script"]

            spec = importlib.util.spec_from_file_location("student_script", self.student_file_path)
            student_module = importlib.util.module_from_spec(spec)
            sys.modules["student_script"] = student_module
            spec.loader.exec_module(student_module)

            suite = unittest.defaultTestLoader.discover('tests', pattern='test_cases.py')
            buffer = self.TextRedirector(self.result_box)
            result = unittest.TextTestRunner(stream=buffer, verbosity=2).run(suite)

            score = result.testsRun - len(result.failures) - len(result.errors)
            summary = f"\n📊 Score: {score}/{result.testsRun}\n  ✅ Passed: {score}\n  ❌ Failed: {len(result.failures)}\n  🛑 Errors: {len(result.errors)}\n"
            self.result_box.insert(tk.END, summary)
            self.test_results = self.result_box.get("1.0", tk.END)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_report(self):
        if not self.test_results:
            messagebox.showwarning("Warning", "No results to export.")
            return

        filename = os.path.join(REPORT_DIR, f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(filename, "w") as f:
            f.write(self.test_results)

        messagebox.showinfo("Success", f"Report saved to:\n{filename}")

    class TextRedirector:
        def __init__(self, widget):
            self.widget = widget

        def write(self, text):
            self.widget.insert(tk.END, text)
            self.widget.see(tk.END)

        def flush(self):
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = CodeTesterApp(root)
    root.mainloop()