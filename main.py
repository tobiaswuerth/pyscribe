import multiprocessing as mp
import traceback

from pyscribe import Recorder, Transcriber


def main():
    try:
        on_exit = mp.Event()

        recorder = Recorder(on_exit)
        recorder.initialize()
        recorder.start()

        transcriber = Transcriber(on_exit)
        transcriber.start()

        while not on_exit.is_set():
            on_exit.wait(1)
    except KeyboardInterrupt:
        recorder.join()
        transcriber.join()
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        on_exit.set()


if __name__ == "__main__":
    print("Started main process")
    main()
    print("Exiting main process")
