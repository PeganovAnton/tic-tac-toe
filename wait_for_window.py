from tkinter import *
from tkinter.messagebox import *
root = Tk()
val = 0
val2 = 0

def op1():

    global e, l, root, val, e2, b, new
    try:
        val = int(e.get())
    except ValueError:
        showerror("Error", "Enter an int")
    else:
        new = Toplevel()
        e2 = Entry(new)
        e2.pack(side = LEFT)
        b2 = Button(new, text = "OK", command = op2)
        b2.pack(side = RIGHT)
        l2 = Label(new, text = "Enter new number to multiply %d by" %val)
        l2.pack()
        e2.focus_force()
        root.wait_window(new)
        for i in range(5):
            print (i + 1)

def op2():
    global val
    try:
        val2 = int(e2.get())
    except ValueError:
        showerror("Error", "Enter an int")
        e2.focus_force()
    else:
        val = val * val2
        l.config(text = "This is your total: %d Click OK to exit" %val)
        new.destroy()
        b.config(command = op3)
def op3():
    root.destroy()

e = Entry(root)
e.pack(side = LEFT)
b = Button(root, text = "OK", command = op1)
b.pack(side = RIGHT)
l = Label(root, text = "Enter a number")
l.pack()
root.mainloop()