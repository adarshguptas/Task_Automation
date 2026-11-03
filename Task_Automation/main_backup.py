import os
import shutil


SOURCE_FOLDER = "source_images"
DESTINATION_FOLDER = "destination_images"


def move_image_files():

    os.makedirs(DESTINATION_FOLDER, exist_ok=True)

    moved_count = 0

    for file_name in os.listdir(SOURCE_FOLDER):

        if file_name.lower().endswith((".jpg", ".jpeg", ".png")):

            source_path = os.path.join(SOURCE_FOLDER, file_name)
            destination_path = os.path.join(
                DESTINATION_FOLDER,
                file_name
            )

            shutil.move(source_path, destination_path)

            print(f"Moved: {file_name}")

            moved_count += 1

    print()
    print("--------------------------------")
    print(f"Total image files moved: {moved_count}")
    print("--------------------------------")


if __name__ == "__main__":
    move_image_files()