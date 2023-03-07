import pandas as pd

"""
Extracting data from dataset downloaded from Etherscan
"""
df1 = pd.read_csv("etherscan_data/ALL_BID_DATA.csv", index_col=False)
df2 = pd.read_csv("etherscan_data/ALL_BID_DATA_2.csv", index_col=False)
final_bids = pd.concat([df1, df2]).drop_duplicates().reset_index(drop=True)
final_bids.rename(columns={"From": "bidder", "To": "auction_house", "DateTime": "bid_date_time"}, inplace=True)
noun_auction = pd.read_csv("etherscan_data/NOUN_NFT_TRANSFER_AUCTION_HOUSE.csv")
auction_house_address = "0x830bd73e4184cef73443c15111a1df14e495c706"
final_noun_auction = noun_auction.loc[noun_auction["From"] == auction_house_address]
final_noun_auction.rename(columns={"From": "auction_house", "To": "bidder", "DateTime": "auction_date_time"},
                          inplace=True)

joined_data_full = pd.merge(final_noun_auction, final_bids, on="bidder", how="left")
# Remove all the records with status having any errors
joined_data_full = joined_data_full[joined_data_full["Status"].isnull()]

joined_data = joined_data_full[
    ["Token_ID", "auction_house_x", "auction_date_time", "bid_date_time", "bidder", "Value_IN(ETH)"]]

joined_data["auction_date_time"] = joined_data["auction_date_time"].astype('datetime64[ns]')
joined_data["bid_date_time"] = joined_data["bid_date_time"].astype('datetime64[ns]')
missing_data = joined_data[joined_data["bid_date_time"].isnull()]

# Only take the data where the auction date is the same as bid date. This is because the same bidder can bid for
# other nouns on a different day and that will cause wrong joining of data.
joined_data = joined_data[(joined_data["auction_date_time"].dt.date == joined_data["bid_date_time"].dt.date)]
final_output_df = joined_data.loc[joined_data.groupby(["Token_ID"])["Value_IN(ETH)"].idxmax()]
final_output_df = final_output_df[["Token_ID", "bidder", "Value_IN(ETH)"]].rename(
    columns={"Token_ID": "noun_id", "bidder": "winner_address", "Value_IN(ETH)": "winning_bid_eth"}
)
# For noun token_id that are divisible by 10, the auction goes to the founders.
# This can be hardcoded and added to the dataset.
nounder_address = "0x2573c60a6d127755aa2dc85e342f7da2378a0cc5"
nouns_till_date = 634
for i in range(0, nouns_till_date, 10):
    final_output_df = final_output_df.append({
        "noun_id": i,
        "winner_address": nounder_address,
        "winning_bid_eth": 0
    }, ignore_index=True)

final_output_df = final_output_df.sort_values(by=["noun_id"])
final_output_df.to_csv("final_data/etherscan_processed.csv", index=False)
