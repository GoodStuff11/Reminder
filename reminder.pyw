from tkinter import Tk, ttk
import tkinter as tk
from datetime import datetime
import sys

class window(tk.Frame):
    def __init__(self, master,filename):
        self.filename = filename
        self.index = -1
        tk.Frame.__init__(self, master=master)

        master.minsize(width=300, height=200)
        master.resizable(width=0, height=0)
        self.master = master
        self.master.title("Reminder")
        self.tree = ttk.Treeview(master, selectmode='browse')

        vsb = ttk.Scrollbar(master, orient="vertical", command=self.tree.yview)
        vsb.place(x=485, y=25, height=200)

        self.tree.configure(yscrollcommand=vsb.set)

        self.tree["columns"] = ('due', 'notes', 'dates')
        self.tree['displaycolumns'] = ('due', 'notes')
        self.tree.column("due", width=100)
        self.tree.heading("due", text='Due date')
        self.tree.column("notes", width=200)
        self.tree.heading("notes", text='notes')

        self.on_open()

        self.popup_menu = tk.Menu(master, tearoff=0)
        self.popup_menu.add_command(label="Insert", command=self.insert)
        self.popup_menu.add_command(label="Modify Item", command=self.modify)
        self.popup_menu.add_command(label="Delete Item", command=self.delete)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Collapse All", command=self.collapse)
        self.popup_menu.add_command(label="Expand All", command=self.expand)

        master.bind("<ButtonRelease-3>", self.popup)
        master.bind("<ButtonPress-1>", self.deselect)

        self.tree.pack()

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def collapse(self):
        self._open('', False)

    def expand(self):
        self._open('', True)

    @staticmethod
    def displayDueDate(YMD):
        try:
            days = int((datetime.strptime(YMD, '%y/%m/%d') - datetime.now()).days) + 1
            if days >= 2:
                return "Due in " + str(days) + " days"
            elif days == 1:
                return "Due tomorrow"
            elif days == 0:
                return "Due today"
            elif days == -1:
                return "Due yesterday"
            elif days <= -2:
                return "Due " + str(abs(days)) + " days ago"
        except ValueError:
            return ''

    def _open(self, item, open):
        for child in self.tree.get_children(item):
            self.tree.item(child, open=open)
            self._open(child, open)

    def deselect(self, event):

        if not self.tree.identify_row(event.y):
            print("NOT SELECTED")
            for i in self.tree.selection():
                self.tree.selection_remove(i)
        else:
            print(self.tree.identify_row(event.y))

    def popup(self, event):
        try:
            self.popup_menu.tk_popup(event.x_root + 50, event.y_root + 30, 1)
        finally:
            self.popup_menu.grab_release()

    def on_open(self):
        try:
            file = open(self.filename, 'r')
            file.readline()
            items = []
            initial_i = -1
            for line in file.readlines():
                info = line[:-1].split(',')

                due = self.displayDueDate(info[3])

                if initial_i == -1:
                    initial_i = int(info[0])
                if info[1] == '':
                    items.append(self.tree.insert('', info[0], text=info[2], values=(due, info[4], info[3]), open=True))
                else:
                    items.append(self.tree.insert(items[int(info[1]) - initial_i], info[0], text=info[2], values=(due, info[4], info[3]), open=True))
        except FileNotFoundError:
            print("No existing file to read from")

    def on_closing(self):
        file = open(self.filename, 'w+')
        file.write('item_index,parent_index,text,date,notes\n')

        self._write_children(file)
        file.close()
        self.master.destroy()

    def _write_children(self, file, parent='', parent_index=''):
        for item in self.tree.get_children(parent):
            self.index += 1
            file.write(str(self.index) + ',' + str(parent_index) + ',' + self.tree.item(item, 'text') + ',' + self.tree.set(item, 2) + ',' + self.tree.set(item, 1) + '\n')
            self._write_children(file, item, self.index)
        return

    def modify(self):
        try:
            item = self.tree.selection()[0]

            popup = Tk()
            popup.config(padx=8, pady=5)

            def close_window():
                self.tree.item(item, text=name.get())

                self.tree.set(item, 2, date.get())
                self.tree.set(item, 0, self.displayDueDate(date.get()))

                self.tree.set(item, 1, notes.get())
                popup.destroy()  # find better way

            def set_text(e, text):
                e.delete(0, tk.END)
                e.insert(0, text)
                return

            name = tk.Entry(popup)
            set_text(name, self.tree.item(item, 'text'))
            date = tk.Entry(popup)

            set_text(date, self.tree.set(item, 2))

            notes = tk.Entry(popup)
            set_text(notes, self.tree.set(item, 1))
            exit = tk.Button(popup, text='Modify', command=close_window)

            ttk.Label(popup, text="Modify Item").grid(row=0, column=0, columnspan=2)
            ttk.Label(popup, text="Item name").grid(sticky=tk.W, row=1, column=0)
            ttk.Label(popup, text="Due date").grid(sticky=tk.W, row=2, column=0)
            ttk.Label(popup, text="notes").grid(sticky=tk.W, row=3, column=0)

            name.grid(row=1, sticky=tk.E, column=1)
            date.grid(row=2, sticky=tk.E, column=1)
            notes.grid(row=3, sticky=tk.E, column=1)

            exit.grid(row=4, columnspan=2)
            exit.config(width=10)
        except IndexError:
            return

    def insert(self):
        selection = self.tree.selection()
        self.index += 1
        if len(selection) == 0:
            self.tree.insert("", 0, text='<empty>')
        else:
            self.tree.item(selection[0], open=True)
            self.tree.insert(selection[0], 0, text='<empty>')

    def delete(self):
        try:
            self.tree.delete(self.tree.selection()[0])
        except IndexError:
            pass


if __name__ == "__main__":
    root = Tk()
    root.iconbitmap('Reminder.ico')
    window(root, sys.argv[1])
    root.mainloop()
