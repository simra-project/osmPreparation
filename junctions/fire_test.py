import fire

import pandas as pd

import manualClusterPrep

import manualMergeTool

def update(buffer):

    # curr_clust = np.float64(curr_clust)
    # new_clust = np.float64(new_clust)

    print("test")

    # complete_df = pd.read_csv(f'{region}_jcts_buf={buffer_size}_manual_merging_target.csv', sep='|')

    complete_df = pd.read_csv('manual_merging_target.csv', sep='|')

    complete_df.loc[:,'neighbour_cluster'] = complete_df['neighbour_cluster'].map(lambda x: x if x != 605.0 else 600)

    # Grab the rows from complete_df that are going to be merged

    res = manualMergeTool.reMerge(complete_df, 600)

    complete_df = manualClusterPrep.split_and_plot(res, "pforz", buffer)

    complete_df.to_csv('manual_merging_target.csv', index=False, sep="|")

if __name__ == '__main__':
  fire.Fire(update)