
import seaborn as sns
import matplotlib.pyplot as plt

def plot_pie_by_chem(data_sql, chemical_country='boscalid', what_to_plot='sum_detected',is_country=True,product='all'):
    """

    Args:  
        data_sql (pd df): data to plot
        chemical_country (str): chemical or country to plot
        what_to_plot (str): what to plot
        is_country (bool): if True plot by country, else plot by chemical
        product (str): product to plot
    """
    if is_country:
        label_plot ='country_of_origin'
        title_str = product + '. ' + what_to_plot + ' by chemical = ' + chemical_country
        selective = 'chem_name'
    else:
        label_plot = 'chem_name'
        title_str = product + '. ' + what_to_plot + ' from country = ' + chemical_country
        selective = 'country_of_origin'

    if chemical_country =='all':
        data_sql = data_sql.groupby(label_plot,as_index=False).sum()
        data = data_sql.loc[:,what_to_plot]
        labels = data_sql.loc[:,label_plot]
    
    else:
        data = data_sql.loc[data_sql[selective]==chemical_country,what_to_plot]
        labels = data_sql.loc[data_sql[selective]==chemical_country,label_plot]
    
    useme = data != 0
    data = data[useme]
    labels = labels[useme]

    #define Seaborn color palette to use
    colors = sns.color_palette('pastel')[0:len(labels)]
    fig=plt.figure(figsize=(7,7))
    plt.pie(data, labels=labels, colors = colors,
        autopct='%.0f%%', normalize=True);
    plt.title( title_str  )
    return fig