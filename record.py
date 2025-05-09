import traceback
import multiprocessing as mp

from pyscribe import Recorder


def main():
    try:
        recorder = Recorder(mp.Event())
        recorder.initialize()

        print("Recording...")
        recorder.run()
        print("Recording finished.")
    except KeyboardInterrupt:
        print("Interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
