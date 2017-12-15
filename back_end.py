#Event Function
    if method == "new"
        #New Event Function
    elif method == "edit" or method == "delete"
        #User Event Function
	
#New Events
    #Take in all credentials relevant
    day = ""
    room = ""
    from_time = ""
    to_time = "" 
    results = db.reservations.find({"date"=day},{"room":room})
        #Check for time conflicts
    #If conflicts, error, else
    db.reservations.insert({'phone_number': phone_number
    
#Check MongoDB for User Events
    phone_num = ""
    results = db.reservations.find({"phone_number":phone_num,})
    print results
        
#Check MongoDB for Twilio
    day = ""
    results = db.reservations.find("date": day)
    print results