import tkinter
import sv_ttk
from tkinter import ttk
from bart_data import load_stops, fetch_feed, prepare_data, get_train_schedule, get_stop_arrivals, refresh_data, get_all_stops

stops = load_stops()  # a dictionary of stops
feed = fetch_feed()  # a FeedMessage object
nextByTrain, byStop = prepare_data(feed, stops)  # process the feed and stops
allStops = get_all_stops(feed, stops)  # Get all stops with predictions

def onClick(btn):
    textContent = btn.cget("text")
    print(textContent + " Button clicked!")

    if textContent == 'refresh':
        print("Refreshing data...")
        # stops = load_stops()  # Reload stops
        # feed = fetch_feed()  # Fetch the latest feed
        # nextByTrain, byStop = prepare_data(feed, stops)  # Prepare data again
        # output = "Data refreshed successfully.\n"
        
    elif textContent == 'list trains':
        print("Listing Trains...")
        output = "Train List:\n"

        for trainId, (stopId, minutes) in sorted(nextByTrain.items()):
            stopName = stops.get(stopId, {}).get('name', 'Unknown')
            output += f"Train {trainId} → {stopName} ({stopId}) in {minutes} min\n"

        showOutput(output)
    
    elif textContent == 'list stops':
        print("Listing Stops...")
        output = "Stop List:\n"

        listOfStops = get_all_stops(feed, stops)
        
        for stopName in sorted(listOfStops):
            parentStation = listOfStops[stopName]['parent_station']
            stopId = listOfStops[stopName]['stop_id']
            output += f"{stopName} ({stopId}) - Parent Station: {parentStation}\n"
        
        showOutput(output)
        
    elif textContent == 'exit':
        print("Exiting Application...")
        root.quit()
        return

def showOutput(text):
    # Function to display output in the text box
    outputBox.config(state='normal')  # Make it editable
    outputBox.delete(1.0, 'end')  # Clear previous content
    outputBox.insert('end', text)  # Insert new content
    outputBox.config(state='disabled')  # Make it read-only again

def byTrain(trainId):
    schedule = get_train_schedule(feed, stops, trainId)  # Example train ID

    output = 'Train Schedule:\n'
    if not schedule:
        output += f"No schedule found for train {trainId}."
    else:
        for stopName, stopId, minutes in schedule:
            output += f"{stopId} ({stopName}) in {minutes} min\n"

    showOutput(output)

def byStop(stopName):
    arrivals = get_stop_arrivals(feed, stops, stopName)  # Example stop ID

    output = 'Stop Arrivals:\n'
    if not arrivals:
        output += f"No arrivals found for stop {stopName}."
    else:
        for trainId, minutes, stopId, stopName in arrivals:
            output += f"Train {trainId} at {stopName} ({stopId}) in {minutes} min\n"
    
    showOutput(output)

def createButtons(buttonsFrame, buttonsList):
    # refresh
    refreshButton = ttk.Button(buttonsFrame, text="refresh")
    refreshButton.config(command=lambda btn=refreshButton: onClick(btn))
    refreshButton.grid(row=1, column=0, padx=5, pady=9, sticky='ew')
    buttonsList.append(refreshButton)

    # list trains
    listTrainsButton = ttk.Button(buttonsFrame, text="list trains")
    listTrainsButton.config(command=lambda btn=listTrainsButton: onClick(btn))
    listTrainsButton.grid(row=2, column=0, padx=5, pady=9, sticky='ew')
    buttonsList.append(listTrainsButton)

    # list stops
    listStopsButton = ttk.Button(buttonsFrame, text="list stops")
    listStopsButton.config(command=lambda btn=listStopsButton: onClick(btn))
    listStopsButton.grid(row=3, column=0, padx=5, pady=9, sticky='ew')
    buttonsList.append(listStopsButton)
    
    # exit
    exitButton = ttk.Button(buttonsFrame, text="exit")
    exitButton.config(command=lambda btn=exitButton: onClick(btn))
    exitButton.grid(row=4, column=0, padx=5, pady=9, sticky='ew')
    buttonsList.append(exitButton)

def createDropdowns(buttonsFrame, buttonsList):
    pass

if __name__ == "__main__":
    # create the main application window
    root = tkinter.Tk()
    root.geometry("1024x768")  # Set the window size
    root.title("SV TTK Example")

    # create all the buttons
    buttonsList = []
    buttonsFrame = ttk.Frame(root)
    buttonsFrame.pack(side='left', padx=10, pady=10, fill='y', expand=True)

    buttonLabel = ttk.Label(buttonsFrame, text="Viewer Controls: ")
    buttonLabel.grid(row=0, column=0, padx=5, pady=5, sticky='ew')  # Place label in grid
    
    createButtons(buttonsFrame, buttonsList)  # Create buttons

    # Create see train button
    trainList = [f"see train: {trainId}" for trainId in sorted(nextByTrain.keys())]
    trainDropdown = ttk.Combobox(buttonsFrame, values=trainList, state='readonly')
    trainDropdown.grid(row=len(buttonsList)+1, column=0, padx=5, pady=9, sticky='ew')  # Place trains dropdown in grid
    selectTrainButton = ttk.Button(buttonsFrame, text="see train", command=lambda: byTrain(trainDropdown.get().split(': ')[1]))
    selectTrainButton.grid(row=len(buttonsList)+2, column=0, padx=5, pady=9, sticky='ew')  # Place test button in grid

    # create see stop button
    stopList = [f"see stop: {stopId}" for stopId in sorted(allStops)]
    stopDropdown = ttk.Combobox(buttonsFrame, values=stopList, state='readonly')
    stopDropdown.grid(row=len(buttonsList)+3, column=0, padx=5, pady=9, sticky='ew')  # Place stop dropdown in grid
    selectStopButton = ttk.Button(buttonsFrame, text="see stop", command=lambda: byStop(stopDropdown.get().split(': ')[1]))
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