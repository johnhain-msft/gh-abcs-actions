import requests
import os

# Make an HTTP GET request to the cat-fact API
cat_url = "https://catfact.ninja/fact"
r = requests.get(cat_url)
r_obj = r.json()

# Get the fact directly from the response
random_fact = r_obj["fact"]

# Print the cat fact
print(random_fact)

# Set the fact output of the action using GITHUB_OUTPUT
with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
    f.write(f"fact={random_fact}\n")