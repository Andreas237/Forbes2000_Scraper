##########  Some Text Functions  ##########
import re #for regex on URL
import time # check run time
import math

# Return proper case string
def properCase(inStr):
    return ( inStr[0].upper() + inStr[1:])

# Return the company name in upper case
def getForbesCompany(inStr):
    return [i for i in re.split(r'(\W+)',inStr)][10]


###########################################################################################################
#   CLASS
#   Name:           forbes_killer
#   Purpose:        Take a URL to the Forbes website and strip the info
#   Example URL:    http://www.forbes.com/companies/actavis
###########################################################################################################
import urllib.request as urlr # For URLOpen
import urllib.error

class forbes_killer:

    # Values hold everything scraped that we want
    values = {'ForebsURL':'',
              'MarketCap': 0,
              'Industry': '',
              'Founded': 0,
              'Country': '',
              'CEO': '',
              'Employees': 0,
              'Sales': '',
              'Headquarters': '',
              'Website': '',
              'EmailDomain': ''
              }
    
    start = 0
    ourStuff = ''
    companyName = ''
    lastEnd = 0 # lastEnd from the last DT tag
    VALID_WEBSITE = 1 # If invalid website set to 0, set in getStringFromURL

    # Default constructor
    def __init__(self):
        # Base Forbes URL
        self.values['Website'] = 'http://www.forbes.com/companies/'


    # Constructor taking a URL
    def __init__(self,url):
        self.values['Website'] = url.replace(",","")
        self.getStringFromURL()
        if( self.VALID_WEBSITE != 0):
            self.values['ForebsURL'] = self.values['Website']
            self.run()
        else:
            print("Error with website '" + self.values['Website'] + "'----------- Moving on.")

        
    # Open URL and save it for later
    def getStringFromURL(self):
        try:
            with urlr.urlopen( self.values['Website'] ) as f:
                self.ourStuff =  str( f.read(1000000).decode('utf-8') )
            f.close()
        except ValueError:
            print("ValueError: Couldn't open '" + self.values['Website'] + "'\nYou should delete this row from the file.")
            self.VALID_WEBSITE = 0
        except urllib.error.URLError:
            print("urllib.error.URLError: Couldn't open '" + self.values['Website'] + "'\nYou should delete this row from the file.")
            self.VALID_WEBSITE = 0
        except socket.gaierror:        
            print("socket.gaierror: Couldn't open '" + self.values['Website'] + "'\nYou should delete this row from the file.")
            self.VALID_WEBSITE = 0



    # Shrinks the String in mem
    def shrinkOurStuff(self):
         start = self.ourStuff.find( "<h1 class=\"large\">")
         end = self.ourStuff.find( "<!-- End Data -->" )
         self.ourStuff = self.ourStuff[start:end]


    # Test String method
    def printSome(self):
        for k,v in self.values.items():
            print(k, v)


    # Add tag to self
    def addToValues(self, tagName, tagValue):
        self.values[ tagName ] = tagValue
    

    # Get Market Cap
    def getMarketCap(self):
        start = self.ourStuff.find( "<li class=\"amount\">" ) + len ("<li class=\"amount\">")
        end = self.ourStuff.find( "</li>", start)
        ret = self.ourStuff[start:end].replace("<span>","")
        ret = ret.replace("</span>","")
        return ret

    def getEmailDomain( self):
        start = self.values['Website'].find("www.") + len("www.")
        return self.values['Website'][start:]
    

    # get website from DD tag
    # Ex: <a href="http://www.actavis.com" target="_blank">http://www.actavis.com</a>
    def getWebsite(self, instr):
        start = instr.find("http")
        end = instr.find("\" target=")
        return instr[start:end]

    def formatStringCurr(self, instr):
        multiplier = 1
        instr = instr.replace("$","")
        instr = instr.replace(" ","")
        if( instr.find("Billion")):
            multiplier = 1000000000
            instr = instr.replace("Billion","")
        if ( instr.find("B" ) ):
            multiplier = 1000000000
            instr = instr.replace('B',"")
        if( instr.find("Million")):
            multiplier = 1000000
            instr = instr.replace("Million","")
        if ( instr.find("M" ) ):
            multiplier = 1000000
            instr = instr.replace("M","")
        try:
            retVal = float(instr)*multiplier
        except ValueError:
            print("Failed on " + instr)
            instr = 0
        return float(instr)*multiplier


    # Checks if the DT tag is a valid key
    def validDT(self, dt):
        if( dt in self.values):
            return 1
        else:
            return 0
    
    # Finds the next DT tag
    def getDtTag(self, instr, start):
        start = instr.find("<dt>", start) + len("<dt>")
        end = instr.find("</dt>", start)
        tag =  instr[start:end]
        self.ourStuff = self.ourStuff[end:]
        self.lastEnd = end + 1
        return tag


    # Finds the next DD tag
    #       called after getDtTag
    def getDdTag(self, instr, start):
        start = instr.find("<dd>", start) + len("<dd>")
        end = instr.find("</dd>", start)
        tag =  instr[start:end]
        self.ourStuff = self.ourStuff[end:]
        self.lastEnd = end + 1
        return tag
    


    # Run the program
    # Method
    #   1 - Get the company name for fun
    #   2 - Reduce the size of the string in memory
    #   3 - Get the market cap
    #   4 - Add the other tags to this class
    #   5 - Print the dict as text
    def run(self):
        self.companyName = properCase( getForbesCompany( self.values['Website'] ) )
        self.shrinkOurStuff()
        # print("MarketCap: " + self.getMarketCap() )
        self.addToValues('MarketCap', self.formatStringCurr( self.getMarketCap() ) )

        instr = self.ourStuff
        count = instr.count("<dt>")
        while count != 0:
            dt = self.getDtTag( instr, self.lastEnd )   
            if( dt == 'Chief Executive Officer'):
                dt = 'CEO'
            # end 

            if( self.validDT(dt) == 1 ):

                if( dt == 'Website'):
                    dd = self.getWebsite( self.getDdTag( instr, self.lastEnd) )
                else:
                    dd = self.getDdTag( instr, self.lastEnd )
                # end if( dt == 'Website')
                
                if( dt == 'Sales'):
                    dd = self.formatStringCurr ( dd )
                # end if( dt == 'Sales')


                self.addToValues(dt,dd)
                count = count - 1
                self.addToValues('EmailDomain',self.getEmailDomain())

            # end if( validDT == 1 )
            
        self.printSome()
        
        # end  while count != 0
    # end def run(self)



###########################################################################################################
#   CLASS
#   Name:           ProcessURLs
#   Purpose:        read a CSV in and get the associated URL.  Close it. Write each URL and associated
#                   fields to a file.
#   Example URL:    http://www.forbes.com/companies/actavis
###########################################################################################################
import csv

class ProcessURLs:

    inFileName = '__'
    outFileName = '__'
    URLs = []
    killers = [] # Dictionaries
    keys = [] # Dictionary key values


    # default constructor looks at the CSV in the directory
    def __init__(self):
        print("In default constructor")
        self.run()

    # Constructor takes filename
    def __init__(self, TEST_ON):
        if ( TEST_ON != 0):
            self.inFileName = 'C:/Users/andreas.slovacek.MS/AppData/Local/Programs/Python/Python35/Scripts/Test_URLs.csv'
            self.outFileName = 'test_output.csv'
        else:
            self.inFileName = 'C:/Users/andreas.slovacek.MS/AppData/Local/Programs/Python/Python35/Scripts/full_list_urls.csv'
            self.outFileName = 'full_output.csv'
        self.run()


    # Runs the program
    #   1 - Open the file
    #   2 - Read the lines into a list
    #   3 - Create a list of the keys
    #   4 - open CSV writer
    #   5 - write keys to header
    #   6 - create the processed object
    #   7 - print the object to the screen
    #   8 - create the string to write

    def run(self):
        # 1
        with open( self.inFileName, newline='') as csvfile:
            csvReader = csv.reader(csvfile, delimiter=' ', quotechar='|')
            count = 0
        # 2
            for row in csvReader:
                if( count != 0):
                    row = str(row).replace("['","")
                    row = row.replace("']","")
                    self.URLs.append( row )
                count = count + 1

        

        # 3
        print("\n\n\n" + "-"*40)

        self.keys = forbes_killer("www").values.keys()


        # 4
        with open(self.outFileName, 'w', newline='') as csvfile:
        #with open('full.csv', 'w', newline='') as csvfile:
            # 5
            writer = csv.DictWriter(csvfile, fieldnames=self.keys)
            writer.writeheader()

            for u in self.URLs:
                # 6
                x = forbes_killer(u)
                writer.writerow( x.values )
                self.killers.append( x )
                # 7 
                # x.printSome()
                # 8
                #writer.writerow( x.values )
                #print( self.returnValueString( x.values ) )

    def returnValueString(self, inDict):
        outStr = ''
        for k in self.keys:
            outStr = str(inDict[k]) + ";"
        return outStr


start_time = time.time()
#x = forbes_killer('http://www.forbes.com/companies/actavis')
# y = ProcessURLs(1) # Test run
z = ProcessURLs(0) # live run

end_time = time.time()

seconds = end_time - start_time
minutes = math.fmod (seconds, 60 )
hours = math.fmod ( seconds, 60*60 )



print("\n"*10 + "It took " + str(hours) + " hours\n"
              + str(minutes) + " minutes\n"
              + "and " + str(seconds) + " seconds\n")
