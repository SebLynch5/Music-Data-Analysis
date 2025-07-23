#####
# Top5.py
# Written by Sebastian Lynch, Jan 2025.
#####

"""
This module ranks top artists over a specified year range, based on the number
of songs, average popularity, and average danceability. It retrieves song data
from "MusicDatabase.db", calculates rank values for each artist, and presents the
top 5 artists' results in a table and a line chart.
The weights used for the ranking are specified at the start of the program.

Functions:
- year_check(start_year, end_year): Validates that the inputted year range is
  within 1998–2020 and that start_year is not greater than end_year.
- get_data(start_year, end_year): Fetches song data from "MusicDatabase.db" for the
  specified year range.
- calculate_rank_values(df): Calculates the rank value for each artist based on
  the formula using the number of songs, average popularity, and average
  danceability. This function uses the weigth values specified at the start of
  the program.
- generate_table_and_chart(df, start_year, end_year): Generates a summary table
  and a line chart for the top 5 ranked artists, highlighting their yearly rank
  values if it's the highest for that year.
- main(start_year, end_year): Validates the year range, fetches data, calculates
  rank values, generates the table and chart.

Dependencies:
- sqlite3
- pandas
- numpy
- matplotlib
- IPython.display

Database Details:
- 'MusicDatabase.db':
  - **Song Table**: Contains song data with columns year, popularity,
    danceability and references artists.
  - **Artist Table**: Contains artist names and IDs.

Usage:
- Run main() to produce the Top 5 analysis.
- If run directly, the test code at the end of the script will be executed.

Written by Sebastian  Lynch, Jan 2025
"""


import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display

# Define the formula weights
WEIGHT_X = 10 # Weight for the number of songs
WEIGHT_Y = 0.7 # Weight for average popularity
WEIGHT_Z = 50 # Weight for average danceability

def year_check(start_year, end_year):
    """
    Validates that the inputted years form a range within 1998-2020.
    
    Parameters:
    - start_year (int): The inputted start year.
    - end_year (int): The inputted end year.
    
    Returns:
    - Boolean value. True if the inputted years form a range within 1998-2020,
      false if not.
    """
    if start_year < 1998 or end_year > 2020 or start_year > end_year:
        print("Invalid year range. Please enter years between 1998 and 2020.")
        return False
    else:
        return True

def get_data(start_year, end_year):
    """
    Fetch data from the database for the specified year range.
    
    Parameters:
    - start_year (int): The inputted start year.
    - end_year (int): The inputted end year.
    
    Returns:
    - df (pd.DataFrame): The data in the specified year range.
    """
    try:
        conn = sqlite3.connect("MusicDatabase.db")
        query = f"""
        SELECT artist.artist AS artist,
        song.year,
        COUNT(song.Song) AS num_song,
        AVG(song.popularity) AS avg_popularity,
        AVG(song.danceability) AS avg_danceability
        FROM song
        JOIN artist ON song.artist_id = artist.artist_id
        WHERE song.year BETWEEN ? AND ?
        GROUP BY artist.artist, song.year
        ORDER BY song.year, artist.artist;
        """
        df = pd.read_sql_query(query, conn, params=(start_year, end_year))
        conn.close()
        df.columns = df.columns.str.lower()
        return df
    except Exception as e:
        print("Error fetching data:", e)
        return pd.DataFrame()

def calculate_rank_values(df):
    """
    Calculates the rank values for each artist.
    
    Parameter:
    - df (pd.DataFrame): with columns "num_song", "avg_popularity" and
      "avg_danceability".
    
    Returns:
    - df (pd.DataFrame): same as inputted but now with "rank_value" column.
    """
    if df.empty:
        return df

    df["rank_value"] = (
        (df["num_song"] * WEIGHT_X) + 
        (df["avg_popularity"] * WEIGHT_Y) +
        (df["avg_danceability"] * WEIGHT_Z)
    )

    return df

def generate_table_and_chart(df, start_year, end_year):
    """
    Generates the summary table and line chart.
    """
    if df.empty:
        print("No data found for the specified year range.")
        return

    # Get the top 5 artists by overall rank value
    overall_rank = (
        df.groupby("artist")["rank_value"]
        .mean()
        .sort_values(ascending = False)
    )
    
    top_artists = overall_rank.head(5).index.tolist()

    # Filter data for the top 5 artists
    top_df = df[df["artist"].isin(top_artists)]

    # Pivot table for visualisation
    pivot = top_df.pivot_table(index = "year",
                               columns = "artist",
                               values = "rank_value",
                               aggfunc = "mean")

    # Calculate overall averages for the table
    pivot["Yearly Avg"] = pivot.mean(axis = 1)
    pivot.loc["Overall Avg"] = pivot.mean()

    # Highlight the top artist per year
    def highlight_top(s):
        """
        Highlights the maximum value in a pandas Series.

        Parameters:
        - s (pd.Series): The input Series; a row or column
          from a DataFrame.

        Returns:
        - list: A list of CSS styles ("background-color: lightgreen" or "") 
          corresponding to each element in the series, where the maximum 
          value(s) are highlighted in lightgreen.
        """
        is_max = s == s.max()
        return ["background-color: lightgreen" if v else "" for v in is_max]
    
    styled_table = pivot.style.apply(highlight_top,
                                     axis = 1,
                                     subset = top_artists
                                    ).format("{:.2f}", na_rep = "Null")
    print("Top 5 Artists Rank Table:")
    display(styled_table)

    # Plot the line chart
    plt.figure(figsize = (12, 8))
    for artist in top_artists:
        plt.plot(pivot.index[:-1],
                 pivot[artist][:-1],
                 label = artist,
                 marker = 'o') # Exclude overall avg row
        
    plt.plot(pivot.index[:-1],
             pivot["Yearly Avg"][:-1],
             label = "Yearly Avg",
             linestyle = "--",
             color = "black"
            )

    plt.xlabel("Year")
    plt.ylabel("Rank Value")
    plt.title(f"Top 5 Artists' Yearly Rank Values ({start_year}–{end_year})")
    plt.legend()
    plt.grid()
    plt.show()

def main(start_year, end_year):
    """
    Validates that the inputted years form a range within 1998-2020.
    Calculates the rank values for each artist.
    Generates the summary table and line chart.
    
    Parameters:
    - start_year (int): The inputted start year.
    - end_year (int): The inputted end year.
    """
    
    if year_check(start_year, end_year) == True:
        print("Top Artists Analysis")
        # Fetch and process data
        data = get_data(start_year, end_year)
        ranked_data = calculate_rank_values(data)

        # Generate the table and chart
        generate_table_and_chart(ranked_data, start_year, end_year)

        
        
#####
# Test code 
#####
if __name__ == "__main__":
    print("Testing year_check():")
    if year_check(1997, 2000):
        print("Failed")
    else:
        print("Passed")
            
    if year_check(2015, 2018):
        print("Passed")
    else:
        print("Failed")
        
    if year_check(2019, 2021):
        print("Failed")
    else:
        print("Passed")
        
    #
    print("\n Testing get_data():")
    test_df = get_data(1998, 2000)
    print(test_df)
    
    print("\n Testing calculate_rank_values():")
    test_df = calculate_rank_values(test_df)
    print(test_df)
    
    print("\n Testing generate_table_and_chart():")
    generate_table_and_chart(test_df, 1998, 2000)
    
    print("\n Testing main():")
    main(1998, 2000)
