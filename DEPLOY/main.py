import requests

def get_user_repositories(user_url):
    # Extract username from the user's GitHub URL
    username = user_url.split('/')[-1]

    # Fetch the user's repositories using the GitHub API
    api_url = f'https://api.github.com/users/{username}/repos'
    response = requests.get(api_url)
    repositories = response.json()

    return repositories

def get_repository_complexity(repository):
    # Calculate complexity based on forks, stars, and size
    forks = repository['forks']
    stars = repository['stargazers_count']
    size = repository['size']
    complexity = forks + stars + size

    return complexity

def get_most_complex_repository(user_url):
    repositories = get_user_repositories(user_url)

    if not repositories:
        return None

    # Find the most complex repository
    most_complex_repo = max(repositories, key=get_repository_complexity)

    return most_complex_repo

# Example usage
# user_url = 'https://github.com/openai'
user_url="https://github.com/gitsubhamc"
most_complex_repository = get_most_complex_repository(user_url)

if most_complex_repository:
    print("Most complex repository:")
    print(f"Name: {most_complex_repository['name']}")
    print(f"Description: {most_complex_repository['description']}")
    print(f"Complexity: {get_repository_complexity(most_complex_repository)}")
else:
    print("No repositories found for the given user.")
