import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

column_names_dict = {
    "amount_detected": "Pesticide residues \nfound (mg/kg)",
    "mrl": "Maximum reporting \nlimit MRL (mg/kg)",
    "amount_pc": "Pesticide residues \nfraction of MRL",
}


def range_plots(
    df2: pd.DataFrame,
    plot_type: str = "boxplot",
    column_to_plot: str = "amount_detected",
    cols_numeric: list = [],
    max_bin: list = [],
    bin_no: int = 30,
    column_names_dict: dict = column_names_dict,
) -> plt.figure:
    """
    Produces plots to show ranges in data
    N.B. zeros are removed
    https://seaborn.pydata.org/generated/seaborn.boxplot.html#seaborn.boxplot
    change for violinplot

    Args:
        df2 (pd.DataFrame): Pandas DataFrame. Pesticide data after grouping
        plot_type (str): string of type of plot to do 'boxplot' or 'hist'
        column_to_plot (str): which column to plot
        cols_numeric (list[str]): list of column strings to plot (no input finds numeric columns)
        max_bin (list[float]): list of floats (or ints) to gave max range for histogram (min = 0).
        bin_no (int): number of bins
        column_names_dict (dict): dict of what to change column names to and from

    Raises:
        ValueError: ??

    Returns:
        pyplot figures object of a boxplot or histogram
    """

    # if no input of cols_numeric finds from dtype=int or float
    if not cols_numeric:
        cols_numeric = [
            column
            for column in df2
            if df2[column].dtype == "float" or df2[column].dtype == "int"
        ]

    # get just the cols_numeric columns
    numeric_df = df2.loc[:, cols_numeric].copy()
    numeric_df = numeric_df.loc[numeric_df[column_to_plot] != 0]

    # rename columns
    numeric_df = numeric_df.rename(columns=column_names_dict)

    # different plot types

    if plot_type == "boxplot":

        fig = plt.figure(figsize=(8, 8))
        sns.boxplot(data=numeric_df)
        plt.yscale("log")

    elif plot_type == "hist":

        n_cols = 3  # columns in plot

        n_rows = (len(numeric_df.columns) - 1) // n_cols + 1

        fig, ax = plt.subplots(
            nrows=n_rows, ncols=n_cols, sharex=False, figsize=(12, 6)
        )

        if not max_bin:
            max_bin = [5, 20, 1]

        for i, cols in enumerate(numeric_df):
            data_col = numeric_df[cols]
            counts, bins = np.histogram(data_col, range=[0, max_bin[i]], bins=bin_no)
            ax[i].hist(bins[:-1], bins, weights=counts)

            # ax[i].set_yscale('log')
            ax[i].set_title(cols)
            if i == 0:
                ax[i].set_ylabel("Count")

    return fig


#######################################################################################


def pie_plot(
    df_grouped_temp: pd.DataFrame,
    col_groupby: str = "country_of_origin",
    col_plot: str = "number_of_tests",
    NUM_LABELS: int = 15,
    MIN_PCT: float = 2.0,
) -> plt.figure:
    """
    Produces a pie plot from grouped data see groupby_id_country_chemical which does the grouping


    Args:
        df_grouped_temp (pd.DataFrame): Pandas DataFrame. Pesticide data after grouping
        col_groupby (str): which column has the names of the pie slices
        col_plot (str): which column has the data
        NUM_LABELS (int): max number of labels shown on the plot
        MIN_PCT (float): min % to display text has to be more than

    Raises:
        ValueError: ??

    Returns:
        pyplot figures object of a pie chart
    """

    maxed_out = False

    # what multiple of MIN_PCT have no decimal point
    go_to_1dp = 2.0

    df_grouped_temp = df_grouped_temp[[col_groupby, col_plot]].copy()

    df_grouped_temp = df_grouped_temp.sort_values(col_plot, ascending=False)

    if len(df_grouped_temp) > NUM_LABELS:
        df_grouped_temp[col_plot] = (
            100 * df_grouped_temp[col_plot] / sum(df_grouped_temp[col_plot])
        )

        df_grouped_temp = df_grouped_temp.loc[df_grouped_temp[col_plot] > MIN_PCT]

        new_row = pd.Series(
            {col_groupby: "Other", col_plot: 100 - sum(df_grouped_temp[col_plot])}
        )

        df_grouped_temp = pd.concat(
            [df_grouped_temp, new_row.to_frame().T], ignore_index=True
        )

        maxed_out = True

    labels = df_grouped_temp[col_groupby].copy()
    colors = sns.color_palette("pastel")
    len_colors = len(colors)

    # create colors of length of labels
    for i in range(0, len(labels) // len_colors + 1):
        colors = colors + colors
    colors = colors[: len(labels)]

    # if there is an 'other' make the other this color
    if maxed_out:
        colors[-1] = (0.9, 0.9, 0.9)

    fig = plt.figure(figsize=(7, 7))

    def func(pct, allvals):

        if pct > MIN_PCT * go_to_1dp:
            text_out = "{:.1f}%".format(pct)
        else:
            text_out = "{:.0f}%".format(pct)
        return text_out

    wedges, texts, autotexts = plt.pie(
        df_grouped_temp[col_plot],
        colors=colors,
        labels=labels,
        autopct=lambda pct: func(pct, df_grouped_temp[col_plot]),
    )

    col_plot = col_plot.replace("_", " ")
    col_groupby = col_groupby.replace("_", " ")
    plt.title(f"The {col_plot} by {col_groupby}")

    return fig


#######################################################################################


def plot_pie_by_chem(
    data_sql,
    chemical_country="boscalid",
    what_to_plot="sum_detected",
    is_country=True,
    product="all",
):

    if is_country:
        label_plot = "country_of_origin"
        title_str = product + ". " + what_to_plot + " by chemical = " + chemical_country
        selective = "chem_name"
    else:
        label_plot = "chem_name"
        title_str = (
            product + ". " + what_to_plot + " from country = " + chemical_country
        )
        selective = "country_of_origin"

    if chemical_country == "all":
        data_sql = data_sql.groupby(label_plot, as_index=False).sum()
        data = data_sql.loc[:, what_to_plot]
        labels = data_sql.loc[:, label_plot]

    else:
        data = data_sql.loc[data_sql[selective] == chemical_country, what_to_plot]
        labels = data_sql.loc[data_sql[selective] == chemical_country, label_plot]

    useme = data != 0
    data = data[useme]
    labels = labels[useme]

    # define Seaborn color palette to use
    colors = sns.color_palette("pastel")[0 : len(labels)]
    fig = plt.figure(figsize=(7, 7))
    plt.pie(data, labels=labels, colors=colors, autopct="%.0f%%", normalize=True)
    plt.title(title_str)
    return fig
