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