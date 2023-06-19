import requests
import json
import re
from flask import Flask, render_template, request

app = Flask(__name__)

GPT_API_KEY = 'YOUR_GPT_API_KEY'
LANGCHAIN_API_KEY = 'YOUR_LANGCHAIN_API_KEY'

def preprocess_code(code):
    # Remove excessive line breaks and leading/trailing white spaces
    code = re.sub(r'\n+', '\n', code)
    code = code.strip()

    # Split code into chunks to fit within GPT token limits
    MAX_TOKENS = 4096  # Maximum tokens supported by GPT-3.5
    code_chunks = [code[i:i+MAX_TOKENS] for i in range(0, len(code), MAX_TOKENS)]

    return code_chunks

def assess_code_complexity(code):
    # Preprocess code
    code_chunks = preprocess_code(code)

    complexity_scores = []
    # Make an API request to GPT for prompt engineering and code complexity evaluation
    for chunk in code_chunks:
        gpt_input = f"Assess the technical complexity of the following code:\n\n```python\n{chunk}\n```"
        response = requests.post(
            GPT_API_URL,
            headers={'Authorization': f'Bearer {GPT_API_KEY}'},
            json={'prompt': gpt_input}
        )
        complexity_score = response.json()['choices'][0]['text']
        complexity_scores.append(complexity_score)

    # Sum the complexity scores for the entire code
    total_complexity_score = sum(complexity_scores)

    return total_complexity_score

def assess_repository_complexity(repository):
    # Check if repository is a Jupyter notebook
    if repository['name'].endswith('.ipynb'):
        # Preprocess notebook by extracting code cells
        notebook_url = repository['html_url']
        notebook_content = requests.get(notebook_url).json()
        code_cells = notebook_content['cells']
        code = '\n'.join(cell['source'] for cell in code_cells if cell['cell_type'] == 'code')
    else:
        # Repository is not a notebook, fetch the code
        code_url = repository['contents_url'].replace('{+path}', '')
        response = requests.get(code_url)
        code = response.text

    # Assess the complexity of the code using GPT
    complexity_score = assess_code_complexity(code)

    return complexity_score

def get_most_complex_repository(user_url):
    # Extract username from the user's GitHub URL
    username = user_url.split('/')[-1]

    # Fetch the user's repositories using the GitHub API
    api_url = f'https://api.github.com/users/{username}/repos'
    response = requests.get(api_url)
    repositories = response.json()

    if not repositories:
        return None

    most_complex_repo = None
    max_complexity_score = float('-inf')

    # Iterate over each repository and assess its complexity
    for repository in repositories:
        complexity_score = assess_repository_complexity(repository)

        # Update the most complex repository if needed
        if complexity_score > max_complexity_score:
            max_complexity_score = complexity_score
            most_complex_repo = repository

    return most_complex_repo

@app.route('/', methods=['GET', 'POST'])
def analyze_user_repositories():
    if request.method == 'POST':
        user_url = request.form['user_url']
        most_complex_repository = get_most_complex_repository(user_url)

        if most_complex_repository:
            repository_name = most_complex_repository['name']
            repository_url = most_complex_repository['html_url']
            repository_analysis = f"Justification for selecting {repository_name}: [GPT analysis goes here]"

            return render_template('result.html', repository_name=repository_name, repository_url=repository_url, repository_analysis=repository_analysis)
        else:
            error_message = 'No repositories found for the given user.'
            return render_template('index.html', error_message=error_message)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
