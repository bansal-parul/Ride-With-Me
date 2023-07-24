""""
A function to map rider with a available list of drivers. If no suitable driver is matched to the rider, function return a string asking rider to check back later. 

The inputs are rider details such as rider name, start and end point. Start and end points are starting and ending location of rider in singapore pincode.

API Flow : Rider requests the rider and the get_driver_list_api gets a list of all available drivers. Then for each driver we check if the start and end time of the driver are within the range the start time of rider, if yes then using google routes api, first we calculte the actual distance driver will cover if he takes no rides. Then we calculate the modified distance driver has to cover if he picks up the rider and drops them and then goes to his/her destination. If the difference in the 2 distances is less than 6 kms, we assign the rider to the driver. Since the driver becomes busy, we remove the driver from table of available drivers using delete_driver_api and notify the driver about his/her ride using notification ride. Finally we share the ride details with the rider.

""""


import json
import requests
import googlemaps 
from datetime import datetime


API_KEY= 'AIzaSyB7U8FvcC4gek4YEmtuXzv-ZWuhH8HAguk'
get_driver_list_api = 'https://7y4c2hpftd.execute-api.us-east-1.amazonaws.com/dev/get_driver'
delete_driver_api = 'https://7y4c2hpftd.execute-api.us-east-1.amazonaws.com/dev/delete_driver'
notification_api = 'https://7y4c2hpftd.execute-api.us-east-1.amazonaws.com/dev/DriverNotification'

def get_driver_data(Data):
    data_refined = Data.split(",")
    data_refined = [data.split(":") for data in data_refined]
    for data in data_refined:
        if data[0] == 'destination':
            destination = data[1]
        if data[0] == ' username':
            username = data[1]
        if data[0] == ' start_time':
            start_time = int(data[1])
        if data[0] == ' departure':
            departure = data[1]
        if data[0] == ' end_time':
            end_time = data[1]
        if data[0] == ' car_brand':
            car_brand = data[1]
        if data[0] == ' car_number':
            car_number = data[1]
        if data[0] == ' email':
            driver_email = data[1]
        if data[0] == ' mobile_number':
            driver_phone = data[1]
    return destination, username, start_time, departure, end_time, car_brand, car_number, driver_email, driver_phone

def get_route_distance(route):
    return sum([leg['distance']['value'] for leg in route['legs']])

def get_time(str_time):
    str_time = str_time.split(" ")
    data = str_time[0]
    time = str_time[1].split(":")
    time_of_day = str_time[2]
    timestamp = str_time[0].split("/")
    if time_of_day == 'AM':
        final_time = timestamp[0] +timestamp[1] + timestamp[2] + time[0] + time[1]
    else :
        hour = int(time[0]) + 12
        final_time = timestamp[0] +timestamp[1] + timestamp[2] + str(hour) + time[1]
    return int(final_time)

def get_driver_data(Data):
    data_refined = Data.split(",")
    data_refined = [data.split(":") for data in data_refined]
    destination = None 
    username = None
    start_time = None 
    departure= None 
    end_time = None
    driver_phone = None
    for data in data_refined:
        if data[0] == 'destination':
            destination = data[1]
        if data[0] == ' username':
            username = data[1]
        if data[0] == ' start_time':
            start_time = int(data[1])
        if data[0] == ' departure':
            departure = data[1]
        if data[0] == ' end_time':
            end_time =int(data[1])
        if data[0] == ' car_brand':
            car_brand = data[1]
        if data[0] == ' car_number':
            car_number = data[1]
        if data[0] == ' email':
            driver_email = data[1]
        if data[0] == ' mobile_number':
            try:
                driver_phone = data[1]
            except error as e:
                ## do nothing
                x = "nothing"
    return destination, username, start_time, departure, end_time, car_brand, car_number, driver_email, driver_phone

def get_route_distance(route):
    return sum([leg['distance']['value'] for leg in route['legs']])

def match_drivers_to_riders(drivers, rider, gmaps_client):
    matches = {}
    rider_name = rider['username']
    rider_start = rider['start']
    rider_destination = rider['destination']
    #rider_start_time = get_time(rider['start_time'])
    rider_start_time = int(rider['start_time'])
    now = datetime.now()
    current_time = int(now.strftime("%d%m%Y%H%M%S"))
    #print("current time" ,current_time)
    for driver in drivers:
        destination, username, start_time, departure, end_time, car_brand, car_number, driver_email, driver_phone = get_driver_data(driver)
       # print("destination, username, start_time, departure, end_time, car_brand, car_number, driver_email, driver_phone")
        if start_time <= rider_start_time and end_time > rider_start_time:
            driver_route = gmaps_client.directions(start ,destination)
            #print("driver route")
            modified_route = gmaps_client.directions(start, destination, waypoints=[rider_start, rider_destination], optimize_waypoints=True)
            driver_route_distance = get_route_distance(driver_route[0])
            #print("driver_route_distance")
            modified_route = get_route_distance(modified_route[0])
            #print("Actual Distance",driver_route_distance )
            #print("Modified Distance", modified_route)
            #print("route distance")
            if modified_route - driver_route_distance <= 6000:
                #delete driver from available list
                delete_driver = {"username":username}
                response = requests.post(delete_driver_api, json = delete_driver) 
                #Send Notification to Driver
                content = "Rider Details are as follows \n Rider Name :" + rider_name+"\n Rider Start time" + rider_start_time + "\n Rider Departure" +rider_start + "\n Rider destination"+ rider_destination
                notif = {"phone_number" : driver_phone,
                    'email' :driver_email,
                    'content':content  ,
                    'subject' : "Ride With Me : Rider Details"}
                #print("Done Unitl Here")
                response = requests.post(notification_api, json = notif)
                #send back driver details
                rider_content = "Hurray! your ride has been confirmed. The driver details are \n Driver Name" + username + "\n Car" + car_brand + "\n Car Number" + car_number + "\n Driver Contact" +driver_phone
                return rider_content
         
        else :
            content = "Sorry, No drivers Available at the Moment. Please checkback later"
            return content
            #print("in else")
    return {
        'statusCode': 200,
        'body': json.dumps("Sorry, No drivers Available at the Moment. Please checkback later", default=str)
    }


def lambda_handler(event, context):
    response = requests.post(get_driver_list_api, auth = None)
    driver_list = response.json()['body']
    data_driver = driver_list[1:-1].split('{')[1:]
    data_driver = [data.replace('}', "") for data in data_driver]
    data_driver = [data.replace('"','' ) for data in data_driver]
    gmaps_client = googlemaps.Client(key=API_KEY)
    rider = json.loads(event['body'])
    #rider = {'username': "test1", 'start' : 'Singapore 448791',"destination" : "Singapore 469973", "start_time" :'16/04/2023 6:40 PM' }
    rider_name = rider['username']
    rider_start = rider['start']
    rider_destination = rider['destination']
    rider_start_time = get_time(rider['start_time'])
    content = match_drivers_to_riders(data_driver,rider,gmaps_client)
    return { 'statusCode': 200,
            'body': json.dumps(content, default=str) }
