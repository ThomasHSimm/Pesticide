
import seaborn as sns
import matplotlib.pyplot as plt

def plot_pie_by_chem(data_sql, chemical_country='boscalid', what_to_plot='sum_detected',is_country=True):

    if is_country:
        label_plot ='country_of_origin'
        title_str = what_to_plot + ' by chemical = ' + chemical_country
        selective = 'chem_name'
    else:
        label_plot = 'chem_name'
        title_str = what_to_plot + ' from country = ' + chemical_country
        selective = 'country_of_origin'

    if chemical_country =='all':
        data_sql = data_sql.groupby(label_plot,as_index=False).sum()
        data = data_sql.loc[:,what_to_plot]
        labels = data_sql.loc[:,label_plot]
    
    else:
        data = data_sql.loc[data_sql[selective]==chemical_country,what_to_plot]
        labels = data_sql.loc[data_sql[selective]==chemical_country,label_plot]
    
    #define Seaborn color palette to use
    colors = sns.color_palette('pastel')[0:len(labels)]
    fig=plt.figure(figsize=(7,7))
    plt.pie(data, labels=labels, colors = colors,
        autopct='%.0f%%', normalize=True);
    plt.title( title_str  )
    return fig