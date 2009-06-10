import sys
class MyLog:   
    def write(self,msg):
        print >> sys.stderr, msg
        

myLog = MyLog()




