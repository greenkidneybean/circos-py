#!/usr/bin/env python3

################################################################################
#
# Copyright (c) 2018 Michael Chambers.  All rights reserved.
#
# @version: 0.8.0
# @author: Michael Chambers
# @license: MIT (http://opensource.org/licenses/MIT)
#
################################################################################

'''
TODO:
dump all images into generated project folder
better names for files
handle .csv and .xls file input
easily replicate environment (Docker?)
import csv to generate dictionaries
print message functions
function to make file paths
option for all images or specific color layer
specify full path to project folder if saving somewhere else
'''

# imports may not be necessary with the circos module imported
import argparse
from circos import *
import datetime
import glob
import numpy as np
import os
import pandas as pd
import shutil
import subprocess


# arguments
parser = argparse.ArgumentParser()
parser.add_argument('input_excel', type=str, help='input full name of excel workbook')
parser.add_argument('-o', '--output_dir', default=f'{datetime.datetime.now():circos_plots_%y%m%d-%H%M%S}', type=str, help='input the project folder name and path')
args = parser.parse_args()

# setup sample dictionaries

all_spec_dict = {'output_file_name':'h7-stem',
                 'circos_conf_file':'circos.conf'}
h7_spec_dict = {'output_file_name':'h7',
                'spec_list':['H7 sp', 'spec_2'],
                'color':'red_orange',
                'circos_conf_file':'circos_h7.conf'}
stem_spec_dict = {'output_file_name':'stem',
                  'spec_list':['H7 dp', 'spec_1'],
                  'color':'blue',
                  'circos_conf_file':'circos_stem.conf'}
dict_list = [all_spec_dict, h7_spec_dict, stem_spec_dict]


# assign variables
input_file = args.input_excel
project_folder = args.output_dir

# make paths
home_dir = os.getcwd()
project_dir = home_dir + '/' + project_folder
input_files_folder = project_dir + '/input_files'
samples_dir = project_dir + '/samples'
circos_conf_dir = home_dir + '/circos_conf'

# make directories
os.makedirs(project_dir, exist_ok=True)
os.makedirs(input_files_folder, exist_ok=True)
os.makedirs(samples_dir, exist_ok=True)

# identify all sheets in Excel input file
x1 = pd.ExcelFile(input_file)
sheets = x1.sheet_names

# work through each sheet in the Excel input file
for i in sheets:
    os.chdir(project_dir)
    sample_id = i
    sample_input_file = sample_id + '_input.csv'
    start_df = x1.parse(i)
    start_df.to_csv(input_files_folder + '/' + sample_input_file, index=False)

    print()
    print('---')
    print(f'Sample ID: {sample_id}')
    print(f'Input File: {sample_input_file}')
    print('---')

    # file paths
    current_dir = os.getcwd()
    sample_dir = samples_dir + '/' + sample_id
    images_dir = current_dir + '/all_images'
    sample_image_dir = images_dir + '/' + sample_id

    print()
    print('---')
    print('Generate Directory Tree')
    print(f'Current Working Directory: {current_dir}')
    print('---')
    folders_list = [sample_dir, images_dir, sample_image_dir]
    for i in folders_list:
        os.makedirs(i, exist_ok=True)

    # this is the biggie
    for i in dict_list:
        # navigate to sample directory
        os.chdir(sample_dir)
        # make directories
        img_fld = sample_image_dir + '/' + i['output_file_name']
        current_folder_name = i['output_file_name']
        os.makedirs(current_folder_name, exist_ok=True)
        os.makedirs(img_fld, exist_ok=True)
        # go to directory
        os.chdir(current_folder_name)
        # make circos files
        #df = circos_input_file(sample_input_file, i) # spits out sorted file
        df = format_dataframe(start_df, i)
        make_top_karyotype(df, i)
        make_bands_karyotype(df, i)
        for a in dict_list[1:]:
            generate_circos_links(df, a)

    # run circos
        for i in dict_list:
            circos_conf = circos_conf_dir + '/' + i['circos_conf_file']
            circos_plot_name = sample_id + '_' + i['output_file_name']
            print()
            print('---')
            print('Running Circos')
            print(f'Circos configuration file path: {circos_conf}')
            print(f'Output plot name: {circos_plot_name}')
            print('---')
            subprocess.run('circos -conf {0} -outputfile {1}'.format(circos_conf, circos_plot_name), shell=True)

        # copy images to main image folder
        print()
        print('---')
        print('Copying {sample_id} Circos Plots to "images" Directory')
        print('---')
        for file in glob.glob('*.png'):
            shutil.copy(file, img_fld)
        for file in glob.glob('*.svg'):
            shutil.copy(file, img_fld)
        print()
