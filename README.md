This script was used to quickly validate some ISBN numbers based on tabular book metadata. Some rows have ISBNs (valid or invalid), and some have nothing at all.
The script performs a search of WorldCat looking for a potential ISBN if there is none, and if there is an ISBN it tries to determine whether that ISBN is valid based in part on WorldCat search results.
It is fairly specific to the data format used in this project but may be of glancing interest for others.
