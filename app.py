from utils.jsrunner import NodeJsEntrypoint

# entrypoint for the n8n docker container
if __name__ == "__main__":
    entrypoint = NodeJsEntrypoint()
    entrypoint.with_command("npx n8n").run()