#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 13:48:35 2021

@author: hunain
"""

from tkinter import filedialog
from tkinter import *
import pydicom
import os
from hashlib import sha1
import csv


def get_filenames (dicom_dirname):
    # Get all the filenames in the DICOM directory
    filename_list = []
    for path, subdirs, files in os.walk(dicom_dirname):
        for name in files:
            if not name.startswith('.'):
                f = os.path.join(path, name)
                filename_list.append(f)
    return filename_list

def get_patientID (filename_list):
    # Iteratre through the filenames till the func comes across
    # a DICOM. Then return the patientID
    for ix in range(len(filename_list)):
        fn = filename_list[ix]
        try:
            di = pydicom.dcmread(fn)
            patientID = di.PatientID
            print('PatientID: ' + patientID)
            return patientID
        except:
            print('Not a dicom: ' + fn)

def hash_key_gen (patientID):
    # Create a hash key from the patient ID
    try:
        hash_object = sha1(patientID.encode('utf-8'))
        hash_key = hash_object.hexdigest()
        print(hash_key)
        return hash_key
    except Exception as e:
        print(patientID)
        print(e)

def ensure_dir(fname):
    #creates the directory if it doesn't exist
    try:
        if (not fname is None) and (not fname == ''):
            op_dname=os.path.sep.join(fname.split('/')[:-1])
            if not os.path.exists(op_dname):
                    os.makedirs(op_dname)
    except:
        print("Unable to create directory for: " + fname)

def anonymise_dicom (fn, new_fn, elements_to_anonymise, replace_element):
    di = pydicom.dcmread(fn)
    if 'report' in di.SeriesDescription:
        print('Report discarded')
    else:
        for ii,_ in enumerate(elements_to_anonymise):
            e = elements_to_anonymise[ii]
            if e in di:
                di.data_element(e).value = replace_element
        di.remove_private_tags()
        
        ensure_dir(new_fn)
        di.save_as(new_fn)
    return True

def anonymise_dicom_study (orig_name, new_name, new_key):
    '''
        orig_name: orignal dicom directory name
        new_name: anonymised directory name
        
    '''
    dicom_dirname = orig_name
    filename_list = get_filenames (dicom_dirname)
    #fn = filename_list[0]
    for ix in range(len(filename_list)):
        fn = filename_list[ix]
        new_fn = fn.replace(orig_name, new_name)
        try:
            # print(new_fn)
            anonymise_dicom (fn, new_fn, elements_to_anonymise, new_key)
        except:
            print("Warning: failed to anonymise "+fn)
    
elements_to_anonymise = ['PatientName','PatientSex','PatientID','PatientBirthDate','OtherPatientIDs',
    'Patient​Birth​Time',
    'Other​PatientI​Ds',
    'Other​Patient​Names  ',
    'Patient​Birth​Name',
    'Patient​Address',
    'Patient​Mother​Birth​Name',
    'Ethnic​Group',
    'Patient​Religious​Preference']

def browse_input():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global input_path
    filename = filedialog.askdirectory()
    input_path.set(filename)
    print(filename)

def browse_output():
    # Allow user to select a directory and store it in global var
    # called folder_path
    global output_path
    filename = filedialog.askdirectory()
    output_path.set(filename)
    print(filename)

def anonymise():
    global message
    print(input_path.get())
    print(output_path.get())
    if input_path.get() == '' and output_path.get() == '':
        message.set('Need to choose the DICOM folder and save folder')
    elif input_path.get() == '' and output_path.get() != '':
        message.set('Need to choose the DICOM folder')
    elif input_path.get() != '' and output_path.get() == '':
        message.set('Need to choose the save folder')
    elif input_path.get() != '' and output_path.get() != '':
        anonymise_study(input_path.get(), output_path.get())
        message.set('Processed')
        
def anonymise_study(input_path, output_path):                   
    # Obtain the DICOM folder root and the individual folders
    dicom_root = input_path
    dicom_output = output_path
    
    # Write inital CSV
    output_csv = os.path.join(dicom_output + '/key_list.csv')
    with open(output_csv, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Patient_ID', 'Hash Key', 'Output filename'])
        
    individual_folders = [os.path.join(dicom_root, o) for o in os.listdir(dicom_root)]
    for dicom_dirname in individual_folders:
        print(dicom_dirname)
        filenames = get_filenames(dicom_dirname)
        patientID = get_patientID(filenames)
        if patientID == None:
            print("Not a DICOM or no patientID")
            pass
        else:
            hash_key = hash_key_gen (patientID)
            output_fn = os.path.join(dicom_output, hash_key)
            
            anonymise_dicom_study (dicom_dirname, output_fn, hash_key)
            
            with open(output_csv, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([patientID, hash_key, output_fn])
        print('')
        
    # Writes key list into CSV in output folder

    

        
root = Tk()

input_path = StringVar()
lbl1 = Label(master=root,textvariable=input_path)
lbl1.grid(row=0, column=3)
button1 = Button(text="Choose DICOM folder", command=browse_input)
button1.grid(row=0, column=1)

output_path = StringVar()
lbl2 = Label(master=root,textvariable=output_path)
lbl2.grid(row=1, column=3)
button2 = Button(text="Choose save folder", command=browse_output)
button2.grid(row=1, column=1)

message = StringVar()
lbl3 = Label(master=root,textvariable=message)
lbl3.grid(row=2, column=3)
button3 = Button(text="ANONYMISE", command=anonymise)
button3.grid(row=2, column=1)

experiment = StringVar()
lbl4 = Label(master=root,textvariable=experiment)
experiment.set('EXPERIMENTAL 12/04/2021')
lbl4.grid(row=3, column=1)

name = StringVar()
lbl5 = Label(master=root,textvariable=name)
name.set('Hunain Shiwani')
lbl5.grid(row=4, column=1)

mainloop()