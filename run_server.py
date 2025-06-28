import uvicorn
from dotenv import load_dotenv
import os
import sys

# Add the 'backend' directory to the Python path
# This ensures that modules inside 'backend' can be found
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

if __name__ == "__main__":
    # Load environment variables from the .env file in the backend directory
    dotenv_path = os.path.join(backend_path, '.env')
    load_dotenv(dotenv_path=dotenv_path)
    
    # Now that environment variables are loaded, run the uvicorn server
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True) 