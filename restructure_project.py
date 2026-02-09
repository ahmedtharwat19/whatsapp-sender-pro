import os
import shutil

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SRC_OLD = os.path.join(BASE_DIR, "src")
SRC_NEW = os.path.join(BASE_DIR, "src", "whatsapp_sender")

STRUCTURE = {
    "app.py": "main.py",

    "config": {
        "settings.py": "config/settings.py",
        "license_manager.py": "config/license_manager.py",
        "encryption.py": "config/encryption.py",
    },

    "licensing": {
        "license_manager.py": "config/license_manager.py",
        "license_generator.py": "developer/license_generator.py",
        "encryption.py": "config/encryption.py",
    },

    "ui": {
        "main_window.py": "ui/main_window.py",
        "dialogs.py": "ui/dialogs.py",
        "components.py": "ui/components.py",
        "styles.py": "ui/styles.py",
    },

    "core": {
        "whatsapp_client.py": "core/whatsapp.py",
        "sender.py": "core/sender.py",
        "contact_manager.py": "core/contact_manager.py",
        "image_processor.py": "core/image_processor.py",
    },

    "utils": {
        "logger.py": "utils/logger.py",
        "helpers.py": "utils/helpers.py",
        "translator_service.py": "utils/translator.py",
    },
}


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def move_file(src_relative, dst_relative):
    src = os.path.join(SRC_OLD, src_relative)
    dst = os.path.join(SRC_NEW, dst_relative)

    if not os.path.exists(src):
        print(f"⚠️  ملف غير موجود: {src_relative}")
        return

    ensure_dir(os.path.dirname(dst))
    shutil.move(src, dst)
    print(f"✅ moved: {src_relative} → {dst_relative}")


def main():
    print("🚀 Starting project restructuring...\n")

    ensure_dir(SRC_NEW)

    # نقل main.py → app.py
    move_file("main.py", "app.py")

    for group, files in STRUCTURE.items():
        if isinstance(files, dict):
            for new_name, old_path in files.items():
                move_file(old_path, f"{group}/{new_name}")

    print("\n🎉 Done! Project restructured successfully.")


if __name__ == "__main__":
    main()
