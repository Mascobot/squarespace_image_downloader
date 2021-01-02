import tkinter as tk
from tkinter import filedialog 
import requests
import xml.etree.ElementTree as ET
import urllib.request

window = tk.Tk()
window.title('Squarespace image downloader by @Mascobot') 
window.geometry("450x300") 
window.config(background = "white") 

#Global variables:
xmlfile = ''
folder_selected = ''

def browseFiles(): 
    global xmlfile, labeltext
    xmlfile = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = (("XML files", "*.xml*"), ("all files", "*.*"))) 
    if folder_selected == '':
        labeltext.set("XML file has been selected. Please select destination folder") 
    else:
        labeltext.set("XML file and destination folder have been selected. Ready to start download") 
       
def download(): 
    global labeltext
    if xmlfile == '':
        labeltext.set("Please select XML file") 
    elif folder_selected == '':
        labeltext.set("Please select destination folder") 
    else:
        labeltext.set("Downloading images.Please wait...") 
        tree = ET.parse(xmlfile)
        root = tree.getroot()
        images_jpg = set([elem.text for elem in root.iter() if elem.tag=='link' and '.jpg' in elem.text])
        images_png = set([elem.text for elem in root.iter() if elem.tag=='link' and '.png' in elem.text])
        opener=urllib.request.build_opener()
        opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        urllib.request.install_opener(opener)

        for image_url in images_jpg:
            path = folder_selected + '/' + image_url.split('/')[-1]
            urllib.request.urlretrieve(image_url, path)
          
        for image_url in images_png:   
            path = folder_selected + '/' + image_url.split('/')[-1]
            urllib.request.urlretrieve(image_url, path)
        labeltext.set("Finshed downloading all images") 
        

def destination():
    global folder_selected, labeltext
    folder_selected = filedialog.askdirectory()
    if xmlfile == '':
        labeltext.set("Destination folder has been selected. Please select XML file.") 
    else:
        labeltext.set("XML file and destination folder have been selected. Ready to start download.") 


def changeText():
    global labeltext
    labeltext.set("Text updated") 

#Buttons
button_explore = tk.Button(window, text = "Browse local XML File", command = browseFiles)  
button_destination = tk.Button(window, text = "Select destination folder", command = destination)  
button_download = tk.Button(window, text = "Start download", command = download)     
button_exit = tk.Button(window, text = "Exit", command = exit)  
labeltext = tk.StringVar()
labeltext.set("Select XML file and destination folder")  
label = tk.Label(window, textvariable=labeltext)

#Grids: 
column = 160
button_explore.grid(padx = column, pady = 10)   
button_destination.grid(padx = column, pady = 15)   
button_download.grid(padx = column, pady = 20)   
button_exit.grid(padx = column, pady = 25) 
label.grid(row=10) 


window.mainloop()
