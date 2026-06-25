import pandas as pd

def load_transaction(uploaded_file):

    raw = pd.read_excel(uploaded_file, header=None)

    header_row = None

    for i in range(min(15, len(raw))):

        row = (
            raw.iloc[i]
            .fillna("")
            .astype(str)
            .str.replace("_x000a_", " ", regex=False)
            .str.replace("\n", " ", regex=False)
            .str.strip()
            .tolist()
        )

        # Detect any known transaction report header
        if (
            "Lane_id" in row
            or "Txn_Id" in row
            or "Origin" in row
            or "Payment Mode" in row
            or "Operator Class" in row
        ):
            header_row = i
            break

    if header_row is None:
        print(raw.head(15).to_string())
        raise Exception("Header row not found.")

    txn_df = raw.iloc[header_row + 1:].copy()
    txn_df.columns = raw.iloc[header_row]

    txn_df = txn_df.loc[:, txn_df.columns.notna()]

    txn_df.columns = (
        txn_df.columns.astype(str)
        .str.replace("_x000a_", " ", regex=False)
        .str.replace("\n", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    txn_df.reset_index(drop=True, inplace=True)

    return txn_df