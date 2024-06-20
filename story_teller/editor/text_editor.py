import tkinter as tk
from tkinter import messagebox
from pymongo import MongoClient

from tkinter import simpledialog
import urllib.parse
import tkinter.font as tkFont


# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client.story_teller
collection = db["posts"]

# Function to load data from MongoDB
def load_data(post_id):
    post = collection.find_one({"post_id": post_id})
    if post:
        text_vietnamese.delete("1.0", tk.END)
        text_english.delete("1.0", tk.END)
        text_vietnamese.insert(tk.END, urllib.parse.unquote(post.get("body_vn", "")))
        text_english.insert(tk.END, post.get("body", ""))
        entry_post_id.delete(0, tk.END)
        entry_post_id.insert(0, post.get("post_id", ""))
        entry_post_title.delete(0, tk.END)
        entry_post_title.insert(0, post.get("title", ""))
    else:
        messagebox.showerror("Error", "Post not found")

# Function to submit data to MongoDB
def submit_data():
    post_id = entry_post_id.get()
    title = entry_post_title.get()
    vietnamese_text = urllib.parse.quote(text_vietnamese.get("1.0", tk.END).strip())
    english_text = text_english.get("1.0", tk.END).strip()
    
    post_data = {
        "post_id": post_id,
        "title": title,
        "body_vn": vietnamese_text,
        "body": english_text
    }
    
    collection.update_one({"post_id": post_id}, {"$set": post_data}, upsert=True)
    messagebox.showinfo("Success", "Data written to MongoDB")

# Function to open the post selection window
def open_post_selection_window():
    post_selection_window = tk.Toplevel(root)
    post_selection_window.title("Select Post")
    post_selection_window.geometry("400x400")

    posts = collection.find({"status": 1})
    post_listbox = tk.Listbox(post_selection_window, font=font, width=50, height=20)
    post_listbox.pack(padx=10, pady=10)

    for post in posts:
        post_listbox.insert(tk.END, f"{post['post_id']}: {post['title']}")

    def on_post_select(event):
        selected_post = post_listbox.get(post_listbox.curselection())
        post_id = selected_post.split(":")[0].strip()
        load_data(post_id)
        post_selection_window.destroy()

    post_listbox.bind('<<ListboxSelect>>', on_post_select)

# Create the main window
root = tk.Tk()
root.title("Text Editor")
root.geometry("1200x800")  # Set the window size

# Set font
font = tkFont.Font(name="Iosevka Nerd Font", size=16)

# Layout widgets
tk.Label(root, text="Post ID", font=font).grid(row=0, column=0, padx=10, pady=10)
entry_post_id = tk.Entry(root, font=font)
entry_post_id.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Post Title", font=font).grid(row=0, column=2, padx=10, pady=10)
entry_post_title = tk.Entry(root, font=font)
entry_post_title.grid(row=0, column=3, padx=10, pady=10)

tk.Label(root, text="body_vn", font=font).grid(row=1, column=0, columnspan=2, padx=10, pady=10)
tk.Label(root, text="body", font=font).grid(row=1, column=2, columnspan=2, padx=10, pady=10)

text_vietnamese = tk.Text(root, height=25, width=50, font=font)
text_vietnamese.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

text_english = tk.Text(root, height=25, width=50, font=font)
text_english.grid(row=2, column=2, columnspan=2, padx=10, pady=10)

btn_load = tk.Button(root, text="Load", command=lambda: load_data(entry_post_id.get()), font=font)
btn_load.grid(row=3, column=0, padx=10, pady=10)

btn_submit = tk.Button(root, text="Submit", command=submit_data, font=font)
btn_submit.grid(row=3, column=1, padx=10, pady=10)

btn_open_menu = tk.Button(root, text="Open Menu", command=open_post_selection_window, font=font)
btn_open_menu.grid(row=3, column=2, columnspan=2, padx=10, pady=10)

# Start the main event loop
root.mainloop()