def get_datetime():
    am_or_pm = request.form["AMorPM"].strip() # AM or PM
    month = int(request.form["month"]) # Month 
    day = int(request.form["day"]) # Day
    year = int(request.form["year"]) # Year
    hour = int(request.form["hour"]) #Hour
    minute = int(request.form["minute"]) # Minute

    # Hour is out of range of hour isn't between 1 and 12
    if not 1 <= hour <= 12:
        raise ValueError("Hour out of range")

    # Adds 12 if it's pm (only allows military time)
    hour24 = hour % 12 + (12 if am_or_pm == "PM" else 0)

    # Full datetime
    return datetime(year, month, day, hour24, minute)