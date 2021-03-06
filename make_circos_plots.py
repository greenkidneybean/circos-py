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
better names for files
handle .csv and .xls file input
easily replicate environment (Docker?)
import csv to generate dictionaries
print message functions
function to make file paths
option for all images or specific color layer
specify full path to project folder if saving somewhere else
run circos and specify links file rather than specific circos.conf?
run circos once if current_spec is "all-data"
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
# includes circos.conf files to be used (call different link files)

all_spec_dict = {'output_file_name':'all-data',
                 'circos_conf_file':'circos.conf'}
spec_dict_1 = {'output_file_name':'spec_1',
                'spec_list':['H7 sp', 'spec_1'], # feature #1 in "spec" column
                'color':'red_orange',
                'circos_conf_file':'circos_h7.conf'}
spec_dict_2 = {'output_file_name':'spec_2',
                  'spec_list':['H7 dp', 'spec_2'], # feature #2 in "spec" column
                  'color':'blue',
                  'circos_conf_file':'circos_stem.conf'}
dict_list = [all_spec_dict, spec_dict_1, spec_dict_2]

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

### run a test to check for .csv or .xlsx file and generate sheet

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
        current_spec = i['output_file_name']
        os.makedirs(current_spec, exist_ok=True)
        os.makedirs(img_fld, exist_ok=True)
        # go to directory
        os.chdir(current_spec)
        # make circos files
        #df = circos_input_file(sample_input_file, i) # spits out sorted file
        df = format_dataframe(start_df, i)
        make_top_karyotype(df, i)
        make_bands_karyotype(df, i)
        for a in dict_list[1:]:
            generate_circos_links(df, a)

        # run circos
        for i in dict_list:
            #circos_conf = circos_conf_dir + '/' + i['circos_conf_file']
            current_circos_spec =  i['output_file_name']
            circos_conf = f'{circos_conf_dir}/circos.conf'
            circos_plot_name = f'{sample_id}_{current_circos_spec}'

            link_file=f'links_{current_circos_spec}.txt'
            print()
            print('---')
            print('Running Circos')
            print(f'Circos configuration file path: {circos_conf}')
            print(f'Output plot name: {circos_plot_name}')
            print('---')
            subprocess.run('circos -conf {0} -outputfile {1} -param links/link/file={2}'.format(circos_conf, circos_plot_name, link_file), shell=True)

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
