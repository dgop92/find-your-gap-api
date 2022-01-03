# Find Your Gap API

Find your gap was created to find common gaps (free hours between the U classes) given the schedules of a group of classmates. It will order the results based on how close the gaps are from classes

This project is the API, The client is [GapFind](https://github.com/dgop92/GFind)

## Project setup

### Download the dependencies with pip

```
pip install -r requirements.txt
```

### Before running the project apply the respective migrations

```
python manage.py migrate
```

### Run the API in the localhost

```
python manage.py runserver
```

## API reference

There is no API reference, but you can figure out, looking at the URLs of the project and the structure of the requests and responses from the docs folder

## Motivation

I got the idea during my first year of college while struggling to find a gap to make a study group with my classmates

## How it works

### Main API endpoints

/register for users to register in the app and be available for finding gaps

The registration process uses the username and password for scrapping the schedule from the official university app. Not all information about the schedule is needed, only when the user has classes

/find for finding all possible gaps

### Algorithm for finding gaps

#### Step 1:

We retrieve from the database all _string schedules_ associated with each user then, we transform each schedule into a _distance matrix_

**string schedule:** A bit array, but in string format representing whether you have class or no. It has a fixed size of 98 because it can be parsed into a 14x7 matrix where rows represent hours and columns days.

**distance matrix:** A matrix where each element represents the distance from a class or the start/end of the day.

In other words, if the element is zero, that position in the matrix corresponds to a class, and if the element is greater than zero corresponds to a gap with distance `M[i][j]`

#### Example

For this example we'll use the following schedule, a simplified 5x4 matrix

|       | Monday  | Tuesday | Wednesday | Thursday |
|-------|---------|---------|-----------|----------|
| 6:30  |         | Class A | Class B   |          |
| 7:30  |         |         |           | Class C  |
| 8:30  | Class A | Class B |           | Class C  |
| 9:30  |         |         |           | Class C  |
| 10:30 |         |         | Class D   | Class D  |


```python

# string schedule

"0110 0001 1101 0001 0011"

# matrix representation:

[
    [0, 1, 1, 0],
    [0, 0, 0, 1],
    [1, 1, 0, 1],
    [0, 0, 0, 1],
    [0, 0, 1, 1]
]

# distance matrix

[
    [2, 0, 0, 1],
    [1, 1, 1, 0],
    [0, 0, 2, 0],
    [1, 1, 1, 0],
    [2, 2, 0, 0]
]


```

#### Step 2:

We sum all distance matrices of each user, then compute the average and a standard deviation to get the _average matrix_ and _standard-deviation matrix_

Given these matrices, we find the common gaps and sort them based on how close the gaps are from classes

## What I learned

* Real problem analysis
* Algorithm development
* Better unit tests
* Pre-commit hooks
* Different settings files (CI, DEV, PROD)
