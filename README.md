# Coffee Shop A2A Agent & MCP Server Setup

This guide will help you set up your environment, deploy the MCP server, and deploy the A2A server for the Coffee Shop agent project.

---

## 1. Setup Environment

1. **Activate Python Virtual Environment**
   - If you don't have a virtual environment, create one:
     ```sh
     python -m venv venv
     ```
   - Activate it:
     - On Windows:
       ```sh
       .\venv\Scripts\activate
       ```
     - On macOS/Linux:
       ```sh
       source venv/bin/activate
       ```

2. **Install gcloud CLI**
   ```sh
   pip3 install gcloud
   ```

3. **Set the Google Cloud project**
   ```sh
   gcloud config set project PROJECT_NAME
   ```
   Replace `PROJECT_NAME` with your actual Google Cloud project ID.

4. **Set up Application Default Credentials**
   ```sh
   gcloud auth application-default login
   ```

5. **Get your Google API key**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey) and generate an API key.

---

## 2. Setup MCP Server

1. Change directory to the MCP server folder:
   ```sh
   cd MCP_server
   ```

2. Deploy the MCP server to Google Cloud Run:
   ```sh
   gcloud run deploy coffee-shop-mcp --source . --region us-central1 --platform managed --allow-unauthenticated
   ```

3. After deployment, copy the server URL (e.g., `https://your-mcp-url.run.app/mcp-server/mcp`).

---

## 3. Setup A2A Server

1. Ensure you have added your Google API key in `agent.py`.
2. Paste your MCP server URL in `agent.py` as well.
3. In the root project directory, deploy the A2A server:
   ```sh
   gcloud run deploy coffee-shop-a2a-server --source . --region us-central1 --platform managed --allow-unauthenticated
   ```

---

**Note:**
- Make sure all environment variables and credentials are set correctly before deploying.
- Please note that this setup should only be used for demo / testing purposes. Please keep a tab on your Google Cloud Billing budget. 
- For any issues, refer to the official Google Cloud documentation or your project maintainer.
