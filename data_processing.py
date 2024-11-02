import requests
import pandas as pd
import time

# GitHub API URL and headers
GITHUB_API_URL = "https://api.github.com"
TOKEN = "#############################"  
HEADERS = {'Authorization': f'token {TOKEN}'}

def fetch_users(city="Shanghai", min_followers=200):
    users = []
    page = 1
    while True:
        query = f"location:{city}+followers:>{min_followers}"
        url = f"{GITHUB_API_URL}/search/users?q={query}&page={page}&per_page=100"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"Error fetching users: {response.status_code}")
            break

        data = response.json().get("items", [])
        if not data:
            break

        users.extend(data)
        page += 1
        time.sleep(1)  # Delay to respect rate limits

    return users

def fetch_user_repositories(username, max_repos=500):
    repos = []
    page = 1
    while len(repos) < max_repos:
        url = f"{GITHUB_API_URL}/users/{username}/repos?page={page}&per_page=100"
        response = requests.get(url, headers=HEADERS)

        if response.status_code != 200:
            print(f"Error fetching repos for {username}: {response.status_code}")
            break

        data = response.json()
        if not data:
            break

        repos.extend(data)
        page += 1
        time.sleep(1)  # Delay to respect rate limits

    return repos[:max_repos]

def fetch_user_details(username):
    url = f"{GITHUB_API_URL}/users/{username}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching user details for {username}: {response.status_code}")
        return {}

def process_user_data(users):
    user_data = []
    for user in users:
        user_details = fetch_user_details(user['login'])
        user_data.append({
            'login': user['login'],
            'name': user_details.get('name', ''),
            'company': (user_details.get('company') or '').strip('@').upper(),  # Ensure it's not None
            'location': user_details.get('location', ''),
            'email': user_details.get('email', ''),
            'hireable': user_details.get('hireable', ''),
            'bio': user_details.get('bio', ''),
            'public_repos': user_details.get('public_repos', 0),
            'followers': user_details.get('followers', 0),
            'following': user_details.get('following', 0),
            'created_at': user_details.get('created_at', '')
        })

    return pd.DataFrame(user_data)

def process_repository_data(repositories):
    repo_data = []
    for repo in repositories:
        license_name = repo.get('license')
        license_name = license_name['name'] if license_name else ''  # Check if license_name is None

        repo_data.append({
            'login': repo['owner']['login'],
            'full_name': repo['full_name'],
            'created_at': repo['created_at'],
            'stargazers_count': repo['stargazers_count'],
            'watchers_count': repo['watchers_count'],
            'language': repo['language'],
            'has_projects': repo.get('has_projects', False),
            'has_wiki': repo.get('has_wiki', False),
            'license_name': license_name  # Use the determined license name
        })

    return pd.DataFrame(repo_data)

def save_to_csv(users_df, repos_df):
    users_df.to_csv('users.csv', index=False)
    repos_df.to_csv('repositories.csv', index=False)
    print("Data saved as 'users.csv' and 'repositories.csv' in the current directory.")

def main():
    # Fetch users
    users = fetch_users()
    users_df = process_user_data(users)

    # Fetch repositories for each user and store them
    all_repos = []
    for user in users_df['login']:
        repos = fetch_user_repositories(user)
        all_repos.extend(repos)

    # Process repositories data and save
    repos_df = process_repository_data(all_repos)
    save_to_csv(users_df, repos_df)

# Run the main function to fetch and save data
main()




def load_data(users_file, repos_file):
    # Load the CSV files into DataFrames
    users_df = pd.read_csv(users_file)
    repos_df = pd.read_csv(repos_file)
    return users_df, repos_df

def get_top_users(users_df, n=5):
    # Sort users by followers in descending order
    sorted_users = users_df.sort_values(by='followers', ascending=False)

    # Get top n users
    top_users = sorted_users.head(n)

    # Extract their logins
    return top_users['login'].tolist()

# File names of the datasets
users_file = 'users.csv'  # Change if necessary
repos_file = 'repositories.csv'  # Change if necessary

# Load the data
users_df, repos_df = load_data(users_file, repos_file)

# Get and print the top 5 users in Shanghai by followers
top_users = get_top_users(users_df)
print("Top 5 users in Shanghai with highest followers:", ", ".join(top_users))



def load_data(users_file):
    # Load the CSV file into a DataFrame
    users_df = pd.read_csv(users_file)
    return users_df

def get_earliest_users(users_df, city='Shanghai', n=5):
    # Filter users by location
    shanghai_users = users_df[users_df['location'] == city]

    # Convert created_at to datetime format for sorting
    shanghai_users['created_at'] = pd.to_datetime(shanghai_users['created_at'])

    # Sort users by created_at in ascending order and get top n users
    earliest_users = shanghai_users.sort_values(by='created_at').head(n)

    # Extract their logins
    return earliest_users['login'].tolist()

# File name of the dataset
users_file = 'users.csv'  # Change if necessary

# Load the data
users_df = load_data(users_file)

# Get and print the 5 earliest registered users in Shanghai
earliest_users = get_earliest_users(users_df)
print("5 earliest registered GitHub users in Shanghai:", ", ".join(earliest_users))


# Load the dataset
users_file = 'users.csv'  # Ensure the file path is correct
users_df = pd.read_csv(users_file)

# Filter for users in Shanghai and drop rows with missing 'created_at'
shanghai_users = users_df[users_df['location'].str.contains("Shanghai", na=False)]

# Convert 'created_at' to datetime
shanghai_users['created_at'] = pd.to_datetime(shanghai_users['created_at'])

# Sort by 'created_at' and get the top 5 earliest users
earliest_users = shanghai_users.nsmallest(5, 'created_at')[['login', 'created_at']]

# Extract logins as a comma-separated string
earliest_logins = ', '.join(earliest_users['login'])
print(earliest_logins)


# Load the repositories dataset
repos_file = 'repositories.csv'  # Ensure the file path is correct
repos_df = pd.read_csv(repos_file)

# Filter out rows with missing licenses
repos_df = repos_df[repos_df['license_name'].notna()]

# Count the occurrences of each license
license_counts = repos_df['license_name'].value_counts()

# Get the top 3 most popular licenses
top_licenses = license_counts.nlargest(3)

# Extract the license names in order as a comma-separated string
most_popular_licenses = ', '.join(top_licenses.index)
print(most_popular_licenses)


users_df['company'] = users_df['company'].str.upper().str.strip('@')

# Drop any rows with missing values in 'company'
users_df = users_df.dropna(subset=['company'])

# Find the most frequent company
top_company = users_df['company'].mode()[0]
print(f"The majority of developers work at: {top_company}")

repos_df = repos_df.dropna(subset=['language'])

# Find the most common programming language
most_popular_language = repos_df['language'].mode()[0]
print(f"The most popular programming language among these users is: {most_popular_language}")


users_after_2020 = users_df[pd.to_datetime(users_df['created_at']) > '2020-12-31']

# Get the list of usernames for these users
users_after_2020_logins = users_after_2020['login'].tolist()

# Filter repositories for these users
repos_after_2020 = repos_df[repos_df['login'].isin(users_after_2020_logins)]

# Drop rows where 'language' is missing
repos_after_2020 = repos_after_2020.dropna(subset=['language'])

# Count the occurrences of each language
language_counts = repos_after_2020['language'].value_counts()

# Get the second most popular language
second_most_popular_language = language_counts.index[1]
print(f"The second most popular programming language among users who joined after 2020 is: {second_most_popular_language}")


# Drop rows with missing 'language' or 'stargazers_count' data
repos_df = repos_df.dropna(subset=['language', 'stargazers_count'])

# Group by language and calculate the average number of stars per language
average_stars_per_language = repos_df.groupby('language')['stargazers_count'].mean()

# Identify the language with the highest average stars
most_popular_language = average_stars_per_language.idxmax()
highest_avg_stars = average_stars_per_language.max()

print(f"The language with the highest average number of stars per repository is: {most_popular_language}, with an average of {highest_avg_stars:.2f} stars.")

users_df['leader_strength'] = users_df['followers'] / (1 + users_df['following'])

# Sort by leader_strength in descending order
top_leaders = users_df.sort_values(by='leader_strength', ascending=False).head(5)

# Get the login names of the top 5 users
top_leader_logins = ','.join(top_leaders['login'].tolist())

print(f"The top 5 users by leader_strength are: {top_leader_logins}")


correlation = users_df['followers'].corr(users_df['public_repos'])

# Display the correlation to 3 decimal places
print(f"Correlation between followers and public_repos: {correlation:.3f}")

users_df = pd.read_csv('users.csv')

# Perform linear regression
slope, intercept, r_value, p_value, std_err = linregress(users_df['public_repos'], users_df['followers'])

# Display the regression slope to 3 decimal places
print(f"Regression slope of followers on public_repos: {slope:.3f}")


correlation = repos_df['has_projects'].corr(repos_df['has_wiki'])

# Display the correlation rounded to 3 decimal places
print(f"Correlation between projects and wiki enabled: {correlation:.3f}")

# Calculate the average 'following' for hireable and non-hireable users
avg_following_hireable = users_df[users_df['hireable'] == True]['following'].mean()
avg_following_non_hireable = users_df[users_df['hireable'] == False]['following'].mean()

# Calculate the difference
difference = avg_following_hireable - avg_following_non_hireable

# Display the result rounded to 3 decimal places
print(f"Difference in average following (hireable - non-hireable): {difference:.3f}")

# Filter out rows without bios
users_with_bios = users_df.dropna(subset=['bio'])

# Calculate word count in each bio by splitting on whitespace
users_with_bios['bio_word_count'] = users_with_bios['bio'].apply(lambda x: len(x.split()))

# Prepare the independent (X) and dependent (y) variables
X = users_with_bios[['bio_word_count']]
y = users_with_bios['followers']

# Fit the linear regression model
model = LinearRegression()
model.fit(X, y)

# Retrieve the slope of the regression
slope = model.coef_[0]

# Display the result rounded to 3 decimal places
print(f"Regression slope of followers on bio word count: {slope:.3f}")

# Convert 'created_at' to datetime
repos_df['created_at'] = pd.to_datetime(repos_df['created_at'])

# Filter for weekend days (Saturday=5, Sunday=6)
repos_df['is_weekend'] = repos_df['created_at'].dt.dayofweek.isin([5, 6])

# Group by user login and count repositories created on weekends
weekend_repos = repos_df[repos_df['is_weekend']].groupby('login').size().reset_index(name='repo_count')

# Sort by the number of repositories in descending order and get top 5
top_users = weekend_repos.sort_values(by='repo_count', ascending=False).head(5)

# Get the user logins
top_user_logins = top_users['login'].tolist()

# Print the top 5 user logins, comma-separated
print(', '.join(top_user_logins))


# Calculate the fraction of users with email when hireable=True
hireable_with_email = users_df[users_df['hireable'] == True]['email'].notna().mean()

# Calculate the fraction of users with email when hireable=False
not_hireable_with_email = users_df[users_df['hireable'] == False]['email'].notna().mean()

# Calculate the difference
email_difference = hireable_with_email - not_hireable_with_email

# Print the result rounded to 3 decimal places
print(round(email_difference, 3))


# Check if there are any hireable users
hireable_users = users_df[users_df['hireable'] == True]
not_hireable_users = users_df[users_df['hireable'] == False]

# Calculate the fraction of users with email when hireable=True
if not hireable_users.empty:
    hireable_with_email = hireable_users['email'].notna().mean()
else:
    hireable_with_email = 0

# Calculate the fraction of users with email when hireable=False
if not not_hireable_users.empty:
    not_hireable_with_email = not_hireable_users['email'].notna().mean()
else:
    not_hireable_with_email = 0

# Calculate the difference
email_difference = hireable_with_email - not_hireable_with_email

# Print the result rounded to 3 decimal places
print(round(email_difference, 3))


users_df['surname'] = users_df['name'].dropna().apply(lambda x: x.strip().split()[-1])

# Count the occurrences of each surname
surname_counts = users_df['surname'].value_counts()

# Find the most common surname(s)
most_common_surname = surname_counts[surname_counts == surname_counts.max()]

# Prepare the result as a comma-separated string, sorted alphabetically
result = ', '.join(sorted(most_common_surname.index))

# Print the result
print(result)
missing_following_count = users_df['following'].isna().sum()
print(f"Number of missing values in 'following': {missing_following_count}")

# Check how many users are hireable and non-hireable
hireable_count = users_df[users_df['hireable'] == True].shape[0]
non_hireable_count = users_df[users_df['hireable'] == False].shape[0]
print(f"Number of hireable users: {hireable_count}")
print(f"Number of non-hireable users: {non_hireable_count}")

# Drop rows with missing values in 'following'
users_df = users_df.dropna(subset=['following'])

# Calculate the average following for hireable users
avg_following_hireable = users_df[users_df['hireable'] == True]['following'].mean()

# Calculate the average following for non-hireable users
avg_following_non_hireable = users_df[users_df['hireable'] == False]['following'].mean()

# Calculate the difference
difference = avg_following_hireable - avg_following_non_hireable

# Print the result rounded to 3 decimal places
print(round(difference, 3))

missing_following_count = users_df['following'].isna().sum()
print(f"Number of missing values in 'following': {missing_following_count}")

# Check how many users are hireable and non-hireable
hireable_count = users_df[users_df['hireable'] == True].shape[0]
non_hireable_count = users_df[users_df['hireable'] == False].shape[0]
print(f"Number of hireable users: {hireable_count}")
print(f"Number of non-hireable users: {non_hireable_count}")

# Drop rows with missing values in 'following'
users_df = users_df.dropna(subset=['following'])

# Calculate the average following for hireable users
avg_following_hireable = users_df[users_df['hireable'] == True]['following'].mean()

# Check for non-hireable users and calculate the difference if applicable
if non_hireable_count > 0:
    avg_following_non_hireable = users_df[users_df['hireable'] == False]['following'].mean()
    # Calculate the difference
    difference = avg_following_hireable - avg_following_non_hireable
else:
    difference = avg_following_hireable  # Only hireable users exist

# Print the result rounded to 3 decimal places
print(round(difference, 3))