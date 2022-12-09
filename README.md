# The Government Pesticide Testing Programme Analyser

This is a program to collect and download the data published by the UK government as part of their pesticide monitoring program. 
The data is imported into Pandas Dataframes and can be analysed.

The Department for Environment, Food and Rural Affairs conducts pesticide testing Data is released in Open Document Spreadsheet format and released on data.gov.uk [here](https://data.gov.uk/dataset/5d5028ef-9918-4ab7-8755-81f3ad06f308/pesticide-residues-in-food). Much of the quarterly and annual data is available in this repo's [data folder](https://github.com/james-westwood/govt_pesticide_test_data_downloader/tree/master/data_files). 

Currently (11/11/21) the script is in a [Jupyter Notebook](https://github.com/james-westwood/govt_pesticide_test_data_downloader/blob/master/govt_pest_data_latest.ipynb) which has not been updated for 2 years. The first task would be to export the Notebook to a .py file, and make sure the script as is works as a continuous pipeline. 

## Requirements of the data parsing script

What this script should (eventually) do:
- Download any new quarterly report data from data.gov.uk
- Cache/save the files locally
- Parse all the sheets of the ods files into dataframes
- Clean up the data
- Split the "Pesticide residues found in mg/kg (MRL)" (which is a combo of three pieces of info" into three separate columns (Chemical Detected, Amount Detected, MRL)
  - Be able to cope if multiple chemicals are detected

### Creating a dashboard

We should use streamlit to create a dashboard that would allow the following grouping and visualisation for analysis:
1) Summary of each product (apples or aubergines), grouped by country of origin
    
    1b) under each Country group, results grouped by detected chemicals (DC)
    
    1c) for each DC, show the count of products with some detected and the range they were in
    
    1d) for each DC, show the count of products with none-detected
2) Counts of product items grouped by country of origin, e.g "Apples from USA = 6, Apples from France = 3 "
3) Distribution of DCs grouped by country of origin, e.g. boscalid : UK = 2, USA = 5.
4) Statement of Count Range of DCs found in how many of total number of samples, e.g. "Residues (ranging from 1 to 11) were detected in 12 of 24 of the samples analysed"
5) A table showing number of residues, sample ID, Type of apple, amounts of each DC (and a '-' if n/a) and the country of origin
6) total list of chemicals analysed for but not found.

#### Types of visualisation:
1) for each product, show chart of prods with none detected, one detected, multiple detected
2) same as above, but filter by supermarket.
  2b) same as above but filter by country of origin
  2c) same as above but show breakdown
3) scattergraph of amounts detected across product category, compared to MRLs (either individual DCs or agregated)
4) Stacked bargraph showing total amount detected per sample, with a different colour to represent each DC.
5) some kind of graph to represent the chemicals that were not detected