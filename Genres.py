#####
# Genres.py
# Written by Sebastian Lynch, Jan 2025.
#####

"""
This module uses song data from "MusicDatabase.db". It retrieves and analyses
song statistics, and visualises results by genre for a given inputted year.
The program also validates that the year is within the correct range.

Classes:
- YearValidator: A class for validating year inputs within a specified range.

Functions:
- retrieve_songs(year): Queries SQLite database "MusicDatabase.db" to retrieve
  songs for the specified year.
- stats_by_genre(df, year): Computes statistics for each genre.
- style_table(genre_stats): Formats and styles the genre statistics DataFrame
  to improve readability.
- stats_vis(df): Visualises the genre statistics through a pie chart showing 
  the distribution of songs by genre and a bar chart showing the average
  popularity by genre.
- main(year): Validates the year, retrieves and processes song data and
  displays genre statistics and visualisations.

Dependencies:
- pandas
- matplotlib
- sqlite3
- IPython.display

Database Details:
- "MusicDatabase.db":
  - **Song Table**: Contains song data (e.g., title, duration, explicit, 
    popularity, and references to genre).
  - **Genre Table**: Contains unique genre names.

Usage:
- Run main() to produce the genre analysis.
- If run directly, the test code at the end of the script will be executed.
    

Written by Sebastian Lynch, Jan 2025.
"""


import matplotlib.pyplot as plt
import pandas as pd
import sqlite3
from IPython.display import display


class YearValidator:
    """
    A class for validating years within a specified range.
    """
    # attributes
    def __init__(self, start_date = 1998, end_date = 2020):
        """
        Initialises the YearValidator with a range of valid years.

        Parameters:
        - start_date (int): Starting year of the valid range (inclusive).
        - end_date (int): Ending year of the valid range (inclusive).
        """
        self.start_date = start_date
        self.end_date = end_date
    # methods
    def is_valid_year(self, year):
        """
        Validates that the inputted year is within the specified range.

        Parameters:
        - year (int or str): The year to validate.

        Returns:
        - bool: True if the year is valid, False otherwise.
        """
        try:
            year = int(year)
            return self.start_date <= year <= self.end_date
        except (ValueError, TypeError):
            return False


def retrieve_songs(year):
    """
    Queries MusicDatabase.db and retrieves all records for the specified year.
    
    Parameter:
    - year (int)
    
    Returns:
    - df (pd.DataFrame): Pandas df with columns from the song and genre tables.
    """
    try:
        connection = sqlite3.connect("MusicDatabase.db")
        query = '''
            SELECT 
                Song.Song, 
                Song.Duration, 
                Song.Explicit, 
                Song.Year, 
                Song.Popularity, 
                Song.Danceability, 
                Song.Speechiness, 
                Genre.genre 
            FROM Song 
            JOIN Genre 
            ON Song.Genre_ID = Genre.Genre_ID 
            WHERE Song.Year = ?
            '''
        df = pd.read_sql_query(query, connection, params = (year,))
        connection.close()
        return df
    except Exception as e:
        print("Error fetching data:", e)
        return pd.DataFrame()

def stats_by_genre(df, year):
    """
    Checks that the df is not empty.
    Produces table of statistics per genre in a given year.
    
    Parameters:
    - df (pd.DataFrame): Pandas df with columns 'genre', 'Danceability',
      'Popularity', 'Explicit' and 'Song'.
    - year (int)
    
    Returns:
    - genre_stats (pd.DataFrame): Table of statistics per genre in a given year.
    """
    if df.empty:
        print("There is no data available for the year %4s."%(year))
    else:
        connection = sqlite3.connect("MusicDatabase.db")
        all_genres = pd.read_sql_query("SELECT DISTINCT genre FROM Genre",
                                       connection)
        all_genres['genre'] = all_genres['genre'].str.split(', ')
        all_genres = (
            all_genres
            .explode('genre')
            .drop_duplicates()
            .reset_index(drop = True)
        )

        connection.close()
        df['genre'] = df['genre'].str.split(', ')
        df_exploded = df.explode('genre')
        genre_stats = df_exploded.groupby('genre').agg(
            avg_danceability = ('Danceability', 'mean'),
            avg_popularity = ('Popularity', 'mean'),
            explicit_pct = ('Explicit', 'mean'),
            song_count = ('Song', 'count')
        ).reset_index()
        genre_stats = pd.merge(
            all_genres,
            genre_stats,
            on = 'genre',
            how = 'left'
        )
        genre_stats['explicit_pct'] = genre_stats['explicit_pct'] * 100
        genre_stats = genre_stats.round(2)
        genre_stats['avg_danceability'] = (
            genre_stats['avg_danceability'].fillna("Null")
        )
        genre_stats['avg_popularity'] = (
            genre_stats['avg_popularity'].fillna("Null")
        )
        genre_stats['explicit_pct'] = (
            genre_stats['explicit_pct'].fillna("Null")
        )
        genre_stats['song_count'] = (
            genre_stats['song_count'].fillna(0).astype(int)
        )
        
        return genre_stats

def style_table(genre_stats):
    """
    Renames columns, drops index of genre_stats from stats_by_genre().
    
    Parameter:
    - genre_stats (pd.DataFrame): DataFrame containing genre statistics.
    
    Returns:
    - genre_stats_styled (pd.DataFrame): Styled DataFrame with renamed columns
      and index reset.
    """
    genre_stats_styled = genre_stats.copy()
    
    genre_stats_styled.rename(
        columns = {
            "genre": "Genre",
            "avg_danceability": "Average Danceability",
            "avg_popularity": "Average Popularity",
            "explicit_pct": "Explicit Percentage",
            "song_count": "Song Count",
        },
        inplace = True,
    )
    
    genre_stats_styled = genre_stats_styled.style.format({
        "Average Danceability": lambda x: x if x == "Null" else f"{x:.2f}",
        "Average Popularity": lambda x: x if x == "Null" else f"{x:.2f}",
        "Explicit Percentage": lambda x: x if x == "Null" else f"{x:.2f}",
        "Song Count": "{:d}"
    }) # Lambda x... formats numbers but ignores 'Null'
    
    return genre_stats_styled


def stats_vis(df):
    """
    Visualises the distribution of songs and their average popularity by genre
    through a visualisation with both a pie chart showing the percentage
    distribution of songs per genre and a bar chart showing the average
    popularity for each genre.
    
    Parameter:
    - df (pd.DataFrame): Pandas df featuring columns 'genre', 'song_count',
      'avg_popularity'.
    """
    pd.set_option('future.no_silent_downcasting', True)
    df = df.replace("Null", int(0))
    df = df[df["song_count"] > 0]
    colors = plt.cm.tab20.colors  # Colour map to match genres in each chart.
    color_mapping = {genre: colors[i % len(colors)] for i,
                     genre in enumerate(df["genre"])
                    }
    genre_colors = [color_mapping[genre] for genre in df["genre"]]
    fig, ax = plt.subplots(1, 2, figsize = (14, 6))

    # Pie chart
    ax[0].pie(
        df["song_count"],
        labels = df["genre"],  
        autopct = '%1.1f%%',
        startangle = 140,
        colors = genre_colors
    )
    ax[0].set_title("Distribution of Songs per Genre")
    
    # Bar chart for avg_popularity
    ax[1].bar(
        df["genre"],
        df["avg_popularity"],
        color = genre_colors,
        alpha = 1,
        zorder = 2
    )
    ax[1].set_title("Average Popularity per Genre")
    ax[1].set_xlabel("Genre")
    ax[1].set_ylabel("Average Popularity")
    ax[1].tick_params(axis = 'x', rotation = 45)
    ax[1].grid(axis = 'y', linestyle = '-', alpha = 0.7, zorder = 0)
    plt.tight_layout()
    plt.show()

def main(year):
    """
    Validates that the inputted year is from 1998-2020.
    Queries MusicDatabase.db and retrieves all records for the specified year.
    Calculates and displays a table of stats per genre and 2 visualisations
    in the form of a pie chart and a bar chart.
    
    Parameter:
    - year (int)
    """
    validator = YearValidator()  # Validator for default range 1998-2020.
    
    if validator.is_valid_year(year):
        song_year_df = retrieve_songs(year)
        genre_stats = stats_by_genre(song_year_df, year)
        if isinstance(genre_stats, pd.DataFrame):
            genre_stats_styled = style_table(genre_stats)
            display(genre_stats_styled.hide(axis='index'))
            stats_vis(genre_stats)
    else:
        print("This is not a valid year.")
        print("Please make sure to enter a year in the range 1998-2020.")

#####
# Test code 
#####
if __name__ == "__main__":
    # Testing the YearValidator with some test years
    validator = YearValidator()
    test_years = [0, 1997, 1998, 2000, 2020, 2021, "invalid", "2000"]
    for year in test_years:
        result = validator.is_valid_year(year)
        print(f"Year {year} is {'valid' if result else 'invalid'}.")
    
    # Test retrieve_songs function
    print("\nTesting retrieve_songs in 2000:")
    test_year = 2000
    df = retrieve_songs(test_year)
    if not df.empty:
        print(f"Retrieved {len(df)} songs for the year {test_year}.")
    else:
        print(f"No data available for the year {test_year}.")
        
    print("\nTesting retrieve_songs in 2019:")
    test_year = 2019
    df = retrieve_songs(test_year)
    if not df.empty:
        print(f"Retrieved {len(df)} songs for the year {test_year}.")
    else:
        print(f"No data available for the year {test_year}.")
    
    # Test stats_by_genre function
    print("\nTesting stats_by_genre:")
    if not df.empty:
        genre_stats = stats_by_genre(df, test_year)
        print("Genre statistics:")
        print(genre_stats)
    else:
        print("No data to calculate statistics.")
    
    # Test style_table function
    print("\nTesting style_table:")
    if 'genre_stats' in locals():
        styled_stats = style_table(genre_stats)
        print("Styled statistics generated successfully.")
    else:
        print("No statistics available to style.")
    
    # Test stats_vis function
    print("\nTesting stats_vis:")
    if 'genre_stats' in locals() and not genre_stats.empty:
        print("Generating visualizations...")
        stats_vis(genre_stats)
        print("Visualizations generated successfully.")
    else:
        print("No data available for visualizations.")
    
    # Main function test
    print("\nTesting main function:")
    print("Testing valid year input which is empty:")
    main(2000)
    print("Testing valid year input:")
    main(2019)
    print("\nTesting invalid year input:")
    main(1997)