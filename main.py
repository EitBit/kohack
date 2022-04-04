from cgitb import text
from doctest import master
from tempfile import TemporaryFile
from textwrap import fill
import tkinter as tk
from tkinter import font
from turtle import color, width

from click import command
import jewishcalendar as jc
import datetime
import threading
#import bluetooth


registry = [] #BlueTooth device names
contact = [] #The people with whom they have been in contact with
timer = [] #expiration timer
tamei = False
exposed = False


#need to add tumah and tehara element

def calculateKorbanot(gYear, gMonth, gDay):
    #Basic korbanot for every day
    korbanot = ["Tamid", "Mincha"]
    #Getting the absolute value of days from the inputed date
    absval = jc.gregorian_to_absdate(gYear, gMonth, gDay)
    #day of week of requested date
    dayOfWeek = jc.get_weekday_from_absdate(absval)
    #hebrew month of requested date
    hDate = jc.absdate_to_hebrew(absval)
    #hebrew year, month, day, and the name of the month of requested date
    hYear, hMonth, hDay, hName = hDate

    #Korban Shabbat
    if(dayOfWeek == 6):
        korbanot.append("Musaf")
    
    #Korban Chodesh
    if(hDay == 1): 
        korbanot.append("Chodesh")
        korbanot.append("Musaf")
        
    #Korban Pesach
    if(hName == 'Nisan' and hDay == 15):
        korbanot.append("Pesach")
        korbanot.append("Chagigah")
        korbanot.append("Musaf")
    
    #Korban Pesach Sheini
    if(hMonth == 2 and hDay == 15):
        korbanot.append("Pesach Sheini")
        korbanot.append("Chagigah")
        korbanot.append("Musaf")
        
    return korbanot, hDate

def calculateMaaser(balance):
    #Terumah gedolah, maximum amount
    terumahGedolah = 0.025*balance
    balance -= terumahGedolah

    #MaaserRishon 10%
    maaserRishon = 0.1*balance
    balance -= maaserRishon

    #MaaserSheini 10%
    maaserSheini = 0.1*balance
    balance -= maaserSheini

    #Total
    total = terumahGedolah + maaserRishon + maaserSheini

    return terumahGedolah, maaserRishon, maaserSheini, total


def scan():
    #Finds device, if it's in the registry add device to a contact list, after 24 hours its removed from that list
    devices = bluetooth.discover_devices(lookup_names = True, lookup_class = True)
    for name in registry:
        for address in devices:
            if(name == bluetooth.lookup_name(address) and not address in contact):
                contact.add(address)
                timer.add(threading.Timer(86400, removeI(address)))
    timer.add(threading.timer(5,scan()))

#removes value from list after 24 hours 
def removeI(num):
    contact.remove(num)
    pass

window = tk.Tk()
window.geometry("420x985")
window.title = "Karbanot Calander"
window.configure(bg="black")

bigFrame = tk.Frame(master=window)



def clearPage():
    global bigFrame
    bigFrame.destroy()
    bigFrame = tk.Frame(master=window)
    bigFrame.grid(row=0,column=0)
    return bigFrame
    

def pageCalendar():
    
    bigFrame = clearPage()
    #very good and organized gui stuff
    #horribly implemented but it works so dont touch 
    dt = datetime.datetime.today()
    year = dt.year
    month = dt.month
    day = dt.day
    korbanot, hDate = calculateKorbanot(year,month,day)
    tabs = ["Calendar","Tracker","Calculator",pageCalendar,pageTracker,pageCalculator]
    for masterRows in range(3):
        masterFrame = tk.Frame(master=bigFrame,relief=tk.RAISED,bg="black")
        if masterRows==0:
            for columns in range(3):
                button = tk.Button(master=masterFrame,text=tabs[columns],width=17,height=1,command=tabs[columns+3]).grid(row=masterRows,column=columns)
            masterFrame.grid(row=masterRows,column=0)


        elif masterRows == 1:
            label = tk.Label(master=masterFrame,text=hDate[3],bg="aqua",width=50,height=3,font=("Arial",10)).grid(row=0,column=0)
            masterFrame.grid(row=masterRows,column=0)

        elif masterRows == 2:
            firstdone = False
            count = 0
            limit = jc.hebrew_month_days(year,hDate[1])
            for rows in range(6):
                for columns in range(7):
                    
                    
                    frame  = tk.Frame(master=masterFrame,relief=tk.RIDGE,borderwidth=1)
                    frame.grid(row=rows,column=columns,padx=2,pady=2)
                    if (rows+columns >= jc.get_weekday_from_absdate(jc.hebrew_to_absdate(hDate[0],hDate[1],1)) and count<limit) or (count < limit and firstdone==True):
                        firstdone = True
                        count+=1 
                        label = tk.Label(master=frame,text=str(count),height=2,width=8,bg="gray",font=("Arial",8)).pack(side=tk.TOP)
                        korbanot, hDate = calculateKorbanot(year,month,count+1) 
                        korbanString = ""
                        for x in korbanot:
                            korbanString+=x+"\n"
                        label = tk.Label(master=frame,text=korbanString,height=4,width=8,font=("Arial",8)).pack(side=tk.BOTTOM)
                        
                    else:
                        label = tk.Label(master=frame,text= "\n  \n  \n",height=2,width=8,bg="gray",font=("Arial",8)).pack(side=tk.TOP)
                        label = tk.Label(master=frame,text="\n  \n  \n",height=4,width=8,font=("Arial",8)).pack(side=tk.BOTTOM)


            masterFrame.grid(row=masterRows,column=0)

def pageCalculator():
    bigFrame = clearPage()
    #entry for number (>1) -> call calc masser w/ number
    #dyanmic label gets return with all different maasers + total [terumahGedolah, maaserRishon, maaserSheini, total]
    #big frame contains two master frames, top frame has exposure status, bottom frame has set buttons
    masterFrame1 = tk.Frame(master=bigFrame,bg="pink").grid(row=0,column=0)
    label = tk.Label(master=masterFrame1,text="Insert crop quantity:",width=100,height=10,font=("Helvetica",10)).grid(row=0,column=0)
    entry = tk.Entry(master=masterFrame1).grid(row=1,column=0)
    button = tk.Button(master=masterFrame1,bg="green",text="Calculate",font=("Helvetica",10),width=15,height=10,command=lambda x: print("good")).grid(row=2,column=0)

    masterframe2 = tk.Frame(master=bigFrame).grid(row=1,column=0) 


def pageTracker():
    bigFrame = clearPage()
    #run scan 

pageCalendar()        
#scan() should start on startup
window.mainloop()