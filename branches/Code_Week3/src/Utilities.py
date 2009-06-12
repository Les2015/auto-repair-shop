import sys
from datetime import datetime

class MyLog:   
    def write(self,msg):
        print >> sys.stderr, msg
        
myLog = MyLog()

DATE_FORMAT = "%b %d, %Y  %H:%M:%S"
SHORT_DATE_FORMAT = "%b %d, %Y"
    
def dateToString(date, format=DATE_FORMAT):
    """ If none, return empty string, otherwise return string version of date. """
    if date == None:
        return ""
    else:
        return date.strftime(format)
    
def stringToDate(strDate):
    """ If empty string, return None, otherwise return datetime object 
        corresponding to string formatted date.  Should be inverse of
        dateToString function. """
    if strDate == "":
        return None
    else:
        return datetime.strptime(strDate, DATE_FORMAT)

def shortDate(strDate):
    """ Take the standard string date representation and return a short date """
    return dateToString(stringToDate(strDate), SHORT_DATE_FORMAT)


################################################################################

def main():
    """ Test the date/string conversion functions. """
    date = datetime.now()
    print str(date)
    print dateToString(date)
    print shortDate(dateToString(date))
    print str(stringToDate(dateToString(date)))
    print
    # Let's make sure that None is handled correctly as well.
    date = None
    print str(date)
    print dateToString(date)
    print shortDate(dateToString(date))
    print str(stringToDate(dateToString(date)))
        
if __name__ == "__main__":
    main()