# This file is no longer needed for show_message as it's not thread-safe.
# You can keep it if you plan to add other utility functions,
# or you can safely delete it.

# The original show_message function is removed because creating a new
# tk.Tk() instance inside a function, especially when called from threads,
# is a bad practice and can lead to instability and crashes.
# The message box logic has been moved into the main App class
# and is called safely via the UI queue.


