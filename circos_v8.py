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
import csv to generate dictionaries

'''



import argparse
import circos
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
                'spec_list':['H7 sp', 'sp'],
                'color':'red_orange',
                'circos_conf_file':'circos_h7.conf'}
stem_spec_dict = {'output_file_name':'stem',
                  'spec_list':['H7 dp', 'dp'],
                  'color':'blue',
                  'circos_conf_file':'circos_stem.conf'}
dict_list = [all_spec_dict, h7_spec_dict, stem_spec_dict]


# assign variables
input_file = args.input_excel
project_folder = args.output_dir


# make files
home_dir = os.getcwd()
input_files_folder = home_dir + '/input_files'
os.makedirs(input_files_folder, exist_ok=True)
participants_dir = home_dir + '/participants'
os.makedirs(participants_dir, exist_ok=True)

# make .csv input files
x1 = pd.ExcelFile(input_file)
sheets = x1.sheet_names

for i in sheets:
    os.chdir(home_dir)
    participant_id = i
    participant_input_file = participant_id + '_input.csv'
    start_df = x1.parse(i)
    start_df.to_csv(input_files_folder + '/' + participant_input_file, index=False)

    print()
    print('---')
    print(f'Participant ID: {participant_id}')
    print(f'Input File: {participant_input_file}')
    print('---')
    print()

    # file paths
    home_dir = os.getcwd()
    indiv_participant_dir = participants_dir + '/' + participant_id
    images_dir = home_dir + '/images'
    participant_image_dir = images_dir + '/' + participant_id
    circos_conf_dir = home_dir + '/circos_conf'

    print()
    print('---')
    print('Generate Directory Tree')
    print(f'Current Working Directory: {home_dir}')
    print('---')
    print()
    folders_list = [indiv_participant_dir, images_dir, participant_image_dir]
    for i in folders_list:
        os.makedirs(i, exist_ok=True)

    # this is the biggie
    for i in dict_list:
        # navigate to participant directory
        os.chdir(indiv_participant_dir)
        # make directories
        img_fld = participant_image_dir + '/' + i['output_file_name']
        current_folder_name = i['output_file_name']
        os.makedirs(current_folder_name, exist_ok=True)
        os.makedirs(img_fld, exist_ok=True)
        # go to directory
        os.chdir(current_folder_name)
        # make circos files
        #df = circos_input_file(participant_input_file, i) # spits out sorted file
        df = format_dataframe(start_df, i)
        make_top_karyotype(df, i)
        make_bands_karyotype(df, i)
        for a in dict_list[1:]:
            generate_circos_links(df, a)

    # run circos
        for i in dict_list:
            circos_conf = circos_conf_dir + '/' + i['circos_conf_file']
            circos_plot_name = participant_id + '_' + i['output_file_name']
            print()
            print('---')
            print('Running Circos')
            print(f'Circos configuration file path: {circos_conf}')
            print(f'Output plot name: {circos_plot_name}')
            print('---')
            print()
            subprocess.run('circos -conf {0} -outputfile {1}'.format(circos_conf, circos_plot_name), shell=True)

        # copy images to main image folder
        print()
        print('---')
        print('Copying Circos Plots')
        print('---')
        print()
        for file in glob.glob('*.png'):
            shutil.copy(file, img_fld)
        for file in glob.glob('*.svg'):
            shutil.copy(file, img_fld)
        print()
