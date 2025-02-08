# 🧱 databricks-n8n

Self-host [n8n](https://n8n.io/) as a [Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)!

## 🗂️ Directory Structure

The basic Databricks Apps directory structure:

```
.
├── README.md
├── app.py
├── app.yaml
└── utils
    ├── __init__.py
    └── jsrunner.py
```

- `app.py`: Your main app logic.
- `app.yaml` (optional): Your app configurations. Contains the entrypoint command (e.g. `python app.py`) and any environmental variables. This is where you define the application port as 8000 (required by Databricks Apps). 
- `requirements.txt` (optional): Dependencies required for the project.
- `utils/`: Utility functions for initializing NodeJS in Python.

## ⚙️ Installation

To install and deploy this app in Databricks Apps, clone the repository to your computer and either manually upload these files to your Databricks workspace, or sync the files to your Databricks workspace via Databricks SDK, i.e.,

`databricks sync --watch . /Workspace/Users/path/to/databricks_n8n`

To deploy the app in your Databricks Workspace, go to Compute > Apps > Create app > Custom. 

Enter your app name and optional description. Skip app resources, and create app. First deployment will take ~5 minutes to get container, and upload and install app. Subsequent redeployment only takes less than 10s.

Once the app is running, you can click the app URL to use it. 

Click on the "Logs" tab to view app logs.

## 👷‍♂️ Usage

To make Databricks services accessible in n8n, first set up Databricks credentials in n8n using your personal access tokens (PAT).

Then you can use n8n's [HTTP node](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/) and reference [Databricks REST API docs](https://docs.databricks.com/api/workspace/introduction) To access Databricks workspace services (e.g. Workflows, Compute, ML, Model Serving, Vector Search, etc.).

For inspiration on what workflows you can create, see [n8n workflow automation templates](https://n8n.io/workflows/).

## 🗒️ Note

By default, n8n uses SQLite to save credentials, past executions, and workflows. n8n also supports PostgresDB, which you can set in app.yaml using the environment variable `DB_TYPE`. See [n8n docs](https://docs.n8n.io/hosting/configuration/supported-databases-settings/) for details.

__WARNING__: If you choose to use n8n's default SQLite database, then all your workflows and credentials will be removed when you delete the app. So you should use an external transactional database to persist app history.
