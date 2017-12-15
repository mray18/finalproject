#Event Function
    -Check Method
    -Take in all new credentials
    -Check for New Events:
	-If no conflicts, success
	-If conflicts, error
	
#Check MongoDB for New Events
-Take in all of the credentials for new event
    -Check for same day
    -Check for same room
    -Check for time
	-If no conflicts, add event
	-If conflicts, error
		
#Autopopulation of Table
    -Recieve signal
    -Pull data from MongoDB
    -Push to front end
    
#Check MongoDB for User Events
    -Take in phone number
    -Check for phone number in MongoDB database
    -Return all existing events
    
#Check MongoDB for Twilio
    -Take in a date
    -Return all existing reservations