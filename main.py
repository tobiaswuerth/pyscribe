import multiprocessing as mp
import traceback

from transcribe import Recorder


def main():
    on_exit = mp.Event()

    recorder = Recorder(on_exit)
    recorder.initialize()
    recorder.start()

    try:
        while not on_exit.is_set():
            print("Recorder is running...")
            on_exit.wait(1)
    except KeyboardInterrupt:
        recorder.join()
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        on_exit.set()


if __name__ == "__main__":
    main()
