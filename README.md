## Quantifying near-homophony induced by French liaison

This github repository contains all the scripts used to extract data and results (statistical analyses) and to create plots. Scripts are listed according to the order in which they should be run. They must be executed in the ```CognitiveScienceMaster-LiaisonProject``` folder. If you want to follow step by step the approach done in the thesis, you can clone this folder and delete all files in the following folders: ```doublets```, ```plots```, ```results```. Then run the scripts in the order below:

### Number of confusing doublets
* ```1-extract-minimal-pairs.py```

Extracts from Lexique all minimal pairs, i.e. pairs of words that differ by the presence vs. absence of a consonant in onset position. (e.g. *ami* 'friend' / *tamis* 'sieve')

* ```2-extract-number-confusing-doublets.py```

Generates doublets (e.g. {*petit ami* 'boyfriend' / *petit tamis* 'little sieve'}) while keeping only grammatical ones. Does it for 'real' French and for all alternative versions (liaison consonant substitutions). Numbers of confusing doublets are stored in ```results/results-number-confusing-doublets.csv```.

* ```Rscripts/confusing-doublets-test.R```

(To easily run the R scripts, open the project file ```statistical-tests.Rproj``` and then open and run the R script you want. This procedure allows you to adjust your wording directory and fetch the data without having to enter any line of code.)
Performs one-sample one-tailed Wilcoxon signed-rank tests, comparing the number of confusing doublets obtained with substitutions to that obtained in real French.

* ```3-plot-number-confusing-doublets.py```

Plots the number of confusing doublets for all liaison consonants and all substitutions. Figure is saved in ```plots/plot-number-confusing-doublets.png```.

### Number of troublesome doublets (frequency analysis)
* ```4-extract-frequency-data.py```

Retrieves frequency data from Google Ngram Viewer for all doublets. These data will be stored in ```doublets/raw-frequency-data```. This script allows one to get the required data without downloading and using all the data available on Google (tons of GB), but is tedious as it makes http requests one by one. If you follow the steps of the thesis, it is better to copy in ```doublets``` the folder available on github ```raw-frequency-data```. 

* ```5-rename-frequency-files.py```

Rename the frequency files and create a correspondence table (new file name - associated query) in order to be able to process all the data (some file names were too long).

* ```6-clean-frequency-data.py```

Cleans frequency data by extracting the number of occurrences for each doublet from proportional data retrieved through Google Ngram Viewer. These data will be stored in ```doublets/cleaned-frequency-data```.

* ```7-extract-number-troublesome-doublets.py```

Plots the cumulative distribution functions of the sum and ratio of the frequency values of doublets, saved in ```plots/plot-CDF-ratio-sum-frequency-data.png ```. Then, extracts the number of troublesome doublets for each liaison consonant and each substitution, stored in ```results/results-number-troublesome-doublets.csv```.

* ```Rscripts/troublesome-doublets-test.R```

Performs one-sample one-tailed Wilcoxon signed-rank tests, comparing the number of troublesome doublets obtained with substitutions to that obtained in real French.

* ```8-plot-number-troublesome-doublets.py```

Plots the number of troublesome doublets for all liaison consonants and all substitutions. Figure is saved in ```plots/plot-number-troublesome-doublets.png```.
