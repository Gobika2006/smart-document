import os
import shutil
import datetime
from tkinter import *
from tkinter import filedialog, messagebox, scrolledtext
from PyPDF2 import PdfReader
from docx import Document

# --- Keyword Loading ---
def load_keywords(filename):
    if not os.path.exists(filename):
        return set()
    with open(filename, 'r') as f:
        return set(line.strip().lower() for line in f)

important_keywords = load_keywords("important_keywords.txt")
junk_keywords = load_keywords("junk_keywords.txt")

# --- Text Extraction ---
def extract_text(file_path):
    try:
        if file_path.endswith(".pdf"):
            reader = PdfReader(file_path)
            return " ".join([page.extract_text() or "" for page in reader.pages])
        elif file_path.endswith(".docx"):
            doc = Document(file_path)
            return " ".join([para.text for para in doc.paragraphs])
        elif file_path.endswith(".txt"):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    except:
        return ""
    return ""

# --- Organize Files ---
def organize_documents(folder_path):
    output_box.delete("1.0", END)  # clear old results
    if not os.path.isdir(folder_path):
        messagebox.showerror("Error", "Invalid folder selected.")
        return

    categorized_folder = os.path.join(os.getcwd(), "categorized")
    os.makedirs(categorized_folder, exist_ok=True)

    count = 0

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            filepath = os.path.join(root, file)
            if not file.lower().endswith(('.pdf', '.docx', '.txt')):
                continue

            text = extract_text(filepath).lower()
            destination = "uncategorized"

            if any(word in text for word in important_keywords):
                destination = "important"
            elif any(word in text for word in junk_keywords):
                destination = "junk"

            category_path = os.path.join(categorized_folder, destination)
            os.makedirs(category_path, exist_ok=True)
            shutil.copy(filepath, os.path.join(category_path, file))

            output_box.insert(END, f"📄 {file} ➜ {destination}\n")
            count += 1

    status_label.config(text=f"✅ Organized {count} files.")
    if count == 0:
        output_box.insert(END, "No documents found to organize.\n")

# --- Browse Folder ---
def browse_folder():
    folder = filedialog.askdirectory()
    folder_entry.delete(0, END)
    folder_entry.insert(0, folder)
    status_label.config(text="📂 Folder selected. Ready to organize.")
    output_box.delete("1.0", END)

# --- GUI Setup ---
window = Tk()
window.title("📁 Smart Document Organizer")
window.geometry("700x500")
window.resizable(False, False)

Label(window, text="📁 Select Folder to Organize:", font=("Arial", 12)).pack(pady=10)
folder_entry = Entry(window, width=70, font=("Arial", 10))
folder_entry.pack()

Button(window, text="Browse", command=browse_folder, width=15).pack(pady=5)
Button(window, text="Organize Documents", command=lambda: organize_documents(folder_entry.get()), width=20, bg="green", fg="white").pack(pady=10)

status_label = Label(window, text="", fg="blue", font=("Arial", 10))
status_label.pack(pady=5)

Label(window, text="🧾 Results:", font=("Arial", 11)).pack()
output_box = scrolledtext.ScrolledText(window, width=80, height=15, font=("Courier", 10))
output_box.pack(pady=10)

window.mainloop()
