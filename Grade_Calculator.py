import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

class GradeCalculator:
    def __init__(self, root):
        self.root = root
        root.title("Grade Calculator")

        self.categories = {}
        self.current_course = None

        self.frame = ttk.Frame(root, padding=10)
        self.frame.grid(row=0, column=0)

        # Course management
        ttk.Button(self.frame, text="Save Course", command=self.save_course).grid(row=0, column=0, pady=5)
        ttk.Button(self.frame, text="Load Course", command=self.load_course).grid(row=0, column=1, pady=5)

        # Category section
        ttk.Label(self.frame, text="Category Name:").grid(row=1, column=0, sticky="w")
        self.cat_name = ttk.Entry(self.frame)
        self.cat_name.grid(row=1, column=1)

        ttk.Label(self.frame, text="Weight (%):").grid(row=2, column=0, sticky="w")
        self.cat_weight = ttk.Entry(self.frame)
        self.cat_weight.grid(row=2, column=1)

        ttk.Button(self.frame, text="Add Category", command=self.add_category).grid(row=3, column=0, columnspan=2, pady=5)
        ttk.Button(self.frame, text="Edit Category", command=self.edit_category).grid(row=4, column=0, columnspan=2, pady=5)

        # Treeview
        self.tree = ttk.Treeview(self.frame)
        self.tree["columns"] = ("col2", "col3")
        self.tree.heading("col2", text="Weight / Avg")
        self.tree.heading("col3", text="Score")
        self.tree.column("col3", width=80)
        self.tree.grid(row=5, column=0, columnspan=2, pady=10)

        # Assignment section
        ttk.Label(self.frame, text="Assignment Name:").grid(row=6, column=0, sticky="w")
        self.assign_name = ttk.Entry(self.frame)
        self.assign_name.grid(row=6, column=1)

        ttk.Label(self.frame, text="Score (%):").grid(row=7, column=0, sticky="w")
        self.assign_score = ttk.Entry(self.frame)
        self.assign_score.grid(row=7, column=1)

        ttk.Button(self.frame, text="Add Assignment", command=self.add_assignment).grid(row=8, column=0, columnspan=2, pady=5)
        ttk.Button(self.frame, text="Edit Assignment", command=self.edit_assignment).grid(row=9, column=0, columnspan=2, pady=5)
        ttk.Button(self.frame, text="Remove Selected", command=self.remove_selected).grid(row=10, column=0, columnspan=2, pady=5)

        ttk.Button(self.frame, text="Calculate Final Grade", command=self.calculate_final).grid(row=11, column=0, columnspan=2, pady=10)

    # ---------------- COURSE SAVE / LOAD ----------------

    def save_course(self):
        data = self.categories
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if file:
            with open(file, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Saved", "Course saved successfully!")

    def load_course(self):
        file = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not file:
            return
        with open(file, "r") as f:
            self.categories = json.load(f)

        # Refresh treeview
        self.tree.delete(*self.tree.get_children())
        for cat, data in self.categories.items():
            self.tree.insert("", "end", iid=cat, text=cat, values=(f"{data['weight']}%", "--"))
            for i, (aname, ascore) in enumerate(data["assignments"], start=1):
                cid = f"{cat}_{i}"
                self.tree.insert(cat, "end", iid=cid, text=aname, values=("", f"{ascore:.2f}"))
            self.update_category_display(cat)

    # ---------------- CATEGORY HANDLING ----------------

    def add_category(self):
        name = self.cat_name.get().strip()
        try:
            weight = float(self.cat_weight.get())
        except:
            messagebox.showerror("Error", "Weight must be numeric.")
            return
        if not name:
            messagebox.showerror("Error", "Category must have a name.")
            return
        if name in self.categories:
            messagebox.showerror("Error", "Duplicate category.")
            return

        self.categories[name] = {"weight": weight, "assignments": []}
        self.tree.insert("", "end", iid=name, text=name, values=(f"{weight}%", "--"))

        self.cat_name.delete(0, tk.END)
        self.cat_weight.delete(0, tk.END)

    def edit_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a category to edit.")
            return
        cat = selected[0]
        if cat not in self.categories:
            messagebox.showerror("Error", "You must select a category, not an assignment.")
            return

        new_name = self.cat_name.get().strip()
        try:
            new_weight = float(self.cat_weight.get())
        except:
            messagebox.showerror("Error", "Weight must be numeric.")
            return

        if new_name != cat and new_name in self.categories:
            messagebox.showerror("Error", "Category name already exists.")
            return

        # Update data
        data = self.categories.pop(cat)
        data["weight"] = new_weight
        self.categories[new_name] = data

        # Update tree
        children = self.tree.get_children(cat)
        self.tree.delete(cat)
        self.tree.insert("", "end", iid=new_name, text=new_name, values=(f"{new_weight}%", "--"))
        for child in children:
            self.tree.move(child, new_name, "end")

        self.update_category_display(new_name)

    # ---------------- ASSIGNMENT HANDLING ----------------

    def add_assignment(self):
        name = self.assign_name.get().strip()
        try:
            score = float(self.assign_score.get())
        except:
            messagebox.showerror("Error", "Score must be numeric.")
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a category to add assignments.")
            return

        cat = selected[0]
        if cat not in self.categories:
            messagebox.showerror("Error", "You must select a category, not an assignment.")
            return

        self.categories[cat]["assignments"].append((name, score))
        cid = f"{cat}_{len(self.categories[cat]['assignments'])}"
        self.tree.insert(cat, "end", iid=cid, text=name, values=("", f"{score:.2f}"))

        self.update_category_display(cat)

        self.assign_name.delete(0, tk.END)
        self.assign_score.delete(0, tk.END)

    def edit_assignment(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select an assignment to edit.")
            return

        node = selected[0]
        parent = self.tree.parent(node)
        if parent not in self.categories:
            messagebox.showerror("Error", "Select a valid assignment.")
            return

        # New values
        new_name = self.assign_name.get().strip()
        try:
            new_score = float(self.assign_score.get())
        except:
            messagebox.showerror("Error", "Score must be numeric.")
            return

        # Update backing data
        assignments = self.categories[parent]["assignments"]
        old_name = self.tree.item(node, "text")
        old_score = float(self.tree.item(node, "values")[1])
        assignments.remove((old_name, old_score))
        assignments.append((new_name, new_score))

        # Update tree
        self.tree.item(node, text=new_name, values=("", f"{new_score:.2f}"))

        self.update_category_display(parent)

    # ---------------- REMOVAL AND DISPLAY ----------------

    def remove_selected(self):
        selected = self.tree.selection()
        if not selected:
            return

        node = selected[0]
        if node in self.categories:
            del self.categories[node]
            self.tree.delete(node)
            return

        parent = self.tree.parent(node)
        if parent in self.categories:
            name = self.tree.item(node, "text")
            score = float(self.tree.item(node, "values")[1])
            self.categories[parent]["assignments"].remove((name, score))
            self.tree.delete(node)
            self.update_category_display(parent)

    def update_category_display(self, cat):
        assignments = self.categories[cat]["assignments"]
        if assignments:
            avg = sum(s for _, s in assignments) / len(assignments)
            self.tree.item(cat, values=(f"{self.categories[cat]['weight']}%", f"{avg:.2f}"))
        else:
            self.tree.item(cat, values=(f"{self.categories[cat]['weight']}%", "--"))

    # ---------------- GRADE CALC ----------------

    def calculate_final(self):
        final = 0
        total_weight = 0
        for cat, data in self.categories.items():
            w = data["weight"] / 100
            total_weight += w
            if data["assignments"]:
                avg = sum(s for _, s in data["assignments"]) / len(data["assignments"])
                final += avg * w
        if abs(total_weight - 1) > 1e-6:
            messagebox.showwarning("Warning", "Total weight does not sum to 100%.")
        messagebox.showinfo("Final Grade", f"Your final grade is: {final:.2f}%")

if __name__ == "__main__":
    root = tk.Tk()
    app = GradeCalculator(root)
    root.mainloop()