import tkinter
import sv_ttk
from tkinter import ttk
from bart_data import load_stops, fetch_feed, prepare_data, get_train_schedule, get_stop_arrivals, refresh_data
stops = load_stops() # a dictionary of stops
feed = fetch_feed() # a FeedMessage object
next_by_train, by_stop = prepare_data(feed, stops) # process the feed and stops


def onClick(btn):
    textcontent = btn.cget("text")
    print(textcontent + " Button clicked!")

    if textcontent == 'refresh':
        print("Refreshing data...")
        
    elif textcontent == 'list trains':
        print("Listing Trains...")
        output = "Train List:\n"

        for train_id, (stop_id, minutes) in sorted(next_by_train.items()):
            stop_name = stops.get(stop_id, {}).get('name', 'Unknown')
            output += f"Train {train_id} → {stop_name} ({stop_id}) in {minutes} min\n"

        show_output(output)
    
    elif textcontent == 'list stops':
        print("Listing Stops...")
        output = "Stop List:\n"

        parent_stations = set()

        for stop_id in sorted(by_stop):
            stop_name = stops.get(stop_id, {}).get('name', 'Unknown')
            parent_station = stops.get(stop_id, {}).get('parent_station', 'None')

            
    elif textcontent == 'exit':
        print("Exiting Application...")
        root.quit()
        return

def show_output(text):
    # Function to display output in the text box
    outputBox.config(state='normal') # Make it editable
    outputBox.delete(1.0, 'end') # Clear previous content
    outputBox.insert('end', text) # Insert new content
    outputBox.config(state='disabled') # Make it read-only again

def testButton():

    print("Data fetched successfully.")

    # Sort stops by parent station, or by stop_id if no parent station
    sorted_by_parent_stop = sorted(stops.items(), key=lambda x: x[1]['parent_station'] or x[0]) 
    
    output = 'Stops sorted by parent station:\n'
    print(f"Stops sorted by parent station: {len(sorted_by_parent_stop)} stops found.")
    
    # Calculate the longest name and parent station lengths for formatting
    # This is used to align the output columns
    longest_name_length = max(len(stop_info['name']) for stop_info in stops.values())
    longest_parent_length = max(len(stop_info['parent_station']) for stop_info in stops.values() if stop_info['parent_station'])
    
    for stop_id, stop_info in sorted_by_parent_stop:
        # Format the output string with aligned columns
        namestr = (stop_info['name'] + ',').ljust(longest_name_length)
        parentstr = (stop_info['parent_station'] + ',').ljust(longest_parent_length) 
        printstr = (f"Name: {namestr} Parent Station: {parentstr} Stop ID: {stop_id}, Code: {stop_info['code']}, Platform Code: {stop_info['platform_code']}")
        
        print(printstr)
        output = output + (printstr + '\n')

    show_output(output)

if __name__ == "__main__":
    # create the main application window
    root = tkinter.Tk()
    root.geometry("1024x768")  # Set the window size
    root.title("SV TTK Example")

    #create all the buttons
    buttonLabelsList = ["refresh", "list trains", "list stops", "exit"]
    buttonsList = []
    buttonsFrame = ttk.Frame(root)
    buttonsFrame.pack(side='left', padx=10, pady=10, fill='y', expand=True)

    buttonLabel = ttk.Label(buttonsFrame, text="Viewer Controls: ")
    buttonLabel.grid(row=0, column=0, padx=5, pady=5, sticky='ew')  # Place label in grid

    # Create buttons dynamically based on buttonLabelsList
    for i, label in enumerate(buttonLabelsList):
        button = ttk.Button(buttonsFrame, text=label)
        button.config(command=lambda btn=button: onClick(btn))
        button.grid(row=i+1, column=0, padx=5, pady=9, sticky='ew')  # Place button in grid
        buttonsList.append(button)
        #root.grid_rowconfigure(i, weight=1)  # Evenly distribute button rows
    
    # Create a test button
    testBtn = ttk.Button(buttonsFrame, text="Test Button", command=testButton)
    testBtn.grid(row=len(buttonsList)+1, column=0, padx=5, pady=9, sticky='ew')  # Place test button in grid
    
    # Create a frame for output
    
    outputFrame = ttk.Frame(root)
    outputFrame.pack(side='right', padx=10, pady=10, fill='both', expand=True)

    # Output label
    label = ttk.Label(outputFrame, text="Output: ")
    label.pack(padx=10, pady=5)

    # Create a text box for output
    global outputBox  # Make outputBox accessible in onClick
    outputBox = tkinter.Text(outputFrame, width=100, height=100)
    outputBox.pack(padx=10, pady=10, fill='both', expand=True)
    outputBox.config(state='disabled')  # Make it read-only

    # root.grid_columnconfigure(0, weight=0)  # Buttons column
    # root.grid_columnconfigure(1, weight=1)  # Output column

    sv_ttk.set_theme("dark")
    root.mainloop()