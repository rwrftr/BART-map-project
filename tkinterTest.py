import tkinter
import sv_ttk
from tkinter import ttk
from bart_data import load_stops, fetch_feed, prepare_data, get_train_schedule, get_stop_arrivals, refresh_data, get_all_stops

stops = load_stops() # a dictionary of stops
feed = fetch_feed() # a FeedMessage object
next_by_train, by_stop = prepare_data(feed, stops) # process the feed and stops
all_stops = get_all_stops(feed, stops)  # Get all stops with predictions

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
    
    elif textcontent == 'list stops':
        print("Listing Stops...")
        output = "Stop List:\n"

        list_of_stops = get_all_stops(feed, stops)
        
        for stop_name in sorted(list_of_stops):
            parent_station = list_of_stops[stop_name]['parent_station']
            stop_id = list_of_stops[stop_name]['stop_id']
            output += f"{stop_name} ({stop_id}) - Parent Station: {parent_station}\n"
        
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

def by_train(train_id):
    
    schedule = get_train_schedule(feed, stops, train_id)  # Example train ID

    output = 'Train Schedule:\n'
    if not schedule:
        output += f"No schedule found for train {train_id}."
    else:
        for stop_name, stop_id, minutes in schedule:
            output += f"{stop_id} ({stop_name}) in {minutes} min\n"

    show_output(output)

def by_stop(stop_name):
    arrivals = get_stop_arrivals(feed, stops, stop_name)  # Example stop ID

    output = 'Stop Arrivals:\n'
    if not arrivals:
        output += f"No arrivals found for stop {stop_name}."
    else:
        for train_id, minutes, stop_id, stop_name in arrivals:
            output += f"Train {train_id} at {stop_name} ({stop_id}) in {minutes} min\n"
    

    show_output(output)

def create_buttons(buttonsFrame):

    # refresh
    # list trains
    # list stops
    # exit
    
    button = ttk.Button(buttonsFrame, text=label)
    button.config(command=lambda btn=button: onClick(btn))
    button.grid(row=i+1, column=0, padx=5, pady=9, sticky='ew')  # Place button in grid
    buttonsList.append(button)


    pass

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
    
    # Create see train button
    trainList = [f"see train: {train_id}" for train_id in sorted(next_by_train.keys())]
    trainDropdown = ttk.Combobox(buttonsFrame, values=trainList, state='readonly')
    trainDropdown.grid(row=len(buttonsList)+1, column=0, padx=5, pady=9, sticky='ew')  # Place trains dropdown in grid
    selectTrainButton = ttk.Button(buttonsFrame, text="see train", command= lambda: by_train(trainDropdown.get().split(': ')[1]))
    selectTrainButton.grid(row=len(buttonsList)+2, column=0, padx=5, pady=9, sticky='ew')  # Place test button in grid

    # create see stop button
    stopList = [f"see stop: {stop_id}" for stop_id in sorted(all_stops)]
    stopDropdown = ttk.Combobox(buttonsFrame, values=stopList, state='readonly')
    stopDropdown.grid(row=len(buttonsList)+3, column=0, padx=5, pady=9, sticky='ew')  # Place stop dropdown in grid
    selectStopButton = ttk.Button(buttonsFrame, text="see stop", command= lambda: by_stop(stopDropdown.get().split(': ')[1]))
    selectStopButton.grid(row=len(buttonsList)+4, column=0, padx=5, pady=9, sticky='ew')  # Place stop button in grid

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