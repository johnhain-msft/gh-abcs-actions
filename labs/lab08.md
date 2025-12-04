# 8 - AI Inference with GitHub Actions
In this lab you will use AI inference capabilities within GitHub Actions workflows.
> Duration: 15-20 minutes

References:
- [GitHub Actions AI Inference Action](https://github.com/actions/ai-inference)
- [GitHub Models Documentation](https://docs.github.com/en/github-models)
- [Using GitHub Models in GitHub Actions](https://docs.github.com/en/github-models/use-github-models-in-github-actions)

## 8.1 Add AI Inference to a Workflow

In this section, you'll update a workflow to use AI inference and generate responses using GitHub Models.

### Understanding the `models: read` Permission

GitHub Actions requires explicit permission to access GitHub Models. The `models: read` permission grants your workflow read-only access to AI models, enabling it to send prompts and receive responses. Without this permission, the workflow will fail with a permissions error.

### Understanding the Starter Workflow

1. Open the workflow file [ai-inference.yml](/.github/workflows/ai-inference.yml)
2. Review the existing structure:
```YAML
name: 08-1. AI Inference

on:
  workflow_dispatch:

permissions:
  models: read

jobs:
  inference:
    name: AI Inference
    runs-on: ubuntu-latest
    steps:
      # Add AI inference steps here
```

> **Note:** The workflow already has the `models: read` permission configured and a `workflow_dispatch` trigger for manual execution. You'll add the AI inference steps.

### Add the AI Inference Step

3. Edit the file and replace the comment `# Add AI inference steps here` with the following YAML content:
```YAML
      - name: Run AI Inference
        id: ai
        uses: actions/ai-inference@v1
        with:
          prompt: "Explain what GitHub Actions is in 2 sentences."
          max-tokens: 150

      - name: Display Response
        run: echo "${{ steps.ai.outputs.response }}"
```

> **Note:** The `actions/ai-inference@v1` action accepts these key inputs:
> - `prompt`: The text prompt to send to the AI model
> - `model`: The model to use (defaults to `openai/gpt-4o`)
> - `max-tokens`: Maximum tokens in the response (controls response length)

> **Note:** The AI response is available in `steps.ai.outputs.response` where `ai` is the `id` we assigned to the inference step.

### Run the Workflow

4. Commit the changes into the `main` branch
5. Go to the `Actions` tab in your repository
6. Select the `08-1. AI Inference` workflow from the left sidebar
7. Click `Run workflow` → select the `main` branch → click `Run workflow`
8. Once the workflow completes, click into the run and expand the `Display Response` step to see the AI-generated explanation of GitHub Actions

## 8.2 Final

> **Note:** Section 8.2 will be completed in a future story with the full solution.

<details>
  <summary>ai-inference.yml</summary>

```YAML
name: 08-1. AI Inference

on:
  workflow_dispatch:

permissions:
  models: read

jobs:
  inference:
    name: AI Inference
    runs-on: ubuntu-latest
    steps:
      - name: Run AI Inference
        id: ai
        uses: actions/ai-inference@v1
        with:
          prompt: "Explain what GitHub Actions is in 2 sentences."
          max-tokens: 150

      - name: Display Response
        run: echo "${{ steps.ai.outputs.response }}"
```
</details>
