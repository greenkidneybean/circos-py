# Functions:
# - circos_input_file
# - format_dataframe
# - make_top_karyotype
# - make_bands_karyotype
# - generate_circos_links

import argparse
import datetime
import glob
import numpy as np
import os
import pandas as pd
import shutil
import subprocess

def circos_input_file(file, spec_dict):
    """
    Custom create pandas dataframe from .csv circos_input_file

    Strip spaces and hyphens in column names
    Remove empty rows
    """
    output_file_name = spec_dict['output_file_name']
    df = pd.read_csv(file)
    # strip spaces and hyphens in column names
    # this could cause a problem in the future
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('-','_')
    # drop any empty rows
    df = df.dropna(axis=0, how='all')
    # add circos_time column for timepoint labels (e.g. "Day000")
    df['circos_time'] = 'Day' + df.timepoint.str.split('-').str[1]
    # count the number of sequences in the clone
    df['total_clone_count'] = df.groupby('clone')['clone'].transform('count')
    # count the number of timepoints the clone shows up in
    df['timepoint_clone_count'] = df.groupby(['timepoint','clone'])['clone'].transform('count')
    # sort the df by time, then by clone count by timepoint, then with ascending clone numbers
    df = df.sort_values(['timepoint', 'timepoint_clone_count', 'clone'], ascending=True, na_position='first')
    df.to_csv(f'sorted_timepoints_{output_file_name}.csv', sep=',', index=False, header=True)
    df = df.reset_index(drop=True)
    if 'spec_list' in spec_dict:
        # downselect dataframe if looking for just h7 or stem sequences
        df = df[df['spec'].isin(spec_dict['spec_list'])]
    return df

def format_dataframe(dataframe, spec_dict):
    """
    use this to format an existing dataframe
    """
    df = dataframe
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('-','_')
    # drop any empty rows
    df = df.dropna(axis=0, how='all')
    # add circos_time column for timepoint labels (e.g. "Day000")
    df['circos_time'] = 'Day' + df.timepoint.str.split('-').str[1]
    # count the number of sequences in the clone
    df['total_clone_count'] = df.groupby('clone')['clone'].transform('count')
    # count the number of timepoints the clone shows up in
    df['timepoint_clone_count'] = df.groupby(['timepoint','clone'])['clone'].transform('count')
    # sort the df by time, then by clone count by timepoint, then with ascending clone numbers
    df = df.sort_values(['timepoint', 'timepoint_clone_count', 'clone'], ascending=True, na_position='first')
    #df.to_csv(f'sorted_timepoints_{output_file_name}.csv', sep=',', index=False, header=True)
    if 'spec_list' in spec_dict:
        # downselect dataframe if looking for just h7 or stem sequences
        df = df[df['spec'].isin(spec_dict['spec_list'])]
    df.reset_index(drop=True, inplace=True)
    return df

def make_top_karyotype(input_dataframe, spec_dict):
    """
    make the top of the circos karyotype
    """
    output_file_name = spec_dict['output_file_name']
    karyotype = input_dataframe['circos_time'].value_counts(sort=False).sort_index().to_frame(name='END')
    karyotype['ID'] = karyotype.index
    karyotype.reset_index(drop=True, inplace=True)
    karyotype['#chr'] = 'chr'
    karyotype['-'] = '-'
    karyotype['START'] = 0
    karyotype['LABEL'] = 'd' + karyotype['ID'].str[3:].apply(int).apply(str) + ' (' + karyotype['END'].apply(str) + ')'
    karyotype['COLOR'] = ['chr'+ str(i+1) for i in range(len(karyotype))]
    cols = ['#chr', '-', 'ID', 'LABEL', 'START', 'END', 'COLOR']
    karyotype = karyotype[cols]
    karyotype.to_csv(f'my_karyotype.txt', sep='\t', index=False)
    return karyotype

def make_bands_karyotype(input_dataframe, spec_dict):
    output_file_name = spec_dict['output_file_name']
    # create bands
    #create band start and stop points
    band_start = [val for i in input_dataframe.groupby('timepoint')['timepoint'].count().tolist() for val in range(i)]
    band_stop = [x+1 for x in band_start]

    # add them as a column
    input_dataframe['#band'] = 'band'
    input_dataframe['band_start'] = band_start
    input_dataframe['band_stop'] = band_stop

    input_dataframe['band_color'] = ''
    a = {True:'gneg',False:'gpos25'}
    b = True

    for i in range(len(input_dataframe)):
        if i == 0:
            input_dataframe.loc[i,'band_color'] = a[b]
            pass
        # for matching above row
        else:
            above = input_dataframe.loc[i-1,'clone']
            current = input_dataframe.loc[i,'clone']
            if above == current:
                input_dataframe.loc[i,'band_color'] = a[b]
            else:
                b = not b
                input_dataframe.loc[i,'band_color'] = a[b]

    # create separate bands df
    bands = input_dataframe[['#band', 'circos_time', 'seq_id', 'seq_id', 'band_start', 'band_stop', 'band_color']].copy()

    # save the bands file (tab delimited)
    bands.to_csv(f'bands.txt', sep='\t', index=False, header=True)

    # append to karyotype file
    with open(f'my_karyotype.txt', 'a') as f:
        bands.to_csv(f, sep='\t', index=False )

    return bands

def hue_list(samples=20, color=None):
    '''
    Generate a list of hues evenly spaced based on the sample number

    hue### goes from 0-360
    '''

    if color == None:
        color = 'all'

    color_list = {
        'all':[0,360],
        'red_yellow':[0,60],
        'yellow_green':[60,140],
        'green_blue':[140,255],
        'blue_purple':[185,275],
        'purple_pink':[275,310],
        'blue':[185,235],
        'red':[0,20],
        'red_orange':[0,30]}

    # check to see of the color is in the list

    for key,item in color_list.items():
        if key == color:
            return ['hue'+str(x).zfill(3) for x in np.linspace(item[0], item[1], samples, dtype=int)]

# generate links
def generate_circos_links(input_dataframe, spec_dict):
    output_file_name = spec_dict['output_file_name']

    link_df = input_dataframe[(input_dataframe['spec'].isin(spec_dict['spec_list'])) & (input_dataframe['clone'].isnull() == False)]

    clones = link_df.groupby(['circos_time','clone'], sort=False)['band_start'].min().reset_index()
    clones['band_stop'] = link_df.groupby(['circos_time', 'clone'], sort=False)['band_stop'].max().reset_index()['band_stop']
    clones = clones.sort_values(['clone','circos_time']).reset_index(drop=True)

    # generate a links df
    cols = clones.columns.tolist()
    df_1 = pd.DataFrame(columns=cols)
    df_2 = pd.DataFrame(columns=cols)

    for i,row in clones.iterrows():
        below = i + 1
        # if statement checks for last row in the clones dataframe
        if below > clones.index.max():
            continue
        else:
            if row['clone'] == clones.iloc[below]['clone']:
                #print("here's clone: ",row['clone'])
                #print(row)
                df_1.loc[i] = row
                df_2.loc[i] = clones.iloc[below]
            else:
                continue

    # change column titles in df_2 before concat into links
    df_2.columns = ['circos_time_2', 'clone_2', 'band_start_2', 'band_stop_2']
    # concat the df_1 and df_1 to create base for links document
    links = pd.concat([df_1, df_2], axis=1)
    links = links.sort_values(['circos_time','band_start']).reset_index(drop=True)
    # band start/stop need to be converted back to integers
    links[['band_start','band_stop','band_start_2','band_stop_2']] = links[['band_start','band_stop','band_start_2','band_stop_2']].astype(int)

    # add the unique colors here
    link_keys = links['clone'].unique().tolist()
    link_hues = hue_list(len(link_keys), color=spec_dict['color']) # this is gonna be a problem
    link_values = ['color='+i+'_a2' for i in link_hues]
    link_color_dict = dict(zip(link_keys, link_values))
    links['link_color'] = links['clone'].map(link_color_dict)
    final_links = links[['circos_time', 'band_start', 'band_stop', 'circos_time_2', 'band_start_2','band_stop_2', 'link_color']].copy()
    final_links=final_links.rename(columns={'circos_time':'#ciros_time'})

    # write link files
    final_links.to_csv(f'links_{output_file_name}.txt', sep='\t', index=False, header=True)

    # this is dangerous because it will layer the links.txt with each iteration
    if os.path.isfile('links.txt') is False:
        final_links.to_csv('links.txt', sep='\t', index=False, header=True)
    else:
        with open('links.txt', 'a') as f:
            final_links.to_csv(f, sep='\t', index=False)

    return final_links
