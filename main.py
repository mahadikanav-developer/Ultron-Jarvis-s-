from core.runtime import UltronRuntime
from voice.voice import shutdown, startup


def main():

    print("================================")
    print("        ULTRON v0.7")
    print("================================")

    startup()

    print("Type 'exit' to shut down.")
    print()

    runtime = UltronRuntime()

    try:

        while True:
            try:

                user_input = input("You > ").strip()

                if user_input.lower() == "exit":
                    shutdown()
                    break

                if not user_input:
                    continue

                result = runtime.process_turn(user_input)
                analysis = result.get("analysis") or {}

                print()
                print("[CORE 1]")
                print("Intent:", analysis.get("intent"))
                print("Complexity:", analysis.get("complexity"))
                print("Response mode:", analysis.get("response_mode"))
                print("Route:", analysis.get("route"))

                print("\n[ULTRON]")
                print(result.get("answer"))
                print()

            except Exception as error:
                print(f"\n[SYSTEM ERROR] An internal fault occurred: {error}")
                print(
                    "[ULTRON]\n"
                    "I encountered a processing error, but my core loop remains stable. "
                    "Please try your request again.\n"
                )

    except (KeyboardInterrupt, EOFError):
        shutdown()
        print("\nShutdown signal received. Exiting.")


if __name__ == "__main__":
    main()
