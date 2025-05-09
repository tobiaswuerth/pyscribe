import traceback

from pyscribe import Transcriber


def main():
    try:
        transcriber = Transcriber(None)
        todo = transcriber.get_files_todo()
        if not todo:
            print("No files to transcribe.")
            return

        transcriber.initialize()
        for filename in todo:
            print(f"Processing file: {filename} ...")
            transcriber.process_audio_file(filename)

        print("All files processed.")
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
