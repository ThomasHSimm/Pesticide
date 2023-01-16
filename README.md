# Intro

This is a program to collect and download the data published by Department for Environment, Food and Rural Affairs (DEFRA) as part of the UK governmental pesticide monitoring program.

DEFRA conducts pesticide testing data is released in Open Document Spreadsheet format on [data.gov.uk](https://data.gov.uk/dataset/5d5028ef-9918-4ab7-8755-81f3ad06f308/pesticide-residues-in-food). 

Much of the quarterly and annual data is available in this repo's [data folder](https://github.com/ThomasHSimm/Pesticide/tree/main/data). 


Information about the data from the [source site](https://www.data.gov.uk/dataset/5d5028ef-9918-4ab7-8755-81f3ad06f308/pesticide-residues-in-food): 

The website of this is found at [PesticideDocs](https://thomashsimm.github.io/PesticideDocs/)

> The data set shows pesticide residues in different foods types, presented in 2 different table formats. The BNA format focusses on details of individual samples  including brand name and origin and shows the pesticides detected if any. The SUM format focuses on the analysis and results across the set of samples, including detail of all the pesticides sought but not found.

# Aims

- Produce a downloader to download ods files and convert to a more useable df format
- Plots and display data
- Combine in a streamlit app

# Current output

- a workable downloader using beautifulsoup exists but how to incoporate in the app not established
  - would like: button on app that downloads new ods files to the github repo
  - why: dowloading the files each time on streamlit is not userfriendly
  - workaround: download files not in the data folder? 
- ods to dataframe:
  - each ods file has a different format. Some basic workarounds given format of ones looked at used
  - either create in one big df in app or group by year and maybe extract other info seperately
  - work as a df somewhere to access by SQL etc?
- dataframe processing
  - done by a combination of pandas and pandas-SQL
  - + understanding of data needed for more coherent processing
- plots
  - (see above) business case needs exploring
  - choice of plot type
  - legend away from pie- looks a mess when lots of elements
- streamlit app
  - maybe a plot with time too
  - df plots crash local pc for df2 if don't put head()
    - maybe more refined display based on criteria of data?
  - add count part to plots

https://thomashsimm-pesticide-pest-streamlit-ku7yyt.streamlit.app/

## Acknowledgement

This project was initiated by [James Westwood](https://github.com/james-westwood) in 2021 at [this repo](https://github.com/james-westwood/govt_pesticide_test_data_downloader). 

