#####
# Artist.py
# Written by Sebastian Lynch, Jan 2025.
#####

"""
This module analyses and visualises song popularity data for a user inputted
artist across genres. It retrieves song data from "MusicDatabase.db" and performs
statistical analysis, displaying results in tables and visualisations.

Functions:
- artist_input(artist_name): Verifies if the inputted artist name exists in
  the "Artist" table of "MusicDatabase.db".
- popularity_analysis(artist_name): Analyses and visualises the average
  popularity of a given artist's songs across genres relative to each genre's
  average.
- main(artist_name): Main function that verifies that the artist name is in
  "MusicDatabase.db" and calls popularity_analysis(artist_name) if it is.
- name_list(): Prints the full list of artist names in the "Artist" table
  of the database in alphabetical order.

Dependencies:
- pandas
- matplotlib
- sqlite3
- IPython.display

Database Details:
- 'MusicDatabase.db':
  - **Artist Table**: Contains artist names.
  - **Song Table**: Contains song data, including popularity and referencing
    the artist and genre of each song.
  - **Genre Table**: Contains unique genre names.

Usage:
- Run main() to produce the artist analysis.
- If run directly, the test code at the end of the script will be executed.
    
Written by Sebastian Lynch, Jan 2025.
"""


import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from IPython.display import display

pd.set_option('future.no_silent_downcasting', True)

def artist_input(artist_name):
    """
    Verifies that the inputted artist name exists within "MusicDatabase.db".
    
    Parameter:
    - artist_name (str): the inputted artist name
    
    Returns:
    - Boolean value. True if the artist name is in the db, false if not.
    """
    try:
        connection = sqlite3.connect("MusicDatabase.db")
        artist_query = "SELECT * FROM Artist WHERE artist = ?"
        artist_exists = pd.read_sql_query(artist_query,
                                          connection,
                                          params = (artist_name,)
                                         )
        if not artist_exists.empty:
            print(f"Artist '{artist_name}' found in the database.")
            connection.close()
            return True
        else:
            return False
    except Exception as e:
        print("Error fetching data:", e)
        return False


def popularity_analysis(artist_name):
    """
    Analyses and visualises the average popularity of a specified artist's
    songs across genres.
    
    Parameter:
    - artist_name (str): the inputted artist name
    
    Displays a table and bar chart.
    """
    connection = sqlite3.connect("MusicDatabase.db")

    # Query for artist-specific popularity
    artist_popularity_query = '''
        SELECT 
            Genre.genre, 
            Song.Popularity AS song_popularity
        FROM Song
        JOIN Artist ON Song.Artist_ID = Artist.Artist_ID
        JOIN Genre ON Song.Genre_ID = Genre.Genre_ID
        WHERE Artist.artist = ?
    '''
    artist_popularity = pd.read_sql_query(artist_popularity_query,
                                          connection,
                                          params = (artist_name,)
                                         )

    # Query for overall genre popularity
    overall_popularity_query = '''
        SELECT 
            Genre.genre, 
            Song.Popularity AS song_popularity
        FROM Song
        JOIN Genre ON Song.Genre_ID = Genre.Genre_ID
    '''
    overall_popularity = pd.read_sql_query(overall_popularity_query,
                                           connection
                                          )

    connection.close()

    # Split and explode combined genres
    def preprocess_genres(df):
        """Split and explode the genres into singular entries."""
        df["genre"] = df["genre"].str.split(', ')
        df = df.explode("genre").reset_index(drop=True)
        return df

    artist_popularity = preprocess_genres(artist_popularity)
    overall_popularity = preprocess_genres(overall_popularity)

    # Calculate artist-specific averages per genre
    artist_genre_stats = (
        artist_popularity
        .groupby("genre")
        .agg(artist_popularity = ("song_popularity", "mean"),
             artist_song_count = ("song_popularity", "count")
            )
        .reset_index()
    )

    # Calculate overall averages per genre
    overall_genre_stats = (
        overall_popularity
        .groupby("genre")
        .agg(overall_popularity = ("song_popularity", "mean"),
             overall_song_count = ("song_popularity", "count")
            )
        .reset_index()
    )

    # Merge artist-specific and overall genre data
    merged_popularity = pd.merge(
        overall_genre_stats,
        artist_genre_stats,
        on = "genre",
        how = "left"
    ).fillna(0)  # Replace NaN with 0 for missing artist genres

    # Highlight genres where the artist exceeds the overall average
    merged_popularity["highlight"] = (
        merged_popularity["artist_popularity"]
        > merged_popularity["overall_popularity"]
    )

    # Convert song counts to integers and
    # replace 0s with Null in artist_popularity.
    merged_popularity["artist_song_count"] = (
        merged_popularity["artist_song_count"]
        .astype(int)
    )

    merged_popularity["artist_popularity"] = (
        merged_popularity["artist_popularity"]
        .replace(0, "Null")
    )

    # Style and display the data table
    def highlight_pop(row):
        """
        Highlights the "artist_popularity" column if the artist's popularity
        is above the overall average popularity.

        Parameters:
        - row (pd.Series): A single row of a DataFrame. The row should include
          "Artist Popularity" and "Overall Popularity" columns.

        Returns:
        - list: A list of styles (e.g, 'background-color: lightgreen') 
          applied to each column in the row. Empty strings for no styling.
        """
        return [
            'background-color: lightgreen'
            if col == "Artist Popularity"
            and row["Artist Popularity"] != "Null"
            and float(row["Artist Popularity"]) > row["Overall Popularity"]
            else ''
            for col in row.index
        ]


    styled_table = merged_popularity.copy()
    styled_table.rename(
        columns = {
            "genre": "Genre",
            "overall_popularity": "Overall Popularity",
            "overall_song_count": "Overall Song Count",
            "artist_popularity": "Artist Popularity",
            "artist_song_count": "Artist Song Count",
        },
        inplace = True,
    )
    styled_table = (
        styled_table
        .drop(columns = ["highlight"])  # Remove highlight column
        .style.apply(highlight_pop, axis = 1)
        .format(
            {"Overall Popularity": lambda x: x if x == "Null" else f"{x:.2f}",
             "Artist Popularity": lambda x: x if x == "Null" else f"{x:.2f}",
            } # Formats numbers but ignores 'Null'
        )
    )

    print(f"Popularity table for {artist_name}:")
    display(styled_table.hide(axis = 'index'))
    
    bar_width = 0.25
    # Plot the overall popularity bars
    plt.figure(figsize = (10, 6))
    plt.grid(axis = 'y', linestyle = '-', alpha = 0.7, zorder = 0)
    # zorder is defined to avoid the background lines overlapping the bars
    
    plt.bar(
        merged_popularity["genre"],
        merged_popularity["overall_popularity"],
        color = "orange",
        alpha = 1,
        width = bar_width,
        label = "Overall Popularity",
        align = "edge",  # Right of the tick positions
        zorder = 2
    )
    
    # Plot the artist popularity bars
    plt.bar(
        merged_popularity["genre"],
        merged_popularity["artist_popularity"].replace("Null", 0),
        color = "blue",
        alpha = 1,
        width = - bar_width, # Artist bars to the left via negative width
        label = f"{artist_name}'s Popularity",
        align = "edge",  
        zorder = 2
    )
    
    # Adjust x-axis to make sure tick labels are aligned
    plt.xticks(rotation = 45, ha = "right")
    plt.xlabel("Genre")
    plt.ylabel("Popularity")
    plt.title(f"Popularity Comparison for {artist_name}")
    plt.legend()
    
    plt.tight_layout()
    plt.show()
    
    
def main(artist_name):
    """
    Verifies that the inputted artist name exists within "MusicDatabase.db".
    
    Analyses and visualises the average popularity of a specified artist's
    songs across genres.
    
    Parameter:
    - artist_name (str): the inputted artist name
    
    Displays a table and bar chart.
    """
    if artist_input(artist_name) == True:
        popularity_analysis(artist_name)
    else:
        print("This is not an artist in the dataset.")
        print("For a full list of artists who are included in the dataset,")
        print("press \'Show Artist List\'.")
    
    
def name_list():
    """
    Prints the full list of artist names which appear in
    "MusicDatabase.db" in alphabetical order.
    
    No input parameter.
    """
    connection = sqlite3.connect("MusicDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Artist")
    rows = cursor.fetchall()
    print("Artist list:")
    artist_list = [row[0] for row in rows]
    artist_list = sorted(artist_list)
    for i in artist_list:
        print(i)
    connection.close()
    
    
#####
# Test code 
#####
if __name__ == "__main__":
    # Testing artist_input
    
    # Viewing the artist table (test code of Preprocessing.py),
    # its seen that 'bob' is not in db, 'DMX' is.
    print("Testing artist_input():")
    if artist_input('bob'):
        print("Failed")
    else:
        print("Passed")
            
    if artist_input('DMX'):
        print("Passed")
    else:
        print("Failed")
            
    # Testing popularity_analysis() and main():
    print("\nTesting popularity_analysis() function:")
    popularity_analysis('DMX')
    
    print("\nTesting main function:")
    main('DMX')
    