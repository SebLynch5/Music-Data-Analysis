#####
# Preprocessing.py 
# Written by Sebastian Lynch, Jan 2025.
#####

"""
This module processes song data from "songs.csv" and creates an SQLite database
consisting of three tables: Artist, Genre, and Song. It also cleans the data,
by filtering 3 variables and changing a specific column. Finally, the program
populates the database with the cleaned data.

Functions:
- clean_duration(df): Cleans the 'duration_ms' column by converting it to
  seconds, rounding, and renaming it to 'duration'.
- filter1(df, column, lower, upper): Filters rows of a DataFrame based on a
  specified column's values within a given range.
- create_db(): Creates the SQLite database 'Database.db' with three tables: 
  Artist, Genre, and Song.
- populate_db(dfSongs): Populates the database tables with data from a cleaned
  and filtered DataFrame.
- main(): Executes the complete workflow by:
  1. Reading the "songs.csv" file.
  2. Cleaning the 'duration_ms' column using clean_duration().
  3. Applying filters for popularity, speechiness, and danceability values.
  4. Removing duplicate entries.
  5. Creating and populating the SQLite database, "Database.db".

Database Details:
- "Database.db":
  - **Artist Table**: Contains artist names and unique IDs.
  - **Genre Table**: Contains genre names and unique IDs.
  - **Song Table**: Stores song data, including title, duration, explicit,
    year, popularity, danceability, speechiness, and references to Artist_ID 
    and Genre_ID.

Usage:
- Run main() or this script directly to process 'songs.csv', and create and
  populate the database.
- If run directly, the test code at the end of the script will also be executed.

Dependencies:
- pandas
- sqlite3

Written by Sebastian Lynch, Jan 2025.
"""


import pandas as pd
import sqlite3

def clean_duration(df):
    """
    Renames duration_ms to duration.
    Also converts milliseconds to seconds in the duration column
    and rounds to an integer.
    
    Parameter:
    - df (pd.DataFrame): The pandas DataFrame.
    
    Returns:
    - pd.DataFrame: The cleaned DataFrame.
    """
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors = 'coerce')
    df.rename(columns = {"duration_ms": "duration"}, inplace = True)
    df["duration"] = (df["duration"] / 1000).fillna(0).round(0).astype(int)
    return df


    
def filter1(df, column, lower = - float('inf'), upper = float('inf')):
    """
    Filters the rows of a DataFrame based on a specified column's values.

    Parameters:
    - df (pd.DataFrame): The pandas DataFrame to filter.
    - column (str): The column name to apply the filter on.
    - lower (float): The lower bound for filtering. Default is -infinity.
    - upper (float): The upper bound for filtering. Default is infinity.

    Returns:
    - pd.DataFrame: The filtered DataFrame.
    """
    df[column] = pd.to_numeric(df[column], errors = 'coerce')
    df[column] = df[column].fillna(0)
    return df[(df[column] > lower) & (df[column] < upper)]

def create_db():
    """
    Creates the SQL database and its 3 tables.
    
    No input parameters.
    """
    connection = sqlite3.connect("MusicDatabase.db") # Connect to db
    cursor = connection.cursor() 
    cursor.execute('CREATE TABLE IF NOT EXISTS Artist \
                   (artist TEXT, \
                    Artist_ID INTEGER PRIMARY KEY AUTOINCREMENT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS Genre \
                   (genre TEXT, \
                    Genre_ID INTEGER PRIMARY KEY AUTOINCREMENT)')
    cursor.execute('CREATE TABLE IF NOT EXISTS Song \
                    (Song TEXT, \
                     Duration INTEGER, \
                     Explicit BOOLEAN, \
                     Year INTEGER, \
                     Popularity INTEGER, \
                     Danceability REAL, \
                     Speechiness REAL, \
                     Artist_ID TEXT, \
                     Genre_ID TEXT, \
                     FOREIGN KEY (Artist_ID) REFERENCES Artist(Artist_ID), \
                     FOREIGN KEY (Genre_ID) REFERENCES Genre(Genre_ID))')
    connection.commit()
    connection.close() # Close connection
    

def populate_db(dfSongs):
    """
    Populate the SQLite database's Artist, Genre, and Song tables with
    the cleaned songs data.
    
    Parameter:
    - dfSongs (pd.DataFrame): The pandas DataFrame whose data fills the tables.
    """
    connection = sqlite3.connect("MusicDatabase.db")
    cursor = connection.cursor()

    # Filling the Artist table
    dfArtists = dfSongs[['artist']].drop_duplicates().reset_index(drop = True)
    dfArtists['Artist_ID'] = dfArtists.index + 1  # Unique IDs for each artist
    dfArtists.to_sql("Artist", connection, if_exists = "replace", index = False)

    # Filling the Genre table
    dfGenres = dfSongs[['genre']].drop_duplicates().reset_index(drop = True)
    dfGenres['Genre_ID'] = dfGenres.index + 1  # Unique IDs for each genre
    dfGenres.to_sql("Genre", connection, if_exists = "replace", index = False)

    # Filling the Song table 
    # Start by merging dfSongs with dfArtists, dfGenres for the ID columns
    dfSongs = dfSongs.merge(dfArtists, on = 'artist', how = 'left')
    dfSongs = dfSongs.merge(dfGenres, on = 'genre', how = 'left')

    dfSongs = dfSongs.rename(columns = {
        'song': 'Song',
        'duration': 'Duration',
        'explicit': 'Explicit',
        'year': 'Year',
        'popularity': 'Popularity',
        'danceability': 'Danceability',
        'speechiness': 'Speechiness'
    })
    song_columns = ['Song',
                    'Duration',
                    'Explicit',
                    'Year',
                    'Popularity',
                    'Danceability',
                    'Speechiness',
                    'Artist_ID',
                    'Genre_ID'
                   ]
    dfSongs[song_columns].to_sql("Song",
                                 connection,
                                 if_exists = "replace",
                                 index = False
                                )

    connection.commit()
    connection.close()

    
def main():
    """
    Creates and populates Artist, Genre, and Song tables in "MusicDatabase.db".
    The database is populated by a filtered set of songs from "songs.csv".
    Filters are popularity > 50, 0.33 < speechiness < 0.66, danceability > 0.2.
    Duration is measured in seconds in the database (rather than ms in the csv).
    
    No input parameters.
    """
    dfSongs = pd.read_csv("songs.csv")
    dfSongs = clean_duration(dfSongs)
    dfSongs = filter1(df = dfSongs,
                      column = "popularity",
                      lower = 50
                     )
    dfSongs = filter1(df = dfSongs,
                      column = "speechiness",
                      lower = 0.33,
                      upper = 0.66
                     )
    dfSongs = filter1(df = dfSongs,
                      column = "danceability",
                      lower = 0.2
                     )
    dfSongs = dfSongs.drop_duplicates()
    create_db()
    populate_db(dfSongs)
    
    
#####
# TEST CODE 
#####

if __name__ == "__main__":
    # creating testing data 
    data = (
    """
    song,artist,genre,duration_ms,explicit,year,popularity,danceability,speech
    Song1,Artist1,Pop, ,True,2018,60,0.7,0.4
    Song2,Artist2,Rock,250000,False,2019,55,0.6,0.5
    Song3,Artist3,Pop,159999,True,2020,65,0.8,0.3
    Song4,Artist3,dance,20001,False,1999,49,0.3,0.5
    """
    )
    # Put data in a csv file
    with open("cw_test_data.csv", "w") as f:
        f.write(data)
    
    # Read the csv file
    test_data_df = pd.read_csv("cw_test_data.csv")
    test_data_df.rename(columns = {"speech": "speechiness"})
    
    # Test clean_duration()
    test_data_df_duration = clean_duration(test_data_df)
    print("duration column (test data):")
    print(test_data_df_duration["duration"])
        
    # Test filter1
    test_df_filtered = filter1(test_data_df, 'popularity', 50)
    print("Song names after filter test:")
    print(test_df_filtered)
    assert test_df_filtered.shape[0] == 3, "Filtering failed; song4"
    print("filter1() passed.")
    
    # Rather than testing both create_db() and populate_db() with test
    # data, I have opted to instead fully print the tables using the 
    # songs.csv data. Viewing these tables shows that they have been
    # created correctly.
    
    connection = sqlite3.connect("MusicDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Song")
    rows = cursor.fetchall()
    print("Song Table:")
    for row in rows:
        print(row)
    connection.close()

    connection = sqlite3.connect("MusicDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Genre")
    rows = cursor.fetchall()
    print("Genre Table:")
    for row in rows:
        print(row)
    connection.close()

    connection = sqlite3.connect("MusicDatabase.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Artist")
    rows = cursor.fetchall()
    print("Artist Table:")
    for row in rows:
        print(row)
    connection.close()