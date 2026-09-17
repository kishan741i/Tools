import os
import re
import time
import sys
import datetime

def normalize_path(path):
    r"""Path ke backslashes ko forward slashes me convert karta hai"""
    return os.path.abspath(path).replace('\\', '/')

def format_display_name(name, max_len=32):
    """Agar filename lamba hai toh limit karke last me '...' laga deta hai"""
    if len(name) > max_len:
        return name[:max_len - 3] + "..."
    return name.ljust(max_len)

def format_eta(seconds):
    if seconds < 0 or seconds == float('inf'):
        return "Calculating..."
    mins, secs = divmod(int(seconds), 60)
    if mins > 0:
        return f"{mins}m {secs}s"
    return f"{secs}s"

def get_braille_progress_bar(percent, width=12):
    filled_len = int(width * percent / 100)
    empty_len = width - filled_len
    bar = "⣿" * filled_len + "⣀" * empty_len
    return f"[{bar}]"

def bulk_file_renamer():
    print("=== 🚀 Ultimate Master Python Bulk File Renamer ===")
    
    # 1. Folder Path
    folder_path = input("👉 Enter folder path: ").strip()
    if not os.path.exists(folder_path):
        print("❌ Error: Yeh folder exist nahi karta!")
        return
        
    # --- RECURSIVE SUBFOLDER SCANNING TOGGLE ---
    sub_choice = input("👉 Kya subfolders ke andar ki files ko bhi rename karna hai? [y/n]: ").strip().lower()
    recursive = (sub_choice == 'y')
        
    # --- OPTIONAL EXTENSION FILTER ---
    ext_input = input("👉 Enter file extension to filter (e.g., .jpg, .mp4) OR press Enter for ALL: ").strip().lower()
    target_ext = ext_input if ext_input else None
    if target_ext and not target_ext.startswith('.'):
        target_ext = '.' + target_ext

    # 2. Categorized Renaming Modes Menu
    print("\nSelect Completely Renaming Mode:")
    print("  [1] Prefix + Counter (e.g., photo_01.jpg, photo_02.jpg)")
    print("  [2] Find & Replace Text (e.g., replace 'IMG' with 'Vacation')")
    print("-" * 75)
    print("Select Existing Name Modification Mode:")
    print("  [3] Case Conversion (Lower / Upper / Title Case)")
    print("  [4] Clean Special Characters & Spaces (Completely Remove Spaces, Emojis & Symbols)")
    
    mode_choice = input("👉 Choose mode (1-4): ").strip()
    
    renames = [] # List to store (old_path, new_path, old_name, new_name)
    
    try:
        # File gathering logic
        all_files = []
        if recursive:
            for root, dirs, files in os.walk(folder_path):
                for f in files:
                    full_p = os.path.join(root, f)
                    if target_ext and not f.lower().endswith(target_ext):
                        continue
                    all_files.append(full_p)
        else:
            for f in os.listdir(folder_path):
                full_p = os.path.join(folder_path, f)
                if os.path.isfile(full_p):
                    if target_ext and not f.lower().endswith(target_ext):
                        continue
                    all_files.append(full_p)
        
        if not all_files:
            print("\n[!] Is path par koi bhi file nahi mili.")
            return

        # --- MODE 1: PREFIX + COUNTER ---
        if mode_choice == '1':
            prefix = input("👉 Enter new base name/prefix (e.g., 'photo'): ").strip()
            
            print("\nSelect Sorting Order:")
            print("  [1] Alphabetical (A to Z)")
            print("  [2] Oldest First (Purani files pehle)")
            print("  [3] Newest First (Nayi files pehle)")
            sort_choice = input("👉 Choose sorting method (1, 2, or 3): ").strip()
            
            if sort_choice == '2':
                all_files.sort(key=lambda x: os.path.getmtime(x))
            elif sort_choice == '3':
                all_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            else:
                all_files.sort(key=lambda x: os.path.basename(x).lower())
                
            total_files_count = len(all_files)
            padding_width = max(len(str(total_files_count)), 2)

            count = 1
            for old_path in all_files:
                directory = os.path.dirname(old_path)
                filename = os.path.basename(old_path)
                ext = os.path.splitext(filename)[1]
                
                padded_counter = str(count).zfill(padding_width)
                new_name = f"{prefix}_{padded_counter}{ext}"
                new_path = os.path.join(directory, new_name)
                
                if old_path != new_path:
                    renames.append((old_path, new_path, filename, new_name))
                count += 1
                    
        # --- MODE 2: FIND & REPLACE ---
        elif mode_choice == '2':
            target_str = input("👉 Text to find: ").strip()
            replace_str = input("👉 Text to replace with: ").strip()
            for old_path in all_files:
                directory = os.path.dirname(old_path)
                filename = os.path.basename(old_path)
                if target_str in filename:
                    new_name = filename.replace(target_str, replace_str)
                    new_path = os.path.join(directory, new_name)
                    if old_path != new_path:
                        renames.append((old_path, new_path, filename, new_name))
                        
        # --- MODE 3: CASE CONVERSION ---
        elif mode_choice == '3':
            print("\nSelect Case Type:")
            print("  [1] lowercase (e.g., my_photo.jpg)")
            print("  [2] UPPERCASE (e.g., MY_PHOTO.JPG)")
            print("  [3] Title Case (e.g., My_Photo.jpg)")
            case_opt = input("👉 Choose case option (1, 2, or 3): ").strip()
            
            for old_path in all_files:
                directory = os.path.dirname(old_path)
                filename = os.path.basename(old_path)
                name_part, ext = os.path.splitext(filename)
                
                if case_opt == '1':
                    new_name = name_part.lower() + ext.lower()
                elif case_opt == '2':
                    new_name = name_part.upper() + ext.upper()
                elif case_opt == '3':
                    new_name = name_part.title() + ext.lower()
                else:
                    continue
                    
                new_path = os.path.join(directory, new_name)
                if old_path != new_path:
                    renames.append((old_path, new_path, filename, new_name))
                    
        # --- MODE 4: REMOVE SPACES, EMOJIS & SYMBOLS COMPLETELY ---
        elif mode_choice == '4':
            for old_path in all_files:
                directory = os.path.dirname(old_path)
                filename = os.path.basename(old_path)
                name_part, ext = os.path.splitext(filename)
                
                cleaned_name = re.sub(r'[^\w\-]', '', name_part)
                new_name = cleaned_name + ext.lower()
                
                new_path = os.path.join(directory, new_name)
                if old_path != new_path:
                    renames.append((old_path, new_path, filename, new_name))
        else:
            print("❌ Invalid mode selected!")
            return

        if not renames:
            print("\n[!] Koi bhi file match nahi hui rename karne ke liye.")
            return

        # --- PREVIEW / DRY RUN (ALIGNED) ---
        print(f"\n--- 📋 Preview ({len(renames)} files will be renamed) ---")
        for _, _, old_n, new_n in renames[:10]:
            formatted_old = format_display_name(old_n, max_len=32)
            formatted_new = format_display_name(new_n, max_len=32)
            print(f"  {formatted_old} ➡️  {formatted_new}")
            
        if len(renames) > 10:
            print(f"  ... aur baaki ki {len(renames) - 10} files.")
            
        # --- CONFIRMATION & LIVE PROGRESS EXECUTION ---
        confirm = input("\n👉 Kya aap yeh changes apply karna chahte hain? [y/n]: ").strip().lower()
        if confirm == 'y':
            print("\n[⚡] Renaming files...")
            success_count = 0
            total_renames = len(renames)
            start_time = time.time()
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            log_filename = os.path.join(folder_path, f"rename_undo_log_{timestamp}.txt")
            
            with open(log_filename, 'w', encoding='utf-8') as log_file:
                log_file.write("OLD_PATH | NEW_PATH\n")
                
                for idx, (old_p, new_p, old_n, new_n) in enumerate(renames, 1):
                    try:
                        os.rename(old_p, new_p)
                        normalize_old = normalize_path(old_p)
                        normalize_new = normalize_path(new_p)
                        log_file.write(f"{normalize_old} -> {normalize_new}\n")
                        success_count += 1
                    except Exception as e:
                        pass

                    # --- LIVE PROGRESS BAR UPDATE ---
                    now = time.time()
                    elapsed = now - start_time
                    speed = idx / elapsed if elapsed > 0 else 1
                    eta = (total_renames - idx) / speed if speed > 0 else 0
                    percent = (idx / total_renames) * 100

                    prog_bar = get_braille_progress_bar(percent, width=12)
                    short_name = old_n
                    if len(short_name) > 20:
                        short_name = short_name[:17] + "..."

                    sys.stdout.write(f"\r🚀 {prog_bar} {percent:3.0f}% | {idx}/{total_renames} | ETA: {format_eta(eta)} | [{short_name}]   ")
                    sys.stdout.flush()

            print("\n")
            print(f"🎉 Success! Total {success_count} files successfully rename ho chuki hain.")
            print(f"📄 Undo Log saved at: {normalize_path(log_filename)}")
        else:
            print("\n[ℹ] Operation cancel kar diya gaya. Files safe hain.")

    except Exception as e:
        print(f"❌ Error aa gaya: {e}")

if __name__ == "__main__":
    bulk_file_renamer()
    input("\nPress Enter to exit...")