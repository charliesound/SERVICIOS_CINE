import os
import sys
import subprocess

def run_migration():
    print("Running database migrations...")
    try:
        # Assuming we are in /opt/SERVICIOS_CINE or similar
        # We use the relative path for alembic
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        print("Migration output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Migration failed with exit code {e.returncode}")
        print("Error output:")
        print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
