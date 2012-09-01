#!/usr/bin/python
###########################################################
# Module Creator
#
# Creates a generic Log2t timeline module given a
# CSV file. It uses a jinja2 template to format and 
# create a Log2timeline module. This module only supports
# CSV files at this time and cannot handle any other type 
# of log data.
# 
# Version: 0.1
# Author: Kevin Glisson
# Date: 08/14/2012
#
#############################################################

import jinja2
import os
from datetime import datetime

def main(myfile, delim):
    env = jinja2.Environment(autoescape=False, loader=jinja2.FileSystemLoader('./templates/'))
    template = env.get_template('log2tModule.template')
    
    templateValues = {}
    
    #set the delimiter for the module
    templateValues["delim"] = delim

    filename = raw_input('Filename -> ')
    templateValues["filename"] = filename
    templateValues["description"] = raw_input('Description -> ')
    templateValues["source"] = raw_input('Source -> ')
    templateValues["sourceType"] = raw_input('Source Type -> ')
    
    # Parse given file
    headers = (myfile.readline()).split(delim) 
    values = (myfile.readline()).split(delim)

    # Match the headers with their respective values
    print "Current CSV Mappings"
    for idx, (head, val) in enumerate(zip(headers, values)):
        print "%s -> %s: %s" % (idx, head, val)

    # Parse option fields
    print "For fields that have more than one answer pipe seperate the answers ex. Option1|Option2|Option3"
    shortFieldInput = raw_input("Which fields do you want included in the short field? -> ")
    
    # Echo the index into the expected variable included in the template
    shortFields = ["$fields[%s]" % x for x in shortFieldInput.split('|')]
    
    # Create the string in something that perl will recognize 
    # (it uses the dot operator for string concationation
    templateValues["short"] = '." ".'.join(shortFields)

    descFieldInput = raw_input("Which fields do you want included in the desc field? -> ")
    descFields = ["$fields[%s]" % x for x in descFieldInput.split('|')]
    templateValues["desc"] =  '." ".'.join(descFields)

    notesFieldInput = raw_input("Which fields do you want included in the notes column? -> ")
    notesFields = ["$fields[%s]" % x for x in notesFieldInput.split('|')]
    templateValues["notes"] = '." ".'.join(notesFields)
    
    # Determine if datetime information is in one or two fields
    dateTimeAnswer = raw_input("Is the time and date information in one field(yY/nN)? -> ")
    
    if (dateTimeAnswer.lower() == 'y'):
        dateTimeIndex = raw_input("Which index holds the datetime information? -> ")
        templateValues["dateTimeIndex"] = "$fields[%s]" % dateTimeIndex
    else:
        dateIndex = raw_input("Which index holds the date information -> ")
        templateValues["dateIndex"] = "$fields[%s]" % dateIndex
        timeIndex = raw_input("Which index holds the time information? -> ")
        templateValues["timeIndex"] = "$fields[%s]" % timeIndex

    # Parse the datetime information 
    print """The following is a decriptive language that allows Python/Perl Datatime Module
             to be able to parse dates and times.

             Examples:
             Time                       Format
             -----------------------------------------------------------------------------
             Aug-21-2012                %b-%d-%Y
             21:52:11                   %H-%M-%S
             8/23/2012 1:24:52 PM       %m/%d/%Y %I:%M:%S %p
             "8/23/2012 21:53:33 GMT"   "%m/%d/%Y %H:%M:%S GMT"

             Values:
             Directive  |   Meaning
             %a         |   Locale's abbreviated weekday name
             %A         |   Locale's full weekday name
             %b         |   Locale's abbreviated month name
             %B         |   Locale's full month
             %c         |   Locale's appropriate date and time representation
             %d         |   Day of the mont as a decimal [01,31]
             %f         |   Microsecond as decimal number [0,999999], zero-padded on the left
             %H         |   Hour (24-hour clock) as a decimal number [00,23].    
             %I         |   Hour (12-hour clock) as a decimal number [01,12].    
             %j         |   Day of the year as a decimal number [001,366].   
             %m         |   Month as a decimal number [01,12].   
             %M         |   Minute as a decimal number [00,59].      
             %p         |   Locale's equivalent of either AM or PM.
             %S         |   Second as a decimal number [00,61]. 
             %U         |   Week number of the year (Sunday as the first day of the week) 
                            as a decimal number [00,53]. All days in a new year preceding 
                            the first Sunday are considered to be in week 0.
             %w         |   Weekday as a decimal number [0(Sunday),6].   
             %W         |   Week number of the year (Monday as the first day of the week) 
                            as a decimal number [00,53]. All days in a new year preceding 
                            the first Monday are considered to be in week 0.
             %x         |   Locale.s appropriate date representation.    
             %X         |   Locale.s appropriate time representation.    
             %y         |   Year without century as a decimal number [00,99].    
             %Y         |   Year with century as a decimal number.   
             %z         |   UTC offset in the form +HHMM or -HHMM 
                                (empty string if the the object is naive
             %Z         |   Time zone name (empty string if the object is naive).    
             %%         |   A literal '%' character.
            """
    
    if(dateTimeAnswer.lower() == 'y'):
        print "Below is an sample from your file, you must provide an exact match to this string"
        print "A sample from your choosen field: %s" % values[int(dateTimeIndex)]
        # Give the user multiple different tries to parse the datetime information
        while(True):
            templateValues["dateTimeFormat"] = raw_input("Datetime Format -> ")
            # Try to parse the data
            try:
                datetime.strptime(values[int(dateTimeIndex)], templateValues["dateTimeFormat"])
                break
            except:
                print "This string cannot parse the choosen field. Try Again?"
    else:
        print "A sample from your chosen field: %s" % values[int(dateIndex)]
        while(True):
            templateValues["dateFormat"] = raw_input("Date Format -> ")
            try:
                datetime.strptime(values[int(dateIndex)], templateValues["dateFormat"])
                break
            except:
                print "This string cannot parse the choosen field. Try Again?"

        print "A sample from your chose field: %s" % values[int(timeIndex)]
        while(True): 
            templateValues["timeFormat"] = raw_input("Time Format -> ")
            try:
                datetime.strptime(values[int(timeIndex)], templateValues["timeFormat"])
                break
            except:
                print "This string cannot parse the choosen field. Try Again?"

    # Try to determine what timezone this module should use
    while(True):
        tzInfo = raw_input("Is the information time zone in (1) UTC or (2) System Time? -> ")
        if int(tzInfo) == 1:
            tz = "'UTC'"
            break
        elif int(tzInfo)== 2:
            tz = "$self->{'tz'}"
            break
        else:
            print "Please Select a valid Option"

    templateValues["tz"] = tz
    # Write template to file
    with open(filename + ".pm", 'w') as f:
        f.write(template.render(templateValues))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="""Create a generic Log2t timeline module given a CSV file""")

    parser.add_argument('-f', type=argparse.FileType('rb'), help="File to create log2t module for")
    parser.add_argument('-l', default=',', help="Input file delimiter")
    params = parser.parse_args()
    main(params.f, params.l)
