import traceback
from pyscribe import Recorder, Transcriber

if __name__ == "__main__":
    try:
        Recorder().run()
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        exit(1)

    try:
        Transcriber().run()
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        exit(1)
