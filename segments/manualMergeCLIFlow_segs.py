
# EXTERNAL IMPORTS

import datetime

# INTERNAL IMPORTS

import manualMergePrep_segs

import manualMergeTool_segs

# ****************************************************************************

print("\nWelcome to the manual merging tool for segments!\n")

# (1) In order to run 'manualMergePrep.py', ask the user for three params:
# * region

region = input ("Please enter a region (in lowercase, e.g.: bern): \n")

print(f'\nThanks! The region you entered is {region}.\n')

# * small_buf

small_buf = float(input("Please enter a rather small buffer size (e.g.: 1): \n"))

print(f'\nThanks! The small buffer size you entered is {small_buf}.\n')

# * large_buf

large_buf = float(input("Please enter a larger buffer size (e.g.: 1.25): \n"))

print(f'\nThanks! The large buffer size you entered is {large_buf}. \n')

# (2) run 'manualMergePrep.py' - notify user that this will take loooooooong

print("Please be patient as the ensuing computations will take a few minutes to complete .........\n")

manualMergePrep_segs.meta_assist(region, small_buf, large_buf)

# (3) Tell the user which outputs were produced and what they will be used for.
#     Specifically, point out the location of the .html map that was generated,
#     as it constitutes the basis for determining where re-merges shall take place.

print("Thanks for waiting! All the data necessary to manually edit junction clusters has been computed.\n")

print(f'Please navigate to directory PyPipeline_/junctions and open the file \'{region}-jcts-manualClust_{datetime.date.today()}.html\' in your browser. \n')

print('By default, the more conservative clustering solutions (green shapes on the map) will be accepted. \n')

print('Would you like to replace any of the more conservative clustering solutions (green) by more liberal ones (blue)? \n')

# (4) Ask the user if any editing is desired. 

continue_editing = input ("Please reply with yes or no. \n")

while (continue_editing == 'yes'):

# Repeat steps (5) - (8) while the user wishes to continue editing.

    print("Typically, a more conservative clustering solution that should be replaced by a more liberal one consists of multiple green shapes.\n")

    print("You will therefore be prompted to provide the cluster numbers of all those green shapes one by one.\n")

    # (5) In order to run 'manualMergeTool.py' > update_clust, ask the user for three params: 
    # * small_buf_clstrs (list of floats) --> ask for them one by one.

    small_buf_clstrs = []
    
    first_small_clstr = float(input("Please enter cluster number of the first green shape you want to replace (e.g., 889.0).\n"))

    small_buf_clstrs.append(first_small_clstr)

    further_small_clstrs = input ("Are there more green shapes you wish to replace? Please reply with yes or no.\n")

    while (further_small_clstrs == 'yes'):

        next_small_clstr = float(input("Please enter the cluster number of the next green shape you want to replace (e.g., 2364.0).\n"))

        small_buf_clstrs.append(next_small_clstr)

        further_small_clstrs = input ("Are there more green shapes you wish to replace? Please reply with yes or no.\n")

    # * large_buf_clstr (float)

    print("Thank you! The following green shapes will be replaced: ")

    for clust in small_buf_clstrs: 

        print(clust)

    print("\nTypically, the more liberal solution to replace the more conservative one will consist of one blue shape only.\n")

    large_buf_clstr = float(input("Please enter the cluster number of the blue shape with which you want to replace the previously specified green ones.\n"))

    print(f'\nThanks! The cluster {large_buf_clstr} will replace the previously specified green clusters.\n')

    # * region: already asked for above

    # (6) run 'manualMergeTool.py' > update_clust - show progress bar using tqdm as this will take loooooooong
    #     (though) not as long as 'manualMergePrep.py' 

    print("Please be patient as the ensuing computations will take a few minutes to complete .........\n")

    manualMergeTool_segs.update_clust(small_buf_clstrs, large_buf_clstr, region)

    # (7) Tell the user to refresh the map to see the result    

    print(f'Please refresh the map (PyPipeline_/segments/\'{region}-segs-manualClust_{datetime.date.today()}.html\') to see the result (in orange).\n')

    # (8) Ask if more manual editing is desired - if so, repeat the process from (5); if not proceed to (9)

    continue_editing = input ("Would you like to continue editing? Please reply with yes or no. \n")

# (9) Write the resultant data frame to memory: 'manualMergeTool.py' > save_result

print("You've chosen to finish editing. The resultant data will be written to csv.\n")

manualMergeTool_segs.save_result(region)

print(f'Your data can be found here: PyPipeline_/segments/manual_merging_res_{region}_{datetime.date.today()}.csv')