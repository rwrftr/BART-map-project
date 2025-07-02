import tkinter
import sv_ttk
from tkinter import ttk
from bart_data import load_stops, fetch_feed, prepare_data, get_train_schedule, get_stop_arrivals, refresh_data

def onClick(btn):
    textcontent = btn.cget("text")
    print(textcontent + " Button clicked!")

    if textcontent == 'refresh':
        print("Refreshing data...")
    elif textcontent == 'list trains':
        print("Listing Trains...")


    elif textcontent == 'list stops':
        print("Listing Stops...")
    elif textcontent == 'exit':
        print("Exiting Application...")

def show_output(text):
    # Function to display output in the text box
    outputBox.config(state='normal') # Make it editable
    outputBox.delete(1.0, 'end') # Clear previous content
    outputBox.insert('end', text) # Insert new content
    outputBox.config(state='disabled') # Make it read-only again


if __name__ == "__main__":
    # create the main application window
    root = tkinter.Tk()
    root.geometry("500x500")
    root.title("SV TTK Example")

    #create all the buttons
    buttonLabelsList = ["refresh", "list trains", "list stops", "exit"]
    buttonsList = []
    for i, label in enumerate(buttonLabelsList):
        button = ttk.Button(root, text=label)
        button.config(command=lambda btn=button: onClick(btn))
        button.grid(row=i, column=0, padx=10, pady=10, sticky="ew")
        buttonsList.append(button)
        root.grid_rowconfigure(i, weight=1)  # Evenly distribute button rows

    # Output label in column 1
    label = ttk.Label(root, text="Output: ")
    label.grid(row=0, column=1, padx=10, pady=10, sticky="nw")

    # Output text box in column 1
    outputBox = tkinter.Text(root, width=40, height=20)
    outputBox.grid(row=1, column=1, rowspan=len(buttonLabelsList), padx=10, pady=10, sticky="n")
    outputBox.config(state='disabled')  # Make it read-only

    root.grid_columnconfigure(0, weight=0)  # Buttons column
    root.grid_columnconfigure(1, weight=1)  # Output column

    sv_ttk.set_theme("dark")
    root.mainloop()