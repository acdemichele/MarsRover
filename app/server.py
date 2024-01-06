from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from random import randint
import pandas as pd
from collections import defaultdict
import requests
import json
import hashlib


app = FastAPI()




# Map 

class Map(BaseModel):

  data: pd.DataFrame
  columns: int
  rows: int

  class Config:
    arbitrary_types_allowed = True  


# Mines

class Mines(BaseModel):

  id: int
  xPosition: int
  yPosition: int
  serialNum: int
  defusedOrNot: bool



# Rover

class Rover(BaseModel):

  id: int
  data: str
  roverStatus: str
  xPosition: int
  yPosition: int
  direction: str

minesDB = defaultdict(list)
roversDB = defaultdict(list)


# Functions


#Map - GET: get the map data



@app.get('/map')
def getMap():
   
    map_instance = Map()

    # Read the number of rows and columns from first row of file
    with open("map.txt", "r") as f:
        rows, cols = map(int, f.readline().split())

    map_instance.rows = rows
    map_instance.columns = cols

    # Read the rest of the file to get the actual map
    map_df = pd.read_csv("map.txt", skiprows=1, sep=' ', header=None)
    map_instance.data = map_df

    return map_instance

#Map - PUT: updating the size (height, width) of the field

@app.put('/map')
def fieldUpdate(cols: int, rows: int):
    # Create new DataFrame with new dimensions
    
    map_data = pd.DataFrame(0, index=range(rows), columns=range(cols))
    
    with open("map.txt", "w") as f:
        # writing to the new dimensions to the text file
        f.write(f"{rows} {cols}\n")

        # Write the new map based on the new number of rows and columns
        for _, row in map_data.iterrows():
            f.write(" ".join(str(x) for x in row) + "\n")
    
    return {"The map has been successfully updated."}


#Mines 

#Mines - GET: get the list of all the mines

@app.get('/mines')
def getMinesList():
   return minesDB

#Mines - retrieve a specific mine, returns error if not found

@app.get('/mines/{mine_id}')
def retrieveMine(mine_id: int):
    
    minesList = getMinesList()
    try:
        # Attempt to retrieve the mine from the database
        mine = minesList[mine_id][0]
    except KeyError:
        # Raise an HTTPException with a 404 status code and detail message if mine not found
        raise HTTPException(status_code=404, detail="Mine not found")

    # Return the retrieved mine
    return mine

#Mines - DELETE mine by id

@app.delete('/mines/{mine_id}')
def deleteMine(mine_id: int):
    minesList = getMinesList()
    try:
        # Attempt to delete the mine from the database
        del minesList[mine_id]
    except KeyError:
        # Raise an HTTPException with a 404 status code and detail message if mine not found
        raise HTTPException(status_code=404, detail="Mine not found")

    # Return a success message
    return {"The mine has been successfully deleted."}

#Mines - POST: create a new mine

@app.post('/mines')
def addMine(mine_id: int):
    minesList = getMinesList()
    # Check if mine with same ID already exists
    if mine_id in minesList:
        return {"error": "Mine with the same ID already exists"}

    map_data = getMap()
    xmax = map_data.columns
    ymax = map_data.rows

    # Loop to generate unique coordinates for the new mine
    while True:
        xpos = randint(0, xmax)
        ypos = randint(0, ymax)

        # Check if the generated coordinates already match an existing mine
        exists = False
        for mine in minesList.values():
            if mine.xPosition == xpos and mine.yPosition == ypos:
                exists = True
                break

        if exists:
            continue  # Try generating new coordinates if there's a match

        # Create a new Mine object
        mine_data = Mines()
        mine_data.id = mine_id
        mine_data.xPosition = xpos
        mine_data.yPosition = ypos
        mine_data.serialNum = randint(0, 999)
        minesDB[mine_id].append(mine_data)
        return {"message": f"Mine {mine_id} created successfully"}


#Mines - PUT: update mine

@app.put('/mines/{mine_id}')
def updateMine(mine_id: int):

    try:
        # Check if a mine with the specified ID exists
        if mine_id not in minesDB:
            raise HTTPException(status_code=404, detail="Mine not found")

        mine_data = minesDB[mine_id][0]

        # Check if the mine has already been defused
        if mine_data.defusedOrNot:
            raise HTTPException(status_code=405, detail="Mine defused.")

        map_data = getMap()
        xmax = map_data.columns
        ymax = map_data.rows

        while True:
            xpos = randint(0, xmax)
            ypos = randint(0, ymax)

            # Check if there is already a mine placed at the randomly generated location
            overlap = False
            for mine in minesDB.values():
                if mine.xPosition == xpos and mine.yPosition == ypos:
                    overlap = True
                    break

            if not overlap:
                mine_data.xPosition = xpos
                mine_data.yPosition = ypos
                break

        return {f"Mine with ID: {mine_id} has been updated successfully."}

    except KeyError:
        raise HTTPException(status_code=404, detail="Mine not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


#-------------------------Rover-------------------------#



# Retrieve the list of all rovers, GET

@app.get('/rovers')
def getRoversList():
    return roversDB

# Retrieve a specific rover by ID

@app.get('/rovers/{rover_id}')

def getRoverID(rover_id: int):
    
    roverList = getRoversList()
    try:
        
        rover = roverList[rover_id][0]
    except KeyError:
        # Raise an HTTPException with a 404 status code 
        raise HTTPException(status_code=404, detail="Rover not found")

    # Return the retrieved rover
    return rover

# Create a rover, POST

@app.post('/rovers')
def addRover(rover_id: int):
    roverList = getRoversList()
    try:
        # Check if rover with same ID already exists
        if rover_id in roverList:
            raise ValueError("Rover with the same ID already exists")
        elif rover_id < 1 and rover_id > 10:
            raise ValueError("Rover ID not in correct range (1-10)")

        # Add rover to database
        rover_data = Rover()
        rover_data.id = rover_id
        rover_data.xPosition = 0
        rover_data.yPosition = 0
        rover_data.roverStatus = "Not Started"
        rover_data.data = " "
        rover_data.direction = "SOUTH"
        roverList[rover_data.id].append(rover_data)

        return {f"Rover {rover_id} initialized."}

    except ValueError as ve:
        return {"error": str(ve)}

#Delete Rover, DELETE

@app.delete('/rovers/{rover_id}')
def deleteRover(rover_id: int):
    roverList = getRoversList()
    try:
        # Attempt to delete the rover from the database
        del roverList[rover_id]
    except KeyError:
        # Raise an HTTPException with a 404 status code and detail message if rover not found
        raise HTTPException(status_code=404, detail="Rover not found")

    # Return a success message
    return {f"The rover with ID: {rover_id} has been successfully deleted."}  


#Sends the list of commands to the rover,

@app.put('/rovers/{rover_id}')
def sendCommands(rover_id: int):
    roverList = getRoversList()
    error_codes = {
        'not_found': {'status_code': 404, 'detail': 'Rover not found'},
        'active': {'status_code': 405, 'detail': 'Rover is active'},
        'not_in_range': {'status_code': 406, 'detail': 'Rover is not in range of 1 to 10'}
    }

    try:
        if rover_id not in roverList:
            raise HTTPException(**error_codes['not_found'])
        elif roversDB[rover_id].roverStatus == 'Active':
            raise HTTPException(**error_codes['active'])
        elif rover_id < 1 and rover_id > 10:
            raise HTTPException(**error_codes['not_in_range'])
        else:
          moves = requests.get("https://coe892.reev.dev/lab1/rover/{rover}".format(rover=rover_id))
          rovers_move = json.loads(moves.text)
          movement = rovers_move["data"]['moves']
          roverList[rover_id][0].data = movement
          

          return {f"Rover {rover_id} has been sent the following commands: {movement}"}

    except HTTPException as he:
        return {"error": he.detail, "status_code": he.status_code}
    
def checkForMine(xCoord: int, yCoord: int):
    minesList = getMinesList()
    return any(mine.xPosition == xCoord and mine.yPosition == yCoord for mine in minesList.values())

def retrieveMinePin(xCoord: int, yCoord: int):
    minesList = getMinesList()
    for mine in minesList.values():
        if mine.xPosition == xCoord and mine.yPosition == yCoord:
          serialNum = mine.serialNum
          for i in range(100000000):
                pin = str(i).zfill(6)
                tempKey = pin + serialNum
                hashed = hashlib.sha256(tempKey.encode()).hexdigest()    
                if hashed[:6] == '0' * 6:
                    mine.defusedOrNot = True
                    bombID = mine.id
                    deleteMine(bombID)
                    print(f"Mine diffused with pin: {pin}")
                    return hashed
    

# Rover Dispatch --- POST

# starting a rover with a particular ID ( between 1 and 10)
@app.post('/rovers/{rover_id}/dispatch')

def dispatchRover(rover_id: int):
    
    error_codes = {
        'not_found': {'status_code': 404, 'detail': 'Rover not found'},
        'finished': {'status_code': 405, 'detail': 'Rover is finished executing'},
        'not_in_range': {'status_code': 406, 'detail': 'Rover is not in range of 1 to 10'}
    }

  
    if rover_id not in roversDB:
        raise HTTPException(**error_codes['not_found'])
    elif roversDB[rover_id].roverStatus == 'Finished':
        raise HTTPException(**error_codes['finished'])
    elif rover_id < 1 and rover_id > 10:
        raise HTTPException(**error_codes['not_in_range'])

    roverMapObject = getMap()
    
    mapNumColumns = roverMapObject.columns
    mapNumRows = roverMapObject.rows


    

    currentRover = getRoverID(rover_id)
    currentRover.data = sendCommands(currentRover.id)
    roverMovement = currentRover.data

    with open('Rover{rover}Log.txt'.format(rover =currentRover.Id), 'w') as f:
        f.write(roverMapObject.data.to_string())
    
    for moves in roverMovement:
        print(f"Rover currently at x:{currentRover.xPosition}, y:{currentRover.yPosition}, statis: {currentRover.roverStatus}\nCurrent move command: {moves}")
        message = f"Rover currently at x:{currentRover.xPosition}, y:{currentRover.yPosition}, statis: {currentRover.roverStatus}\nCurrent move command: {moves}"
        f.write(message + '\n')

        onMine = checkForMine(currentRover.xPosition, currentRover.yPosition)
        minesList = getMinesList()
        if onMine == True and moves != 'D':
            roverMapObject.data.iat[currentRover.yPosition, currentRover.xPosition] = '*'
            print(f"Rover with ID: {rover_id} has exploded.  Proceeding to remove it from database.")
            deleteRover(rover_id)
            
            for mines in minesList:
                if mines.xPosition == currentRover.xPosition and mines.yPosition == currentRover.yPosition:
                    bombID = mines.id
                    deleteMine(bombID)
            return f"Rover has exploded at {currentRover.xPosition}, {currentRover.yPosition}. Bomb {bombID} has been removed from mine list and rover {currentRover.id} has been removed as well"
        
        elif onMine == True and moves == 'D':                 
          roverMapObject.data.iat[currentRover.yPosition, currentRover.xPosition] = '*' 
          hashValue = retrieveMinePin(currentRover.xPosition, currentRover.yPosition)
          continue
        else:

          match moves:
            case 'L':
                if currentRover.direction == 'SOUTH':
                    currentRover.direction =='EAST'
                elif currentRover.direction == 'EAST':
                    currentRover.direction =='NORTH'
                elif currentRover.direction == 'NORTH':
                    currentRover.direction =='WEST'
                elif currentRover.direction == 'WEST':
                    currentRover.direction =='SOUTH' 

            case 'R':    
                if currentRover.direction == 'SOUTH':
                    currentRover.direction =='WEST'
                elif currentRover.direction == 'WEST':
                    currentRover.direction =='NORTH'
                elif currentRover.direction == 'NORTH':
                    currentRover.direction =='EAST'
                elif currentRover.direction == 'EAST':
                    currentRover.direction =='SOUTH'        
            case 'M':
                 if currentRover.direction == 'SOUTH':
                    if currentRover.yPostion != mapNumRows - 1:
                        roverMapObject.data.iat[currentRover.yPosition, currentRover.xPosition] = '*'
                        currentRover.yPosition += 1
                 elif currentRover.direction == 'WEST':
                    if currentRover.xPostion != 0:
                        roverMapObject.data.iat[currentRover.yPosition, currentRover.xPosition] = '*'
                        currentRover.xPosition -= 1
                 elif currentRover.direction == 'NORTH':
                    if currentRover.yPostion != 0:
                        roverMapObject.data.iat[currentRover.yPosition, currentRover.xPosition] = '*'
                        currentRover.yPosition -= 1
                 elif currentRover.direction == 'EAST':
                    if currentRover.xPostion != mapNumColumns - 1:
                        roverMapObject.data.iat[currentRover.yPosition, currentRover.xPosition] = '*'
                        currentRover.xPosition += 1
    
    currentRover.roverStatus = 'Finished' 
    f.write('\n' * 3)
    f.write(f'Rover{currentRover.id} has finished its mission')
    f.write('\n')
    f.write(f'Final Map rover {currentRover.id} has taken')
    f.write('\n')
    f.write(f)
    f.write(roverMapObject.data.to_string() +' \n')

    finalMessage = f'Rover{currentRover.id} has finished its mission'

    return finalMessage


# Access a particular Rover's Logs

@app.get('/rovers/{rover_id}/logs')

def getRoverLogs(rover_id: int):
    currentRover = getRoverID(rover_id)
    roverList = getRoverID(rover_id)
    error_codes = {
        'not_found': {'status_code': 404, 'detail': 'Rover not found'},
        'not_in_range': {'status_code': 406, 'detail': 'Rover is not in range of 1 to 10'}
    }

    if rover_id not in roverList:
        raise HTTPException(**error_codes['not_found'])
    elif rover_id < 1 and rover_id > 10:
        raise HTTPException(**error_codes['not_in_range'])

    with open('Rover{rover}Log.txt'.format(rover = currentRover.id), 'r') as f:
        log = f.read()
        return log

    