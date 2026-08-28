import tkinter as tk
from tkinter import scrolledtext

from core.runtime import UltronRuntime


class UltronInterface:

    def __init__(self, root):
        self.root = root
        self.runtime = UltronRuntime()

        root.title("ULTRON")
        root.geometry("900x650")
        root.minsize(700, 500)

        # ============================================================
        # HEADER
        # ============================================================

        header = tk.Frame(root)
        header.pack(fill="x", padx=15, pady=10)

        title = tk.Label(
            header,
            text="ULTRON",
            font=("Segoe UI", 22, "bold")
        )
        title.pack(side="left")

        status = tk.Label(
            header,
            text="ONLINE",
            font=("Segoe UI", 11)
        )
        status.pack(side="right")

        # ============================================================
        # CHAT AREA
        # ============================================================

        self.chat = scrolledtext.ScrolledText(
            root,
            wrap=tk.WORD,
            font=("Segoe UI", 12),
            state="disabled"
        )

        self.chat.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        self.add_message(
            "ULTRON",
            "Hello. I am ready."
        )

        # ============================================================
        # INPUT AREA
        # ============================================================

        input_frame = tk.Frame(root)
        input_frame.pack(
            fill="x",
            padx=15,
            pady=15
        )

        self.entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 13)
        )

        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=8
        )

        self.entry.bind(
            "<Return>",
            self.send_message
        )

        send_button = tk.Button(
            input_frame,
            text="Send",
            font=("Segoe UI", 11, "bold"),
            command=self.send_message
        )

        send_button.pack(
            side="right",
            padx=(10, 0),
            ipadx=15,
            ipady=5
        )

        self.entry.focus()

    # ================================================================
    # CHAT
    # ================================================================

    def add_message(self, sender, message):

        self.chat.config(state="normal")

        self.chat.insert(
            tk.END,
            f"{sender}: {message}\n\n"
        )

        self.chat.config(state="disabled")
        self.chat.see(tk.END)

    # ================================================================
    # SEND
    # ================================================================

    def send_message(self, event=None):

        user_input = self.entry.get().strip()

        if not user_input:
            return

        self.entry.delete(0, tk.END)

        self.add_message(
            "YOU",
            user_input
        )

        try:
            result = self.runtime.process_turn(user_input)
            answer = result.get("answer", "I could not produce a response.")
        except Exception as error:
            answer = (
                "I encountered a processing error, but my core loop remains stable. "
                f"Details: {error}"
            )

        self.add_message("ULTRON", answer)


# ====================================================================
# START UI
# ====================================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = UltronInterface(root)

    root.mainloop()
