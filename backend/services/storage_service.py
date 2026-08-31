import shutil
from pathlib import Path
from fastapi import UploadFile
from backend.config import STORAGE_DIR

class StorageService:
    @staticmethod
    def save_file(upload_file: UploadFile, filename: str) -> str:
        """Saves an uploaded file to the configured local storage directory and returns the absolute path."""
        target_path = STORAGE_DIR / filename
        
        # Ensure target path doesn't escape STORAGE_DIR
        resolved_path = target_path.resolve()
        if not str(resolved_path).startswith(str(STORAGE_DIR.resolve())):
            raise ValueError("Invalid file path attempted")
            
        with target_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
        return str(target_path)
    
    @staticmethod
    def get_file_path(filename: str) -> Path:
        """Gets the Path object for a stored file, checking that it exists within the storage directory."""
        target_path = (STORAGE_DIR / filename).resolve()
        if not str(target_path).startswith(str(STORAGE_DIR.resolve())):
            raise ValueError("Access denied: File path out of storage directory")
        return target_path
