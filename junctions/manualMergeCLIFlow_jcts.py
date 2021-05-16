
# EXTERNAL IMPORTS

import datetime

# INTERNAL IMPORTS

import manualMergePrep_jcts as manualMergePrep

import manualMergeTool_jcts as manualMergeTool

import utils

import toml

# ****************************************************************************

print("\nWelcome to the manual merging tool for junctions!\n")

# (1) In order to run 'manualMergePrep.py', ask the user for three params:
# * region

region = input ("Please enter a region (in lowercase, e.g.: bern): \n")

print(f'\nThanks! The region you entered is {region}.\n')

# * the other two params (small_buf, large_buf) are optional - ask user if
#   defaults (found in paramDict in utils) should be accepted or custom
#   values desired

small_buf = utils.paramDict[region]["small_buf_default"]

large_buf = utils.paramDict[region]["large_buf_default"]

print(f"The default buffer sizes to compare for this region are: \n")

print(f"Small buffer: {small_buf}")

print(f"Large buffer: {large_buf}")

default = input ("Would you like to accept these defaults? Please reply with yes or no.\n")

if (default == "No"): 

    print("Thanks! You have chosen to supply custom values for a small and large buffer.\n")

    # * read small_buf from user input

    small_buf = float(input("Please enter a rather small buffer size (e.g.: 1): \n"))

    print(f'\nThanks! The small buffer size you entered is {small_buf}.\n')

    # * read large_buf from user input

    large_buf = float(input("Please enter a larger buffer size (e.g.: 1.25): \n"))

    print(f'\nThanks! The large buffer size you entered is {large_buf}. \n')

elif (default == "Yes"):

    print("Thanks! You have chosen to accept the default values for a small and large buffer.\n")

# (2) run 'manualMergePrep.py' - notify user that this will take loooooooong

print("Please be patient as the ensuing computations will take a few moments (up to a few minutes) to complete .........\n")

manualMergePrep.meta_assist(region, small_buf, large_buf)

# (3) Tell the user which outputs were produced and what they will be used for.
#     Specifically, point out the location of the .html map that was generated,
#     as it constitutes the basis for determining where re-merges shall take place.

print("Thanks for waiting! All the data necessary to manually edit junction clusters has been computed.\n")

print(f'Please navigate to directory PyPipeline_/junctions/html_maps and open the file \'{region}-jcts-manualClust_{datetime.date.today()}.html\' in your browser. \n')

print('By default, the more conservative clustering solutions (green shapes on the map) will be accepted. \n')

# NEW 13/02/21: Allow not only chosing liberal buffer solutions over conservative ones, but also the deletion
#               of conservative clusters 
#               REMARK: the deletion of more liberal clusters is not necessary as they are only added to the
#                       modified data frame if specifically desired by the user 
#                       (i.e., if a liberal cluster is chosen as a replacement for a conservative one).

# (4) Prompt the user to add the desired changes to {region}.toml. 

run_modifications = input ("Please add your desired modifications to {region}.toml (in the PyPipeline_/junctions/manual_merge_config directory). \n Enter ok once you're done. \n")

if (run_modifications == 'ok'):

    config_path = utils.getSubDirPath(f'{region}.toml', 'manual_merge_config')

    config = toml.load(config_path)

    for elem in config['replace']:

        manualMergeTool.update_clust(elem['old'], elem['new'], region)

    for elem in config['delete']:

        manualMergeTool.delete_clust(elem, region)

        print(elem)

    manualMergeTool.save_result(region)

    print(f'Your data can be found here: PyPipeline_/junctions/csv_data/manual_merging_res_{region}_{datetime.date.today()}.csv')
