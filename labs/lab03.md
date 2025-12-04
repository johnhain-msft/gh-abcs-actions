# 3 - Environments and Secrets
In this lab you will use environments and secrets.
> Duration: 10-15 minutes

References:
- [Using environments for deployment](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [Encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Accessing your secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#accessing-your-secrets)

## 3.1 Create new encrypted secrets

1. Follow the guide to create a new environment called `UAT`, add a reviewer and an environment variable.
    - [Creating an environment](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#creating-an-environment)
    - [Add required reviewers](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment#required-reviewers)
    - [Create an encrypted secret in the environment](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-an-environment) called `MY_ENV_SECRET`.
2. Follow the guide to create a new repository secret called `MY_REPO_SECRET`
    - [Creating encrypted secrets for a repository](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository)
4. Open the workflow file [environments-secrets.yml](/.github/workflows/environments-secrets.yml)
5. Edit the file and copy the following YAML content as a first job (after the `jobs:` line):
```YAML

  use-secrets:
    name: Use secrets
    runs-on: ubuntu-latest
    if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
    steps:
      - name: Hello world action with secrets
        uses: actions/hello-world-javascript-action@main
        with: # Set the secret as an input
          who-to-greet: ${{ secrets.MY_REPO_SECRET }}
        env: # Or as an environment variable
          super_secret: ${{ secrets.MY_REPO_SECRET }}
      - name: Echo secret is redacted in the logs
        run: |
          echo Env secret is ${{ secrets.MY_REPO_SECRET }}
          echo Warning: GitHub automatically redacts secrets printed to the log, 
          echo          but you should avoid printing secrets to the log intentionally.
          echo ${{ secrets.MY_REPO_SECRET }} | sed 's/./& /g'
```
6. Update the workflow to also run on push and pull_request events
```YAML
on:
  push:
     branches: [main]
  pull_request:
     branches: [main]
  workflow_dispatch:    
```
7. Commit the changes into the `main` branch
8. Go to `Actions` and see the details of your running workflow


## 3.2 Add a new workflow job to deploy to UAT environment

1. Open the workflow file [environments-secrets.yml](/.github/workflows/environments-secrets.yml)
2. Edit the file and copy the following YAML content between the test and prod jobs (before the `use-environment-prod:` line):
```YAML

  use-environment-uat:
    name: Use UAT environment
    runs-on: ubuntu-latest
    if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
    needs: use-environment-test

    environment:
      name: UAT
      url: 'https://uat.github.com'
    
    steps:
      - name: Step that uses the UAT environment
        run: echo "Deployment to UAT..."
        env: 
          env_secret: ${{ secrets.MY_ENV_SECRET }}

```
7. Inside the `use-environment-prod` job, replace `needs: use-environment-test` with:
```YAML
    needs: use-environment-uat
```
8. Commit the changes into the `main` branch
9. Go to `Actions` and see the details of your running workflow
10. Review your deployment and approve the pending UAT job
    - [Reviewing deployments](https://docs.github.com/en/actions/managing-workflow-runs/reviewing-deployments)
11. Go to `Settings` > `Environments` and update the `PROD` environment created to protect it with approvals (same as UAT)

## 3.3 Programmatic Deployment Review (Advanced - Optional)

> **Note:** This section is **optional** and more advanced. It requires setting up a GitHub App. Sections 3.1 and 3.2 can be completed independently.

### What You'll Learn

After completing this section, you will understand:
- How to create and configure a GitHub App for workflow automation
- Why GitHub Apps are needed for programmatic deployment approvals (vs. `GITHUB_TOKEN`)
- How to generate installation tokens using `workflow-application-token-action`
- How to call the GitHub REST API from within a workflow using `github-script`
- The structure of the `reviewPendingDeploymentsForRun` API call

### Purpose and Use Cases

The [review-pending-deployments.yml](/.github/workflows/review-pending-deployments.yml) workflow demonstrates:
- **Automated deployment gates**: Approve/reject deployments based on external conditions (test results, security scans, change windows)
- **Integration with external systems**: Let CI/CD tools, ticketing systems, or chat bots control deployment approvals
- **Bulk operations**: Approve multiple pending deployments without manual UI clicks

### Prerequisites

This workflow requires a **GitHub App** for authentication because the default `GITHUB_TOKEN` cannot approve deployments in the same repository (security restriction).

#### Create a GitHub App

1. Go to **Settings** > **Developer settings** > **GitHub Apps** > **New GitHub App**
2. Configure the app:
   - **Name**: `<your-org>-deployment-reviewer` (or similar)
   - **Homepage URL**: Your repository URL
   - **Webhook**: Uncheck "Active" (not needed)
3. Set **Permissions**:
   - **Repository permissions**:
     - Actions: Read and write
     - Contents: Read-only
     - Deployments: Read and write
4. Click **Create GitHub App**
5. Note the **App ID** (displayed on the app settings page)
6. Generate a **Private Key** (scroll down, click "Generate a private key")
   - Save the downloaded `.pem` file securely

#### Install the App and Configure Secrets

1. On your GitHub App page, click **Install App** in the sidebar
2. Choose your repository and click **Install**
3. In your repository, go to **Settings** > **Secrets and variables** > **Actions**
4. Create two secrets:
   - `GH_ABCS_APP_ACTIONS_APP_ID`: Your App ID
   - `GH_ABCS_APP_ACTIONS_APP_PRIVATE_KEY`: Contents of the `.pem` file

### Review the Workflow

1. Open the workflow file [review-pending-deployments.yml](/.github/workflows/review-pending-deployments.yml)
2. Read through the file and identify the key sections described below.

**Workflow Inputs (lines 4-24):** The workflow uses `workflow_dispatch` with manual inputs:
- `run_id` - Which workflow run has pending deployments
- `environment_ids` - Which environment(s) to approve/reject
- `state` - Either `approved` or `rejected`
- `comment` - Message to include with the review

**Step 1 - Get Token (lines 37-43):** Generates a GitHub App token using [peter-murray/workflow-application-token-action](https://github.com/peter-murray/workflow-application-token-action):
```yaml
- name: Get Token
  id: get_workflow_token
  uses: peter-murray/workflow-application-token-action@v3
  with:
    application_id: ${{ secrets.GH_ABCS_APP_ACTIONS_APP_ID }}
    application_private_key: "${{ secrets.GH_ABCS_APP_ACTIONS_APP_PRIVATE_KEY }}"
    permissions: "actions:write,contents:read,deployments:read"
```
> **Why a GitHub App?** The default `GITHUB_TOKEN` cannot approve deployments in the same repository where the workflow runs. This is a security restriction. A GitHub App token has a separate identity and can approve deployments.

**Step 2 - Review Deployments (lines 57-72):** Calls the GitHub API using [actions/github-script](https://github.com/actions/github-script):
```yaml
- name: Approve or Reject
  uses: actions/github-script@v7
  with:
    github-token: ${{ steps.get_workflow_token.outputs.token }}
    script: |
      github.rest.actions.reviewPendingDeploymentsForRun({
        owner: context.repo.owner,
        repo: context.repo.repo,
        run_id: ${{ github.event.inputs.run_id }},
        environment_ids: [${{ github.event.inputs.environment_ids }}],
        state: '${{ github.event.inputs.state }}',
        comment: '${{ github.event.inputs.comment }}'
      })
```
> **Key insight:** The `github-script` action provides `github.rest.*` methods that map directly to the [GitHub REST API](https://docs.github.com/en/rest). The method `reviewPendingDeploymentsForRun` corresponds to the [Review pending deployments](https://docs.github.com/en/rest/actions/workflow-runs#review-pending-deployments-for-a-workflow-run) endpoint.

### Try It Out

Now that you understand how the workflow works, test it:

1. **Modify the environments-secrets workflow for manual triggering:**
   - Open [environments-secrets.yml](/.github/workflows/environments-secrets.yml)
   - Find the `use-environment-uat` job (around line 80)
   - Comment out the `if` condition so it runs on manual trigger:
     ```yaml
     use-environment-uat:
       name: Use UAT environment
       runs-on: ubuntu-latest
       # if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
       needs: use-environment-test
     ```
   - Commit your change

2. **Create a pending deployment:**
   - Go to **Actions** > **03-1. Environments and Secrets**
   - Click **Run workflow** to trigger it manually
   - Wait for it to pause at UAT (requires approval if you configured it in section 3.1)

3. **Get the Run ID:**
   - Click on the running workflow in the Actions tab
   - Look at the URL: `https://github.com/owner/repo/actions/runs/123456789`
   - The Run ID is `123456789`

4. **Get the Environment ID:**
   - Go to **Settings** > **Environments** > click the environment waiting for approval
   - Look at the URL: `https://github.com/owner/repo/settings/environments/12345`
   - The Environment ID is `12345`

5. **Run the review workflow:**
   - Go to **Actions** > **03-3. Review Pending Deployments**
   - Click **Run workflow**
   - Fill in the values you collected above
   - Set **state** to `approved`
   - Add a **comment** like "Approved via API"

6. **Verify:**
   - Go back to the `environments-secrets.yml` workflow run
   - Confirm the pending deployment was approved and the workflow continued

### References

- [Review pending deployments API](https://docs.github.com/en/rest/actions/workflow-runs#review-pending-deployments-for-a-workflow-run)
- [Creating a GitHub App](https://docs.github.com/en/apps/creating-github-apps)
- [workflow-application-token-action](https://github.com/peter-murray/workflow-application-token-action)

## 3.4 Final
<details>
  <summary>environments-secrets.yml</summary>
  
```YAML
name: 03-1. Environments and Secrets

on:
  push:
     branches: [main]
  pull_request:
     branches: [main]
  workflow_dispatch:    
      
# Limit the permissions of the GITHUB_TOKEN
permissions:
  contents: read
  actions: read
  deployments: read

env:
  PROD_URL: 'https://github.com'
  DOCS_URL: 'https://docs.github.com'
  DEV_URL:  'https://docs.github.com/en/developers'

jobs:
  use-secrets:
    name: Use secrets
    runs-on: ubuntu-latest
    if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
    steps:
      - name: Hello world action with secrets
        uses: actions/hello-world-javascript-action@main
        with: # Set the secret as an input
          who-to-greet: ${{ secrets.MY_REPO_SECRET }}
        env: # Or as an environment variable
          super_secret: ${{ secrets.MY_REPO_SECRET }}
      - name: Echo secret is redacted in the logs
        run: |
          echo Env secret is ${{ secrets.MY_REPO_SECRET }}
          echo Warning: GitHub automatically redacts secrets printed to the log, 
          echo          but you should avoid printing secrets to the log intentionally.
          echo ${{ secrets.MY_REPO_SECRET }} | sed 's/./& /g'
    
  use-environment-dev:
    name: Use DEV environment
    runs-on: ubuntu-latest
    # Use conditionals to control whether the job is triggered or skipped
    # if: ${{ github.event_name == 'pull_request' }}
    
    # An environment can be specified per job
    # If the environment cannot be found, it will be created
    environment:
      name: DEV
      url: ${{ env.DEV_URL }}
    
    steps:
      - run: echo "Run id = ${{ github.run_id }}"

      - name: Checkout
        uses: actions/checkout@v4

      - name: Step that uses the DEV environment
        run: echo "Deployment to ${{ env.URL1 }}..."

      - name: Echo env secret is redacted in the logs
        run: |
          echo Env secret is ${{ secrets.MY_ENV_SECRET }}
          echo ${{ secrets.MY_ENV_SECRET }} | sed 's/./& /g'

  use-environment-test:
    name: Use TEST environment
    runs-on: ubuntu-latest
    #if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
    needs: use-environment-dev

    environment:
      name: TEST
      url: ${{ env.DOCS_URL }}
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Step that uses the TEST environment
        run: echo "Deployment to ${{ env.DOCS_URL }}..."
      
      # Secrets are redacted in the logs
      - name: Echo secrets are redacted in the logs
        run: |
          echo Repo secret is ${{ secrets.MY_REPO_SECRET }}
          echo Org secret is ${{ secrets.MY_ORG_SECRET }}
          echo Env secret is not accessible ${{ secrets.MY_ENV_SECRET }}

  use-environment-uat:
    name: Use UAT environment
    runs-on: ubuntu-latest
    if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
    needs: use-environment-test

    environment:
      name: UAT
      url: 'https://uat.github.com'
    
    steps:
      - name: Step that uses the UAT environment
        run: echo "Deployment to UAT..."
        env: 
          env_secret: ${{ secrets.MY_ENV_SECRET }}

  use-environment-prod:
    name: Use PROD environment
    runs-on: ubuntu-latest
    #if: ${{ github.event_name == 'push' && github.ref == 'refs/heads/main' }}
    
    needs: use-environment-uat

    environment:
      name: PROD
      url: ${{ env.PROD_URL }}
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Step that uses the PROD environment
        run: echo "Deployment to ${{ env.PROD_URL }}..."
```
</details>
