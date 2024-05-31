'''
Functions dealing with setting up configuration parameters.
Main function collects tokens from filenames in given path,
parses the tokens and writes the parameters to a dictionary.
'''

import os, argparse, math, re
import pickle, shutil, datetime

import utils
import pandas as pd
from glob import iglob

def make_results_folders(input_path, output_path):

    '''Generate folder hierarchy for each output step.'''

    bg_corrected_path = os.path.join(output_path, 'BackgroundCorrected') #background_removal
    montaged_path = os.path.join(output_path, 'MontagedImages') #montage
    aligned_path = os.path.join(output_path, 'AlignedImages') #alignment
    cropped_path = os.path.join(output_path, 'CroppedImages') #shift_crop
    results = os.path.join(output_path, 'OverlaysTablesResults') #overlay_tracks and extract_cell_info
    cell_masks = os.path.join(output_path, 'CellMasks') # segmentation
    qc_path = os.path.join(output_path, 'QualityControl') #segmentation visualization
    stacking_scratch_path = os.path.join(output_path, 'StackingTemp')

    output_dir_names = ['BackgroundCorrected', 'MontagedImages',
         'AlignedImages', 'CroppedImages', 'QualityControl',
         'OverlaysTablesResults', 'CellMasks', 'StackingTemp']
    output_subdirs = [bg_corrected_path, montaged_path,
        aligned_path, cropped_path, qc_path, results, cell_masks]

    utils.create_folder_hierarchy(output_subdirs, output_path)

    var_dict = {'RawImageData': input_path}
    for output_dir_name, output_subdir in zip(
        output_dir_names, output_subdirs):

        var_dict[output_dir_name] = output_subdir

    return var_dict

def parse_tokens(filenames, robo_num):
    '''
    Creates data frame of all files in directory with tokens parsed into separate columns
    '''
    files = pd.DataFrame(filenames, columns = ['Filename'])
    if robo_num == 0:
        files[['PID','ExptName','Timepoint','Hours','Well','Panel','Channel','BurstInterval',
                   'Zstep','Zstep_size']] = files['Filename'].str.split('_', expand = True)
        print(list(files))
        files[['Hours','BurstIndex']] = files['Hours'].str.split('-', expand = True)
        files['Zstep_size'] = files['Zstep_size'].str.replace('.tif', '')
        files['Timepoint'] = files['Timepoint'].str.replace('T', '')
        files[['Timepoint','Panel','BurstIndex','Zstep']] = files[['Timepoint','Panel','BurstIndex','Zstep']].astype(int)
        files.sort_index(level=['Well','Timepoint','Channel','Panel','BurstIndex','Zstep'], inplace = True)
    elif robo_num == 3:
        files[['PID','ExptName','Timepoint','Hours','Well','Panel','Channel']] = files['Filename'].str.split('_', expand = True)
        files['Timepoint'] = files['Timepoint'].str.replace('T', '')
        files[['Timepoint','Panel']] = files[['Timepoint','Panel']].astype(int)
        files.sort_index(level=['Well','Timepoint','Panel','Channel'], inplace = True)
    return files

def get_exp_params_general(var_dict, all_files, morph_channel, robo_num):
    '''
    Using filenames in input directory,
    collect experiment parameters (wells, timepoints, channels),
    add them to var_dict.

    Currently supported naming schemes
    Robo3: PIDdate_ExptName_Timepoint_Hours_Well_MontageNumber_Channel.tif
    Robo4 epi: PIDdate_ExptName_Timepoint_Hours_Well_MontageNumber_Channel_FilterDet_Camera.tif
    Robo4 confocal: PIDdate_ExptName_Timepoint_Hours_Well_MontageNumber_FilterDet1_FilterDet2_[FilterDet3]_Channel_DepthIndex_DepthIncrement_Camera.tif
    Robo0: PIDdate_ExptName_Timepoint_Hours-BurstIndex_Well_MontageNumber_Channel_TimeIncrement_DepthIndex_DepthIncrement.tif
    '''
    var_dict['AnalyzedFiles'] = all_files
    if robo_num == 1:
        num_tokens = len(os.path.basename(all_files[0]).split('_'))
        print('Number of tokens:', num_tokens)
        assert num_tokens == 7 or num_tokens == 10 or num_tokens == 13, 'Auto-detect token standard requires filenames have either 7, 10, or 13 tokens'
        var_dict['NumberTokens'] = num_tokens
        if num_tokens == 7:
            var_dict['RoboNumber'] = 3
        elif num_tokens == 10:
            var_dict['RoboNumber'] = 0
        elif num_tokens == 13:
            var_dict['RoboNumber'] = 4
        robo_num = var_dict['RoboNumber']
    else:
        var_dict['RoboNumber'] = robo_num
    print('Token standard: Robo', var_dict['RoboNumber'])
    var_dict['TimePoints'] = utils.get_timepoints(all_files)
    var_dict['Wells'] = utils.get_wells(all_files)
    var_dict['Channels'] = utils.get_channels(
        all_files, var_dict['RoboNumber'], light_path=var_dict['ImagingMode'])
    var_dict['MorphologyChannel'] = utils.get_ref_channel(morph_channel, var_dict['Channels'])
    print('Morphology channel: %s' % var_dict['MorphologyChannel'])
    var_dict['PlateID'] = utils.get_plate_id(all_files)
    var_dict['Bursts'] = utils.get_burst_iter(all_files)
    var_dict['BurstIDs'] = utils.get_bursts(all_files)
    var_dict['Depths'] = utils.get_depths(all_files, var_dict['RoboNumber'])
    if 'ZMAX' not in var_dict['Depths'] and 'ZAVG' not in var_dict['Depths']:
        var_dict['Depths'] = [int(zdepth) for zdepth in var_dict['Depths']]
    var_dict['Resolution'] = -1 #0 is 8-bit, -1 is 16-bit

    return var_dict

def get_array_dimensions(all_files, num_cols, num_rows, var_dict):
    if num_cols is not None and num_rows is not None:
        var_dict['NumberVerticalImages'] = num_cols
        var_dict['NumberHorizontalImages'] = num_rows
    else:
        array_size = max([int(os.path.basename(x).split('_')[5]) for x in all_files])
        assert is_perfect_square(array_size), 'Array size is not square. Must enter the array dimensions.'
        var_dict['NumberHorizontalImages'] = int(math.sqrt(array_size))
        var_dict['NumberVerticalImages'] = int(math.sqrt(array_size))
    print('Array size: %s x %s' % (var_dict['NumberHorizontalImages'], var_dict['NumberVerticalImages']))


def is_perfect_square(array_size):
    if not math.sqrt(array_size) - int(math.sqrt(array_size)):
        return True

def get_filenames(files_path):
    '''
    Returns list of all tiff (non-fiducial) filenames in a directory as basenames.
    '''
    filenames_full = utils.get_all_files(files_path)
    filenames_basenames = [os.path.basename(x) for x in filenames_full]

    return filenames_basenames

def check_data(var_dict):
    # parse filenames into dataframe and include only user-selected Wells and Timepoints
    files_df = parse_tokens([os.path.basename(x) for x in var_dict['AnalyzedFiles']], var_dict['RoboNumber'])
    timepoints = set([int(x.replace('T','')) for x in var_dict['TimePoints']])
    files_df = files_df[files_df['Well'].isin(var_dict['Wells']) & files_df['Timepoint'].isin(timepoints)]
    files_df['Channel'] = files_df['Channel'].str.replace('.tif', '')

    # get list of wells with missing panels, timepoints, and/or channels
    incomplete_wells = []
    extra_wells = []

    num_panels = var_dict['NumberHorizontalImages'] * var_dict['NumberVerticalImages']
    panel_counts = files_df.groupby(['Well','Timepoint','Channel']).size().reset_index(name='NumberOfPanels')
    incomplete_wells.extend(panel_counts.loc[panel_counts['NumberOfPanels'] < num_panels, 'Well'].tolist())
    extra_wells.extend(panel_counts.loc[panel_counts['NumberOfPanels'] > num_panels, 'Well'].tolist())

    num_timepoints = len(var_dict['TimePoints'])
    timepoint_counts = files_df.drop_duplicates(subset=['Well','Channel','Timepoint']) \
        .groupby(['Well','Channel']).size().reset_index(name='NumberOfTimepoints')
    incomplete_wells.extend(timepoint_counts.loc[timepoint_counts['NumberOfTimepoints'] < num_timepoints, 'Well'].tolist())
    extra_wells.extend(timepoint_counts.loc[timepoint_counts['NumberOfTimepoints'] > num_timepoints, 'Well'].tolist())

    num_channels = len(var_dict['Channels'])
    channel_counts = files_df.groupby(['Well','Timepoint','Panel']).size().reset_index(name='NumberOfChannels')
    incomplete_wells.extend(channel_counts.loc[channel_counts['NumberOfChannels'] < num_channels, 'Well'].tolist())
    extra_wells.extend(channel_counts.loc[channel_counts['NumberOfChannels'] > num_channels, 'Well'].tolist())

    if len(incomplete_wells) != 0:
        # filter dataframe by wells with incomplete data
        incomplete_data = files_df[files_df['Well'].isin(set(incomplete_wells))]

        # create duplicate dataframe for holding panel lists
        incomplete_data_output = incomplete_data[['Well', 'Channel']].drop_duplicates()

        for tp in timepoints:

            # subset data by current timepoint, create a column with list of existing panels
            incomplete_data_tp = incomplete_data.loc[incomplete_data['Timepoint'] == tp] \
                .groupby(['Well', 'Channel'])['Panel'] \
                .apply(list) \
                .reset_index(name = 'T' + str(tp) + '_tiles')

            # create a column for list of missing panels and convert list to comma-separated string
            incomplete_data_tp['T' + str(tp) + '_missing-tiles'] = incomplete_data_tp['T' + str(tp) + '_tiles'] \
                .apply(lambda x: [str(i) for i in range(1, num_panels+1) if i not in x]) \
                .apply(','.join)

            # remove column with list of existing panels
            incomplete_data_tp.drop(['T' + str(tp) + '_tiles'], axis = 1, inplace = True)

            # if dataframe is not empty
            if len(incomplete_data_tp) != 0:
                # merge timepoint dataframe with bywell dataframe
                incomplete_data_output = pd.merge(incomplete_data_output, incomplete_data_tp, on = ['Well', 'Channel'], how = 'left')

                # convert NaNs (well/channel/timepoints missing all panels) to a list of all panels
                incomplete_data_output.iloc[:,-1].fillna(','.join([str(i) for i in range(1, num_panels + 1)]), inplace = True)

            # else if dataframe is empty (i.e. all wells/channels at the current timepoint are missing all panels)
            else:
                incomplete_data_output['T' + str(tp) + '_missing-tiles'] = ','.join([str(i) for i in range(1, num_panels + 1)])

        # output to csv
        incomplete_data_output.to_csv(os.path.join(var_dict['GalaxyOutputPath'], var_dict['ExperimentName'] + '_missing-images.csv'), index = False)

        # throw error if missing images
        if len(incomplete_wells) != 0:
            raise ValueError('Dataset is missing images (also saved as csv in output directory):\n\n%s' % incomplete_data_output.to_string(index = False, index_names = False))

    if len(extra_wells) != 0:
        # filter dataframe by wells with extra data
        extra_data = files_df[files_df['Well'].isin(set(extra_wells))]

        # create duplicate dataframe for holding panel lists
        extra_data_output = extra_data[['Well', 'Channel']].drop_duplicates()

        for tp in timepoints:

            # subset data by current timepoint, create a column with list of existing panels
            extra_data_tp = extra_data.loc[extra_data['Timepoint'] == tp] \
                .groupby(['Well', 'Channel'])['Panel'] \
                .apply(list) \
                .reset_index(name = 'T' + str(tp) + '_tiles')

            def count_duplicates(lst):
                #count duplicated tiles
                duplicates_dict = {}
                for x in lst:
                    if lst.count(x) > 1:
                        if x not in duplicates_dict:
                            duplicates_dict[x] = lst.count(x)
                return duplicates_dict

            extra_data_tp['T' + str(tp) + '_extra-tiles'] = extra_data_tp['T' + str(tp) + '_tiles'].apply(count_duplicates)

            # remove column with list of existing panels
            extra_data_tp.drop(['T' + str(tp) + '_tiles'], axis = 1, inplace = True)

            # if dataframe is not empty
            if len(extra_data_tp) != 0:
                # merge timepoint dataframe with bywell dataframe
                extra_data_output = pd.merge(extra_data_output, extra_data_tp, on = ['Well', 'Channel'], how = 'left')

                # convert NaNs (well/channel/timepoints missing all panels) to a list of all panels
                extra_data_output.iloc[:,-1].fillna(','.join([str(i) for i in range(1, num_panels + 1)]), inplace = True)

            # else if dataframe is empty (i.e. all wells/channels at the current timepoint are missing all panels)
            else:
                extra_data_output['T' + str(tp) + '_extra-tiles'] = ','.join([str(i) for i in range(1, num_panels + 1)])

        # output to csv
        extra_data_output.to_csv(os.path.join(var_dict['GalaxyOutputPath'], var_dict['ExperimentName'] + '_extra-images.csv'), index = False)

        # throw error if missing images
        if len(extra_wells) != 0:
            raise ValueError('Dataset has extra tiles (also saved as csv in output directory):\n\n%s' % extra_data_output.to_string(index = False, index_names = False))

def get_timepoint_hours(selected_timepoints, input_path, output_path):
    '''Looks for log files in input path, parses the dates/times of the first image, and saves a csv with the timepoint-hours conversion'''
    first_lines = []
    log_paths = [x for x in iglob(os.path.join(input_path, '*.log')) if 'ImageStart' not in os.path.basename(x)]
    if len(log_paths) > 0:
        # sort log files by timepoint
        log_paths.sort(key=lambda x:int(re.findall(r'(?<=-T)\d{1,2}(?=\.log)', x)[0]))
        # get list of timepoints
        log_timepoints = [re.findall(r'(?<=-T)\d{1,2}(?=\.log)', x)[0] for x in log_paths]
        # read in first acquired image of each timepoint
        for log in log_paths:
            with open(log, 'r') as l:
                first_lines.append(l.readline())

        start_datetimes = [datetime.datetime.strptime(x.split(' -- ')[0], '%y %m %d %H:%M:%S') for x in first_lines]
        start_dates = [x.strftime('%y-%m-%d') for x in start_datetimes]
        start_times = [x.strftime('%H:%M:%S') for x in start_datetimes]
        start_imgs = [x.split(' -- ')[1] for x in first_lines]

        # calculate time delta and convert to hours
        elapsed_hours = [round(((x-start_datetimes[0]).total_seconds())/3600, 1) for x in start_datetimes]

        tp_hours = open(os.path.join(output_path, 'timepoint_hours.csv'), 'w')
        tp_hours.write(','.join(['Timepoint', 'ElapsedHours', 'StartDate', 'StartTime', 'FirstImage', '\n']))
        for idx in range(0,len(first_lines)):
            tp_hours.write(','.join([str(log_timepoints[idx]), str(elapsed_hours[idx]), start_dates[idx], start_times[idx], start_imgs[idx], '\n']))
        tp_hours.close()

        # get hours for selected timepoints only
        selected_timepoints = [x.replace('T', '') for x in selected_timepoints]
        selected_timepoints_idx = [idx for idx, x in enumerate(log_timepoints) if x in selected_timepoints]

        return [elapsed_hours[i] for i in selected_timepoints_idx]


def main():
    '''Point of entry.'''

    # Argument parsing
    parser = argparse.ArgumentParser(description="Process cell data.")
    parser.add_argument("input_path",
        help="Folder path to input data.")
    parser.add_argument("output_path",
        help="Folder path to ouput results.")
    parser.add_argument("dir_structure", help="Type of directory structure.")
    parser.add_argument("robo_num",
        type=int,
        help="Robo number")
    parser.add_argument("imaging_mode",
        help="Light path (epi or confocal).")
    parser.add_argument("morph_channel",
        help="A unique string corresponding to morphology channel.")
    parser.add_argument("pixel_overlap",
        type=int,
        help="Number of pixels to overlap during stitching.")
    parser.add_argument("wells_toggle",
        help="Chose whether to include or exclude specified wells.")
    parser.add_argument("timepoints_toggle",
        help="Chose whether to include or exclude specified timepoints.")
    parser.add_argument("channels_toggle",
        help="Chose whether to include or exclude specified channels.")
    parser.add_argument("--num_cols", dest="num_cols", type=int,
        help="Number of horizontal images in montage.")
    parser.add_argument("--num_rows", dest="num_rows", type=int,
        help="Number of vertical images in montage.")
    parser.add_argument("check_data_option",
        help="Chose whether to check for wells with incomplete data.")
    parser.add_argument("outfile",
        help="Name of output dictionary.")
    parser.add_argument("--min_cell",
        dest="min_cell", type=int, default=50,
        help="Minimum feature size considered as cell.")
    parser.add_argument("--max_cell",
        dest="max_cell", type=int, default=2500,
        help="Maximum feature size considered as cell.")
    parser.add_argument("--threshold_percent", "-tp",
        dest="threshold_percent", type=float, default=0.1,
        help="Threshold value as a percent of maximum intensity.")
    parser.add_argument("--chosen_wells", "-cw",
        dest = "chosen_wells", default = '',
        help="Specify wells to include or exclude"       )
    parser.add_argument("--chosen_timepoints", "-ct",
        dest = "chosen_timepoints", default = '',
        help="Specify timepoints to include or exclude.")
    parser.add_argument("--chosen_channels", "-cc",
        dest = "chosen_channels", default = '',
        help="Specify channels to include or exclude.")
    args = parser.parse_args()

    # Set up I/O parameters
    input_path = str.strip(args.input_path)
    output_path = str.strip(args.output_path)
    dir_structure = args.dir_structure
    robo_num = args.robo_num
    morph_channel = str.strip(args.morph_channel)
    check_data_option = int(args.check_data_option)
    outfile = args.outfile

    # Confirm given folders exist
    assert os.path.exists(input_path), 'Confirm that the input folder (%s) exists.' % input_path
    assert 'GXYTMP' in output_path, 'Output folder must contain the string "GXYTMP" (case sensitive)'
    assert os.path.exists(os.path.split(output_path)[0]), 'Confirm that the output path parent folder (%s) exists.' % os.path.split(output_path)[0]
    assert re.match('^[a-zA-Z0-9_-]+$', os.path.split(output_path)[1]), 'Confirm that the output folder name (%s) does not contain special characters.' % os.path.split(output_path)[1]
    assert '/gladstone/finkbeiner/' in output_path, 'Output folder must be in the new server'
    
    # Confirm that morphology channel is given
    assert morph_channel != '', 'Confirm that you have provided a morphology channel.'

    # Set up dictionary parameters
    utils.create_dir(output_path)
    var_dict = make_results_folders(input_path, output_path)
    var_dict['ImagingMode'] = args.imaging_mode
    var_dict['IntensityThreshold'] = args.threshold_percent
    var_dict['DirStructure'] = dir_structure
    var_dict['ImagePixelOverlap'] = args.pixel_overlap
    var_dict['InputPath'] = input_path
    var_dict['GalaxyOutputPath'] = output_path
    all_files = utils.get_all_files_all_subdir(input_path)
    assert len(all_files) > 0, 'No files to process.'
    var_dict['ExperimentName'] = os.path.basename(all_files[0]).split('_')[1]
    var_dict = get_exp_params_general(var_dict, all_files, morph_channel, robo_num)

    get_array_dimensions(all_files, args.num_cols, args.num_rows, var_dict)

    start_time = datetime.datetime.utcnow()

    # Handle processing specified wells
    user_chosen_wells = args.chosen_wells.strip()
    if user_chosen_wells != '':
        user_chosen_wells = utils.get_iter_from_user(user_chosen_wells, 'wells')
        print('Initial wells:', var_dict['Wells'])
        if args.wells_toggle == 'exclude':
            var_dict['Wells'] = [x for x in var_dict['Wells']  if x not in user_chosen_wells]
        elif args.wells_toggle == 'include':
            assert set(user_chosen_wells).issubset(set(var_dict['Wells'])), 'Confirm that the selected wells (%s) exist in the dataset' % user_chosen_wells
            var_dict['Wells'] = user_chosen_wells
    print('Selected Wells:', var_dict['Wells'])

    # Handle processing specified timepoints
    user_chosen_timepoints = args.chosen_timepoints.strip()
    if user_chosen_timepoints != '':
        user_chosen_timepoints = utils.get_iter_from_user(user_chosen_timepoints, 'timepoints')
        print('Initial timepoints', var_dict['TimePoints'])
        if args.timepoints_toggle == 'exclude':
            var_dict['TimePoints'] = [x for x in var_dict['TimePoints'] if x not in user_chosen_timepoints]
        elif args.timepoints_toggle == 'include':
            assert set(user_chosen_timepoints).issubset(set(var_dict['TimePoints'])), 'Confirm that the selected timepoints (%s) exist within the dataset' % user_chosen_timepoints
            var_dict['TimePoints'] = user_chosen_timepoints
    print('Selected timepoints:', var_dict['TimePoints'])

    # parse first line of log files, output timepoint-hours csv, save to dictionary
    var_dict['ElapsedHours'] = get_timepoint_hours(var_dict['TimePoints'], input_path, output_path)
    print('Elapsed hours for selected timepoints:', var_dict['ElapsedHours'])

    # Handle processing specified channels
    user_chosen_channels = args.chosen_channels.strip()
    if user_chosen_channels != '':
        print('Initial channels', var_dict['Channels'])
        user_chosen_channels = [utils.get_ref_channel(x, var_dict['Channels']) for x in user_chosen_channels.split(',')]
        if args.channels_toggle == 'exclude':
            var_dict['Channels'] = [x for x in var_dict['Channels'] if x not in user_chosen_channels]
        elif args.channels_toggle == 'include':
            assert set(user_chosen_channels).issubset(set(var_dict['Channels'])), 'Confirm that the selected channels (%s) exist within the dataset' % user_chosen_channels
            var_dict['Channels'] = user_chosen_channels
    assert var_dict['MorphologyChannel'] in var_dict['Channels'], 'The morphology channel (%s) not found within the selected channels (%s)' % (var_dict['MorphologyChannel'], ', '.join(var_dict['Channels']))
    print('Selected channels:', var_dict['Channels'])

    # update AnalyzedFiles to include only files for user-selected Wells, Timepoints, Channels
    var_dict['AnalyzedFiles'] = [x for x in var_dict['AnalyzedFiles'] if os.path.basename(x).split('_')[4] in var_dict['Wells']]
    var_dict['AnalyzedFiles'] = [x for x in var_dict['AnalyzedFiles'] if os.path.basename(x).split('_')[2] in var_dict['TimePoints']]
    ch_token_pos = utils.get_channel_token(var_dict['RoboNumber'])
    var_dict['AnalyzedFiles'] = [x for x in var_dict['AnalyzedFiles'] if
             os.path.basename(x).split('_')[ch_token_pos].replace('.tif','') in
             var_dict['Channels']]
    assert len(var_dict['AnalyzedFiles']) > 0, 'No image files match the selected include/exclude criteria'

    # check filenames for wells with missing timepoints, panels, or channels
    if check_data_option == 1:
        check_data(var_dict)

    # ----Output for user and save dict----------
    print('Input path:', input_path)
    print('Input directory structure:', dir_structure)
    print('Results output path:', output_path)

    pickle.dump(var_dict, open('var_dict.p', 'wb'))
    # outfile = os.rename('var_dict.p', outfile)
    outfile = shutil.move('var_dict.p', outfile)
    timestamp = utils.update_timestring()
    utils.save_user_args_to_csv(args, output_path, 'create_folders'+'_'+timestamp)

    end_time = datetime.datetime.utcnow()
    print('Module run time:', end_time - start_time)


if __name__ == "__main__":
    main()
