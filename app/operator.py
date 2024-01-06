import requests
import json
import dotenv

dotenv.load_dotenv()
baseURL = "http://localhost:8000"




def rover_menu():
      while True:
        inputRover = input("Welcome to Rover Menu!\nThese are your options:\n",
                      "Press 1 to view all Rovers\n",
                      "Press 2 to view a specific Rover\n",
                      "Press 3 to create a new Rover\n",
                      "Press 4 to delete a Rover\n",
                      "Press 5 to Update the Rover\n",
                      "Press 6 to dispatch a Rover\n",
                      "Press 7 to return a Rover's Logs\n"
                      "Press 8 to return to Main Menu\n")
        if int(inputRover) < 1 or int(inputRover) > 8:
            print("Invalid input, try again")
            continue
        
        match (inputRover):
            case "1":
                response = requests.get(baseURL+"/rovers")
                print("These are the current Rovers:\n")
                jsonPrint(response.json())
                
                
            case "2":
                roverNum = input("Enter the number of the Rover you would like to view: ")
                number = int(roverNum)
                payload = {'rover_id': number}
                response = requests.get(baseURL+"/rovers/"+str(number)) 
                jsonPrint(response.json())
            case "3":
                roverNum = input("Enter the number of the Rover you would like to add: ")
                number = int(roverNum)
                payload = {'rover_id': number}    
                response = requests.post(baseURL+"/rovers/",params=payload) 
                jsonPrint(response.json())
            case "4":
                roverNum = input("Enter the number of the Rover you would like to delete: ")
                number = int(roverNum)
                payload = {'rover_id': number}    
                response = requests.delete(baseURL+"/rovers/"+roverNum)  
                jsonPrint(response.json())
            case "5":                
                roverNum = input("Enter the ID of the Rover you want to update: ")
                number = int(roverNum)
                payload = {'rover_id': number}
                request = requests.put(baseURL+"/rovers/"+number, params=payload)
                jsonPrint(request.json())

            case "6":
                roverNum = input("Enter the ID of the Rover you want to dispatch: ")
                number = int(roverNum)
                payload = {'rover_id': number}
                request = requests.post(baseURL+"/rovers/"+number+"/dispatch", params=payload)
                jsonPrint(request.json())
            case "7":
                roverNum = input("Enter the ID of the Rover you want to return logs: ")
                number = int(roverNum)
                payload = {'rover_id': number}
                requests.get(baseURL+"/rovers/"+number+"/logs", params=payload)
                jsonPrint(request.json())
            case "8":     
                break
            
            #Return to main menu
        MainMenu()      
        
         
def mine_menu():
    flag = False
    while flag == False:
        inputMine = input("Welcome to Rover Menu!\nThese are your options:\n",
                      "Press 1 to view all Mines\n",
                      "Press 2 to view a specific Mine\n",
                      "Press 3 to delete a Mine\n",
                      "Press 4 to add a Rover\n",
                      "Press 5 to Update a Mine\n",
                      "Press 6 to return to Main Menu\n")
        if int(inputMine) < 1 or int(inputMine) > 6:
            print("Invalid input, try again")
            continue
        
        match(inputMine):
            
            case "1":
              response = requests.get(baseURL+"/mines")
              print("These are all of the present Mines:\n")
              jsonPrint(response.json()) 

            case "2":
                mine = input("Enter the mine ID of the mine you want to see: ")
                mineNum = int(mine)
                payload = {'mine_id': mineNum}
                mineResponse = requests.get(baseURL+"/mines/"+mine)
                jsonPrint(mineResponse.json()) 
            case "3":
                mine = input("Enter the ID of the Mine you want to delete: ")
                mineNum = int(mine)
                payload = {'mine_id': mineNum}
                mineResponse = requests.delete(baseURL+"/mines/"+mine)
                print(mineResponse.text)
            case "4":
                mine = input("Enter the ID of the Mine you wish to add: ")
                mineNum = int(mine)
                payload = {'mine_id': mineNum}
                mineResponse = requests.post(baseURL+"/mines", params=payload)
                print(mineResponse.text)
            case "5":      
                mine = input("Enter the ID of the Mine you wish to update: ")
                mineNum = int(mine)
                payload = {'mine_id': mineNum}
                mine = requests.put(baseURL+"/mines/"+mine, params=payload)
                print(mine.text)  

            case "6":
               flag = True
    MainMenu()        


def map_menu():    
    flag = False
    while flag == False:
        inputMap = input("Welcome to Map Menu!\nThese are your options:\n",
                          "Press 1 to view the Map\n",
                          "Press 2 to update the Map\n",
                          "Press 3 to return to Main Menu\n")
        if int(inputMap) < 1 or int(inputMap) > 3:
            print("Invalid input, try again")
            continue

        match (inputMap):

            case "1":
               response = requests.get(baseURL+"/map")
               print("This is the current map:\n")
               jsonPrint(response.json())
            case "2":
                columns, rows = input("Enter the new desired number of columns and rows: ").split()
                columns = int(columns)
                rows = int(rows)
                payload = {'cols': columns, 'rows': rows}
                newMapRequest = requests.put(baseURL+"/map", params=payload)
                print(newMapRequest.text) 
            case "3":          
                flag = True
    MainMenu() 

def jsonPrint(object):
    text = json.dumps(object, sort_keys=True, indent=4)
    print(text)



def MainMenu():
    

    flag = False

    while flag == False:
        
        input = input("Welcome to Rover Ground Control!\nThese are your options:\n"
                      "Enter '1' for Rover Menu\n",
                      "Enter '2' for Mine Menu\n",
                      "Enter '3' for Map Menu\n",
                      "Enter '4' to exit\n")
        match (input):

          case "1":
               
             rover_menu() 

          case "2":

             mine_menu()

          case "3":    

             map_menu() 

          case "4":

             print("Thank you for using Rover Ground Control!")
             print("Exiting program...")
             flag = True      

if __name__ == '__main__':
    MainMenu()