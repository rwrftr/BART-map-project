import datetime
import tkinter
import sv_ttk
from datetime import datetime
from tkinter import ttk
from bart_data import get_train_schedule, get_stop_arrivals, refresh_data, get_all_stops

STOPS_FILE = 'google_transit_20250113-20250808_v10/stops.txt'
FEED_URL   = 'http://api.bart.gov/gtfsrt/tripupdate.aspx'

# Load stops and fetch the feed
stops, feed, nextByTrain, allStops = refresh_data(STOPS_FILE, FEED_URL)  # process the feed and stops
prevFunction = None

def showOutput(text, currentFunction = prevFunction):
    # display output in the text box
    outputBox.config(state='normal')  # Make it editable
    outputBox.delete(1.0, 'end')  # Clear previous content
    outputBox.insert('end', text)  # Insert new content
    outputBox.config(state='disabled')  # Make it read-only again
    
    # update prevFunction global var
    global prevFunction
    prevFunction = currentFunction

def refreshBtnClick():
    print("Refreshing data...")
    global stops, feed, nextByTrain, allStops
    stops, feed, nextByTrain, allStops = refresh_data(STOPS_FILE, FEED_URL)  # Refresh the data
    print("Data refreshed successfully.")
    print(f"Loaded {len(stops)} stops and {len(nextByTrain)} trains.\n")
    prevFunction()

def listTrainsBtnClick():
    print("Listing Trains...")
    output = "Train List:\n"

    for trainId, (stopId, minutes) in sorted(nextByTrain.items()):
        stopName = stops.get(stopId, {}).get('name', 'Unknown')
        output += f"Train {trainId} → {stopName} ({stopId}) in {minutes} min\n"

    showOutput(output, listTrainsBtnClick)

def listStopsBtnClick():
    print("Listing Stops...")
    output = "Stop List:\n"

    listOfStops = get_all_stops(feed, stops)
    
    for stopName in sorted(listOfStops):
        parentStation = listOfStops[stopName]['parent_station']
        stopId = listOfStops[stopName]['stop_id']
        output += f"{stopName} ({stopId}) - Parent Station: {parentStation}\n"
    
    showOutput(output, listStopsBtnClick)

def byTrainBtnClick(trainId):
    schedule = get_train_schedule(feed, stops, trainId)  # Example train ID

    output = f'Schedule for trip ID {trainId} as of {datetime.now().strftime("%I:%M %p")}: \n'
    if not schedule:
        output += f"No schedule found for train {trainId}."
    else:
        for stopName, stopId, minutes in schedule:
            output += f"{stopId} ({stopName}) in {minutes} min\n"

    showOutput(output, lambda: byTrainBtnClick(trainId))

def byStopBtnClick(stopName):
    arrivals = get_stop_arrivals(feed, stops, stopName)  # Example stop ID

    output = f'Arrivals for {stopName} as of {datetime.now().strftime("%I:%M %p")}:\n'
    if not arrivals:
        output += f"No arrivals found for stop {stopName}."
    else:
        for trainId, minutes, stopId, stopName in arrivals:
            output += f"Train {trainId} at {stopName} ({stopId}) in {minutes} min\n"
    
    showOutput(output, lambda: byStopBtnClick(stopName))

def createButtons(buttonsFrame, buttonsList):
    # refresh
    refreshButton = ttk.Button(buttonsFrame, text="refresh")
    refreshButton.config(command=lambda: refreshBtnClick())
    refreshButton.grid(row=1, column=0, padx=5, pady=9, sticky='ew')
    buttonsList.append(refreshButton)

    # list trains
    listTrainsButton = ttk.Button(buttonsFrame, text="list trains")
    listTrainsButton.config(command=lambda: listTrainsBtnClick())
    listTrainsButton.grid(row=2, column=0, padx=5, pady=9, sticky='ew')
    buttonsList.append(listTrainsButton)

    # list stops
    listStopsButton = ttk.Button(buttonsFrame, text="list stops")
    listStopsButton.config(command=lambda: listStopsBtnClick())
    listStopsButton.grid(row=3, column=0, padx=5, pady=9, sticky='ew')
    buttonsList.append(listStopsButton)
    
    # create train and stop dropdowns
    createDropdowns(buttonsFrame, buttonsList)  # Create dropdowns and their buttons

    # exit
    exitButton = ttk.Button(buttonsFrame, text="exit")
    exitButton.config(command=lambda: root.quit())
    exitButton.grid(row=8, column=0, padx=5, pady=9, sticky='ew')
    buttonsList.append(exitButton)

def createDropdowns(buttonsFrame, buttonsList):
    # Create see train button
    trainList = [f"see train: {trainId}" for trainId in sorted(nextByTrain.keys())]
    trainDropdown = ttk.Combobox(buttonsFrame, values=trainList, state='readonly')
    trainDropdown.grid(row=len(buttonsList)+1, column=0, padx=5, pady=9, sticky='ew')  # Place trains dropdown in grid
    selectTrainButton = ttk.Button(buttonsFrame, text="see train", command=lambda: byTrainBtnClick(trainDropdown.get().split(': ')[1]))
    selectTrainButton.grid(row=len(buttonsList)+2, column=0, padx=5, pady=9, sticky='ew')  # Place test button in grid
    buttonsList.append(trainDropdown)
    buttonsList.append(selectTrainButton)

    # create see stop button
    stopList = [f"see stop: {stopId}" for stopId in sorted(allStops)]
    stopDropdown = ttk.Combobox(buttonsFrame, values=stopList, state='readonly')
    stopDropdown.grid(row=len(buttonsList)+1, column=0, padx=5, pady=9, sticky='ew')  # Place stop dropdown in grid
    selectStopButton = ttk.Button(buttonsFrame, text="see stop", command=lambda: byStopBtnClick(stopDropdown.get().split(': ')[1]))
    selectStopButton.grid(row=len(buttonsList)+2, column=0, padx=5, pady=9, sticky='ew')  # Place stop button in grid
    buttonsList.append(stopDropdown)
    buttonsList.append(selectStopButton)

if __name__ == "__main__":
    # create the main application window
    root = tkinter.Tk()
    root.geometry("1024x768")
    root.title("SV TTK Example")

    # create all the buttons
    buttonsList = []
    buttonsFrame = ttk.Frame(root) 
    buttonsFrame.pack(side='left', padx=10, pady=10, fill='y', expand=True)

    buttonLabel = ttk.Label(buttonsFrame, text="Viewer Controls: ")
    buttonLabel.grid(row=0, column=0, padx=5, pady=5, sticky='ew')  # Place label in grid
    
    createButtons(buttonsFrame, buttonsList)  # Create buttons

    # create the output box
    outputFrame = ttk.Frame(root)
    outputFrame.pack(side='right', padx=10, pady=10, fill='both', expand=True)

    label = ttk.Label(outputFrame, text="Output: ")
    label.pack(padx=10, pady=5)

    global outputBox  # Make outputBox accessible in onClick
    outputBox = tkinter.Text(outputFrame, width=100, height=50)
    outputBox.pack(padx=10, pady=10, fill='both', expand=True)
    outputBox.config(state='disabled')  # Make it read-only

    # Set the theme
    sv_ttk.set_theme("dark")
    root.mainloop()