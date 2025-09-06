import tkinter as tk  
from tkinter import ttk, messagebox
from datetime import datetime
import calendar
from PIL import Image, ImageTk
import mysql.connector

# ---------------- MySQL Connection ----------------
mycon = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="d1"
)
cursor = mycon.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS TO_DO (
        task_date DATE,
        task_text VARCHAR(255),
        status VARCHAR(10)
    )
""")

# ---------------- Main Window ----------------
root = tk.Tk()
root.title("Calendar To-Do Planner")
root.geometry("500x550")
root.resizable(False, False)

img = Image.open(r"C:\\Users\\Lenovo\\OneDrive\\Pictures\\Saved Pictures\\to.PNG").resize((580, 580))
final_img = ImageTk.PhotoImage(img)

labelx = tk.Label(root, image=final_img)
labelx.image = final_img
labelx.place(x=20, y=20)

month_var = tk.StringVar()
year_var = tk.StringVar()

months = list(calendar.month_name)[1:]
current_year = datetime.now().year

month_menu = ttk.Combobox(root, textvariable=month_var, values=months, state="readonly")
month_menu.set(months[datetime.now().month - 1])
month_menu.place(x=30, y=30)

year_menu = ttk.Combobox(root, textvariable=year_var, values=[str(y) for y in range(current_year, current_year + 10)], state="readonly")
year_menu.set(str(current_year))
year_menu.place(x=200, y=30)

cal_frame = tk.Frame(root)
cal_frame.place(x=30, y=80)

today = datetime.today()
date_buttons = {}
done_dates = set()

# ---------------- Show Hooray Frame ----------------
def show_hooray_screen(year, month, day):
    global task_img,ftask_img,back


    framex = tk.Frame(root, bg="white", width=500, height=550)
    framex.place(x=0, y=0)



    task_img = Image.open(r"C:\Users\Lenovo\OneDrive\Pictures\Saved Pictures\horray.jpg").resize((500, 546))
    ftask_img = ImageTk.PhotoImage(task_img)
    back = tk.Label(framex, image=ftask_img)
    back.image = ftask_img
    back.place(x=0,y=0)


    # tk.Text is the upgraded verison of Entry. You can Easily costomize it's width and height.
    # tk.Entry doesn't have option to resize width and height
    task_list = tk.Text(framex, height=24, width=29, font=("Arial",14), bd=2, relief="solid")
    task_list.place(x=160, y=10)

    task_list.tag_configure("heading", font=("Arial", 18, "bold"))
    task_list.tag_configure("body", font=("Arial", 14))

    task_list.insert("end", "      ____TASKS LIST____\n\n", "heading")

    def des():
        framex.destroy()

    destroy_framex = tk.Button(framex, text="Back", fg="#0F0C0C", bg="#FF1C1C", width=10, command=des, font="Arial 9 bold")
    destroy_framex.place(x=395, y=510)

    try:
        commandx = f"Select * from task_{day}_{month}_{year};"
        cursor.execute(commandx)
        data = cursor.fetchall()
        count = 0
        for row in data:
            count+=1
            task_list.insert("end", f"  TASK {count}: {row[0]}\n\n", "body")
        task_list.configure(state="disabled")
    except Exception as e:
        messagebox.showerror("ERROR", f"{e}")
    
    
    framex.mainloop()

# ---------------- Draw Calendar ----------------
def draw_calendar():
    for widget in cal_frame.winfo_children():
        widget.destroy()

    month = months.index(month_var.get()) + 1
    year = int(year_var.get())
    cal = calendar.monthcalendar(year, month)

    tk.Label(cal_frame, text="Mo Tu We Th Fr Sa Su", font="Arial 10 bold").grid(row=0, column=0, columnspan=7)

    for i, week in enumerate(cal):
        for j, day in enumerate(week):
            if day == 0:
                continue
            key = (year, month, day)
            is_past = datetime(year, month, day) < today.replace(hour=0, minute=0, second=0, microsecond=0)

            btn_color = "light grey" if is_past else "sky blue"
            btn_state = "normal"

            cursor.execute("SELECT COUNT(*) FROM TO_DO WHERE task_date=%s AND status='done'", (f"{year}-{month:02}-{day:02}",))
            if cursor.fetchone()[0] > 0:
                btn_color = "green"
                done_dates.add(key)

            btn = tk.Button(cal_frame, text=str(day), bg=btn_color, width=4, state=btn_state)

            if key in done_dates:
                btn.config(command=lambda y=year, m=month, d=day: show_hooray_screen(y, m, d))
            else:
                btn.config(command=lambda y=year, m=month, d=day, b=btn: open_todo_window(y, m, d, b))

            btn.grid(row=i+1, column=j, padx=2, pady=2)
            date_buttons[key] = btn

# ---------------- To-Do Window ----------------
def open_todo_window(year, month, day, date_btn):
    key = (year, month, day)
    is_past_date = datetime(year, month, day) < today.replace(hour=0, minute=0, second=0, microsecond=0)

    todo_win = tk.Toplevel(root)
    todo_win.title(f"To-Do List for {day}-{month}-{year}")
    todo_win.geometry("400x500")
    todo_win.configure(bg="gray")

    task_entry = None
    tasks = []
    task_y = 70
    break_mode = [False]

    canvas = tk.Canvas(todo_win, bg="white")
    canvas.pack(fill="both", expand=True)
    canvas.bind("<Button-1>", lambda e: show_entry(e))

    def show_entry(event):
        nonlocal task_entry, task_y
        if break_mode[0] or is_past_date:
            return
        task_entry = tk.Entry(todo_win, font=("Arial", 12))
        canvas.create_window(100, task_y, window=task_entry, anchor="w")
        task_entry.focus()
        task_entry.bind("<Return>", save_task)

    def save_task(event):
        nonlocal task_y
        task_text = task_entry.get()

        cursor.execute(f"CREATE TABLE IF NOT EXISTS task_{day}_{month}_{year}(TASK_DONE VARCHAR(255));")
        cursor.execute(f"INSERT INTO task_{day}_{month}_{year} (TASK_DONE) VALUES (%s)", (task_text,))
        mycon.commit()

        if task_text:
            var = tk.IntVar()
            cb = tk.Checkbutton(canvas, variable=var, bg="white")
            canvas.create_window(30, task_y, window=cb, anchor="w")
            label = tk.Label(canvas, text=task_text, font=("Arial", 12), bg="white")
            canvas.create_window(60, task_y, window=label, anchor="w")
            tasks.append((cb, label))

            cursor.execute("INSERT INTO TO_DO (task_date, task_text, status) VALUES (%s, %s, %s)",
                           (f"{year}-{month:02}-{day:02}", task_text, "pending"))
            mycon.commit()
            task_y += 30

    def done_for_day():
        cursor.execute("UPDATE TO_DO SET status = 'done' WHERE task_date = %s", (f"{year}-{month:02}-{day:02}",))
        mycon.commit()
        done_dates.add(key)

        date_btn.configure(command=lambda: show_hooray_screen(year, month, day), text="\u2714 Done", bg="green", fg="white")
        todo_win.destroy()
        draw_calendar()

    tk.Button(todo_win, text="Break", command=lambda: break_mode.__setitem__(0, True)).pack(side="left", padx=10, pady=10)
    tk.Button(todo_win, text="Resume", command=lambda: break_mode.__setitem__(0, False)).pack(side="left", padx=10, pady=10)
    tk.Button(todo_win, text="Done For The Day", command=done_for_day).pack(side="right", padx=10, pady=10)

    if is_past_date:
        for child in todo_win.winfo_children():
            if isinstance(child, tk.Button):
                child.config(state="disabled")

    cursor.execute("SELECT task_text, status FROM TO_DO WHERE task_date = %s", (f"{year}-{month:02}-{day:02}",))
    tasks_from_db = cursor.fetchall()
    for task_text, status in tasks_from_db:
        if task_text:
            var = tk.IntVar(value=1 if status == "done" else 0)
            cb = tk.Checkbutton(canvas, variable=var, bg="white")
            canvas.create_window(30, task_y, window=cb, anchor="w")
            label = tk.Label(canvas, text=task_text, font=("Arial", 12), bg="white")
            canvas.create_window(60, task_y, window=label, anchor="w")
            tasks.append((cb, label))
            task_y += 30

# ---------------- Event Bindings ----------------
draw_calendar()
month_menu.bind("<<ComboboxSelected>>", lambda e: draw_calendar())
year_menu.bind("<<ComboboxSelected>>", lambda e: draw_calendar())

root.mainloop()