import subprocess
import os
import sys

def run_command(command):
    print(f"Executing: {command}")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        env=env
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True

def main():
    print("Starting Multi-Tenant Migration Generation...")
    
    # 1. Autogenerate revision
    msg = "add_organization_id_to_delivery_and_review"
    command = f"alembic revision --autogenerate -m \"{msg}\""
    
    if run_command(command):
        print("Migration generated successfully.")
        # 2. Run upgrade to apply to local db for verification
        print("Applying migration to local database...")
        if run_command("alembic upgrade head"):
            print("Migration applied successfully.")
        else:
            print("Failed to apply migration.")
    else:
        print("Failed to generate migration.")

if __name__ == "__main__":
    main()
