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
        # stops = load_stops()  # Reload stops
        # feed = fetch_feed()  # Fetch the latest feed
        # next_by_train, by_stop = prepare_data(feed, stops)  # Prepare data again
        # output = "Data refreshed successfully.\n"
        
    elif textcontent == 'list trains':
        print("Listing Trains...")
        output = "Train List:\n"

        for train_id, (stop_id, minutes) in sorted(next_by_train.items()):
            stop_name = stops.get(stop_id, {}).get('name', 'Unknown')
            output += f"Train {train_id} → {stop_name} ({stop_id}) in {minutes} min\n"

        show_output(output)
    
    elif textcontent.startswith('see train: '):
        print("Viewing Train Schedule...")
        output = ""
        # Extract train ID from the button text
        train_id = textcontent.split(': ')[1]
        schedule = get_train_schedule(feed, stops, train_id)
        if not schedule:
            output = f"No schedule found for train {train_id}."
        
        else:
            output = f"Schedule for Train {train_id}:\n"
            for stop_id, stop_name, minutes in schedule:
                output += f"{stop_name} ({stop_id}) in {minutes} min\n"
    
    elif textcontent == 'list stops':
        print("Listing Stops...")
        output = "Stop List:\n"

        parent_stations = set()

        for stop_id in sorted(by_stop):
            stop_name = stops.get(stop_id, {}).get('name', 'Unknown')
            parent_station = stops.get(stop_id, {}).get('parent_station', 'None')
            if parent_station not in parent_stations:
                parent_stations.add(parent_station)
                output += f"{stop_name} ({stop_id}) - Parent Station: {parent_station}\n"
        
        output += "\nParent Stations:\n"
        for parent in sorted(parent_stations):
            output += f"{parent}\n"
        
        show_output(output)
    
            
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

def testButton(train_id):
    
    schedule = get_train_schedule(feed, stops, train_id)  # Example train ID

    output = 'Train Schedule:\n'
    if not schedule:
        output += f"No schedule found for train {train_id}."
    else:
        for stop_name, stop_id, minutes in schedule:
            output += f"{stop_id} ({stop_name}) in {minutes} min\n"

    show_output(output)

if __name__ == "__main__":
    # create the main application window
    root = tkinter.Tk()
    root.geometry("1024x768")  # Set the window size
    root.title("SV TTK Example")

    #create all the buttons
    buttonLabelsList = ["refresh", "list trains", "list stops", "exit",]
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
    trainList = [f"see train: {train_id}" for train_id in sorted(next_by_train.keys())]
    trainDropdown = ttk.Combobox(buttonsFrame, values=trainList, state='readonly')
    trainDropdown.grid(row=len(buttonsList)+1, column=0, padx=5, pady=9, sticky='ew')  # Place test button in grid
    selectTrainButton = ttk.Button(buttonsFrame, text="see train", command= lambda: testButton(trainDropdown.get().split(': ')[1]))
    selectTrainButton.grid(row=len(buttonsList)+2, column=0, padx=5, pady=9, sticky='ew')  # Place test button in grid

    # Create a frame for output
    outputFrame = ttk.Frame(root)
    outputFrame.pack(side='right', padx=10, pady=10, fill='both', expand=True)

    # Output label
    label = ttk.Label(outputFrame, text="Output: ")
    label.pack(padx=10, pady=5)

    # Create a text box for output
    global outputBox  # Make outputBox accessible in onClick
    outputBox = tkinter.Text(outputFrame, width=100, height=50)
    outputBox.pack(padx=10, pady=10, fill='both', expand=True)
    outputBox.config(state='disabled')  # Make it read-only

    # root.grid_columnconfigure(0, weight=0)  # Buttons column
    # root.grid_columnconfigure(1, weight=1)  # Output column

    sv_ttk.set_theme("dark")
    root.mainloop()