import os
import shutil

class CloneTool:
    @staticmethod
    def hash_file(filepath: str, chunk_size: int = 8192) -> str:
        """Generates blazing fast XXHASH64 checksum for terabytes of media."""
        # Fallback to standard hashlib if xxhash is not available
        try:
            import xxhash
            hasher = xxhash.xxh64()
        except ImportError:
            import hashlib
            hasher = hashlib.sha256()

        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(chunk_size), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    @classmethod
    def secure_copy(cls, src: str, dest: str) -> bool:
        """Copies file and verifies cryptographic integrity."""
        if not os.path.exists(src):
            raise FileNotFoundError(f"Source file not found: {src}")
            
        src_hash = cls.hash_file(src)
        
        # Ensure destination directory exists
        dest_dir = os.path.dirname(dest)
        if dest_dir:
            os.makedirs(dest_dir, exist_ok=True)
            
        shutil.copy2(src, dest)
        dest_hash = cls.hash_file(dest)
        
        if src_hash != dest_hash:
            os.remove(dest)
            raise IOError(f"Checksum mismatch! {src} failed to clone safely to {dest}.")
        return True
