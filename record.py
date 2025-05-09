import traceback
import multiprocessing as mp

from transcribe import Recorder, config


def main():
    try:
        global config
        config = config._replace(
            segment_duration=86400,  # record one long session, 24h max
        )

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
