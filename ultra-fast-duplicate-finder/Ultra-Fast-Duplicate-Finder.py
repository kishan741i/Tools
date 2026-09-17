import os
import hashlib
import time
import sys
from collections import defaultdict

def format_eta(seconds):
    if seconds < 0 or seconds == float('inf'):
        return "Calculating..."
    mins, secs = divmod(int(seconds), 60)
    if mins > 0:
        return f"{mins}m {secs}s"
    return f"{secs}s"

def format_size(size_bytes):
    """Bytes ko readable format (KB, MB, GB) me convert karta hai"""
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {size_name[i]}"

def get_braille_progress_bar(percent, width=15):
    filled_len = int(width * percent / 100)
    empty_len = width - filled_len
    bar = "⣿" * filled_len + "⣀" * empty_len
    return f"[{bar}]"

def normalize_path(path):
    r"""Path ke saare backslashes (\) ko forward slashes (/) me convert karta hai"""
    return os.path.abspath(path).replace('\\', '/')

def get_file_hash(filepath):
    hasher = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def find_duplicates_fast(root_dir, target_ext=None):
    print(f"\n[⚡] Step 1: Scanning folder & grouping by file size...")
    
    size_map = defaultdict(list)
    total_files = 0
    
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            # Extension filter check (agar user ne diya ho)
            if target_ext and not file.lower().endswith(target_ext):
                continue
                
            filepath = os.path.join(root, file)
            if not os.path.islink(filepath):
                try:
                    f_size = os.path.getsize(filepath)
                    
                    # 0-Byte (Empty) files ko ignore karne ka check
                    if f_size > 0:
                        size_map[f_size].append(filepath)
                        total_files += 1
                except Exception:
                    pass

    potential_duplicates = []
    for size, paths in size_map.items():
        if len(paths) > 1:
            for p in paths:
                potential_duplicates.append(p)

    candidates_count = len(potential_duplicates)
    print(f"[+] Total files scanned : {total_files}")
    print(f"[+] Potential duplicates: {candidates_count} files. Scanning hashes...\n")

    if candidates_count == 0:
        return {}

    file_hashes = defaultdict(list)
    start_time = time.time()

    for idx, filepath in enumerate(potential_duplicates, 1):
        file_hash = get_file_hash(filepath)
        if file_hash:
            file_hashes[file_hash].append(filepath)

        now = time.time()
        elapsed = now - start_time
        speed = idx / elapsed if elapsed > 0 else 1
        eta = (candidates_count - idx) / speed if speed > 0 else 0
        percent = (idx / candidates_count) * 100

        prog_bar = get_braille_progress_bar(percent, width=12)
        short_name = os.path.basename(filepath)
        if len(short_name) > 20:
            short_name = short_name[:17] + "..."

        sys.stdout.write(f"\r🚀 {prog_bar} {percent:3.0f}% | {idx}/{candidates_count} | ETA: {format_eta(eta)} | [{short_name}]   ")
        sys.stdout.flush()

    print("\n")
    
    duplicate_groups = {}
    for h, paths in file_hashes.items():
        if len(paths) > 1:
            try:
                # 🕒 Oldest file ko pehle sort karo taaki wo Original bane
                paths.sort(key=lambda x: os.path.getmtime(x))
            except Exception:
                pass
            duplicate_groups[h] = paths

    return duplicate_groups

if __name__ == "__main__":
    target_path = input("👉 Enter folder or drive path to scan (e.g., D:/ or /sdcard): ").strip()
    
    # Optional Extension Input
    ext_input = input("👉 Enter file extension to filter (e.g., .mp3, .png) OR press Enter to scan ALL files: ").strip().lower()
    target_ext = ext_input if ext_input else None
    if target_ext and not target_ext.startswith('.'):
        target_ext = '.' + target_ext

    if os.path.exists(target_path):
        dup_groups = find_duplicates_fast(target_path, target_ext)
        
        if dup_groups:
            print(f"\n[!] Total Duplicate Groups Found: {len(dup_groups)}\n")
            print("=" * 70)
            
            all_duplicates_to_delete = []
            total_bytes_to_free = 0
            
            for idx, (f_hash, paths) in enumerate(dup_groups.items(), 1):
                original = normalize_path(paths[0])
                duplicates = [normalize_path(p) for p in paths[1:]]
                
                print(f"[{idx}] Group Match:")
                print(f"   📁 Original  : {original}")
                for dup in duplicates:
                    print(f"   🗑️ Duplicate : {dup}")
                    all_duplicates_to_delete.append(dup)
                    try:
                        total_bytes_to_free += os.path.getsize(dup)
                    except Exception:
                        pass
                print("-" * 70)
            
            # --- STORAGE SAVED COUNTER ---
            formatted_space = format_size(total_bytes_to_free)
            print(f"\n💾 Total Space to be Freed: {formatted_space}")

            # --- AUTO-CLEANUP OPTION ---
            choice = input("👉 Kya aap saare duplicate files ko automatically delete karna chahte hain? [y/n]: ").strip().lower()
            if choice == 'y':
                deleted_count = 0
                for dup_path in all_duplicates_to_delete:
                    try:
                        os.remove(dup_path)
                        print(f"[✔] Deleted: {dup_path}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"[❌] Error deleting {dup_path}: {e}")
                print(f"\n🎉 Success! Total {deleted_count} duplicate files delete kar di gayi hain aur {formatted_space} space free ho chuki hai.")
            else:
                print("\n[ℹ] Koi file delete nahi ki gayi. Aapka data safe hai.")
                
        else:
            print("\n[✔] Badhai ho! Aapke diye gaye path par koi duplicate file nahi mili.")
    else:
        print("❌ Error: Invalid path entered!")
        
    input("\nPress Enter to exit...")