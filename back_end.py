#Event Function
    if method == "new"
        #New Event Function
    elif method == "edit" or method == "delete"
        #User Event Function
	
#New Events
    #Take in all credentials relevant
    phone_num = ""
    first = ""
    last = ""
    day = ""
    from_time = ""
    to_time = ""
    room = ""
    results = db.reservations.find({"date"=day},{"room":room})
    if not results:
        db.reservations.insert({'phone_number': phone_num 'first': first, 'last': last, 'date': date, 'fromTime': from_time, 'toTime': to_time, 'room': room })
    for result in results:
        from_time1 = datetime.strptime(result["from_time"], '%H:%M')
        to_time1 = datetime.strptime(result["to_time"], '%H:%M')

        # time attempting to add
        from_time_obj = datetime.strptime(from_time, '%H:%M')
        to_time_obj = datetime.strptime(to_time, '%H:%M')

        # sees if the fromTime is within the range of the original time slot
        if from_time_obj >= from_time1 and from_time_obj <= to_time1:
            print('1 time conflict!')

        # sees if the toTime is within the range of the original time slot
        elif to_time_obj >= from_time1 and to_time_obj<= to_time1:
            print('2 time conflict!')

        else:
            print('you\'re good')
            db.reservations.insert({'phone_number': phone_num 'first': first, 'last': last, 'date': date, 'fromTime': from_time, 'toTime': to_time, 'room': room })
    
#Check MongoDB for User Events
    phone_num = ""
    results = db.reservations.find({"phone_number":phone_num})
    print results
        
#Check MongoDB for Twilio
    day = ""
    results = db.reservations.find({"date": day})
    print results