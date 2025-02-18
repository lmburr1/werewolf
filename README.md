In spring of 2020 a friend put together a group to play the social deduction game werewolf. We played so regularly over the course of the pandemic that we invented new roles in the game to keep things interested. On a whim, for a few games I tracked what happened in a spreadsheet to see if I could make something fun with the data.

Recently, I converted the spreadsheet to a relational database in Microsoft Access and wrote a Python program to assess what the best roles are based on that data. To make this assessment, I used the TrueSkill rating system that Microsoft uses on their XBOX Live platform. I chose this system because it allows for asymmetric teams, as well as a convenient Python library that you can find below.

TrueSkill Python library link: https://trueskill.org/
