# 6 - Self-hosted runners
In this lab you will create and use your self-hosted runners.
> Duration: 10-15 minutes

References:
- [Adding self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/adding-self-hosted-runners)
- [Using self-hosted runners in a workflow](https://docs.github.com/en/actions/hosting-your-own-runners/using-self-hosted-runners-in-a-workflow)
- [Using labels with self-hosted runners](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/using-labels-with-self-hosted-runners)

## Understanding Self-Hosted Runner Labels

### Default Labels
When you register a self-hosted runner, GitHub automatically assigns these **default labels**:
- `self-hosted` - Identifies the runner as self-hosted (not GitHub-hosted)
- **Operating System**: `linux`, `windows`, or `macOS` - Based on the runner's OS
- **Architecture**: `x64`, `ARM`, or `ARM64` - Based on the runner's hardware

### Custom Labels
You can add **custom labels** during runner registration to further identify your runners. For example, `self-hosted-linux` or `gpu` are custom labels you define.

### How Label Matching Works
**Important:** When you specify multiple labels in `runs-on`, the runner must have **ALL** of them. Labels operate cumulatively (AND logic), not as options (OR logic).

For example:
```yaml
runs-on: [self-hosted, linux, x64, self-hosted-linux]
```
This means the job will **only** run on a runner that has **all four labels**:
- `self-hosted` ✓ (default)
- `linux` ✓ (default)
- `x64` ✓ (default)
- `self-hosted-linux` ✓ (**custom** - must be added during registration)

If your runner only has the three default labels, the job will **not** match and will remain queued.

## (Optional) 6.1 Add a self-hosted runner
> Prerequisites: Access to a Cloud platform to create a runner machine

1. If you have access to an Azure subscription, follow the guide to create a Linux virtual machine
    - [Create a Linux virtual machine](https://docs.microsoft.com/en-us/learn/modules/host-build-agent/4-create-build-agent)
2. Create a new private repository `my-private-repo`
    - [Creating a new repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository)
3. Follow the guide to install the agent on the runner
    - [Adding a self-hosted runner to a repository](https://docs.github.com/en/actions/hosting-your-own-runners/adding-self-hosted-runners#adding-a-self-hosted-runner-to-a-repository)
    - **Important:** During registration, add the custom label `self-hosted-linux` (for Linux) or `self-hosted-windows` (for Windows) so your runner matches the workflow's `runs-on` requirements. You can add labels using the `--labels` flag:
      ```bash
      ./config.sh --url <REPO_URL> --token <TOKEN> --labels self-hosted-linux
      ```
4. Follow the guide to use the self-hosted runner in a workflow
    - [Using self-hosted runners in a workflow](https://docs.github.com/en/actions/hosting-your-own-runners/using-self-hosted-runners-in-a-workflow)
5. Create a new workflow `.github/workflows/self-hosted-runners.yml` in your private repository and run the workflow on the self-hosted runner

    > **Note on `runs-on` labels:** The workflow below uses `runs-on: [self-hosted, linux, x64, self-hosted-linux]`. This requires the runner to have **all four labels**:
    > - `self-hosted`, `linux`, `x64` — Default labels (assigned automatically)
    > - `self-hosted-linux` — Custom label (you must add this during runner registration)

```YAML
name: Self-Hosted Runners Hello

on:
  workflow_dispatch:
    inputs:
      name:
        description: 'What is your name?'
        required: true
        default: 'World'
        
jobs:
  say_hello_linux:
    name: Say Hello from Linux Self-Hosted Runner
    runs-on: [self-hosted, linux, x64, self-hosted-linux]
    steps:
      - name: Say hello from self-hosted linux runner
        run: |
          echo "Hello ${{ github.event.inputs.name }}, from self-hosted linux runner!"

  say_hello_windows:
    name: Say Hello from Windows Self-Hosted Runner
    runs-on: [self-hosted, windows, x64, self-hosted-windows]
    needs: say_hello_linux
    steps:
      - name: Say hello from self-hosted windows runner
        run: |
          echo "Hello ${{ github.event.inputs.name }}, from self-hosted windows runner!"
```
6. Clean up your runner resources if not needed