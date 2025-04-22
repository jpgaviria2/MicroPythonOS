import _thread
import time

# Global flag to signal thread termination
terminate_threads = False

# Function to be run by each thread
def thread_func(thread_id):
    global terminate_threads
    while not terminate_threads:
        time.sleep_ms(10)  # Minimal work to keep thread alive

# Test function for a given stack size
def test_threads(stack_size):
    global terminate_threads
    print(f"\nTesting with stack size: {stack_size} bytes")
    
    # Set stack size for new threads
    try:
        _thread.stack_size(stack_size)
    except AttributeError as e:
        print(f"Error setting stack size: {e}")
        return 0
    
    # Reset termination flag
    terminate_threads = False
    
    threads = []
    thread_count = 0
    
    try:
        while True:
            # Start a new thread
            thread_id = _thread.start_new_thread(thread_func, (thread_count,))
            threads.append(thread_id)
            thread_count += 1
            print(f"Started thread {thread_count}", end="\r")
            time.sleep_ms(10)  # Small delay to allow thread to start
    except Exception as e:
        print(f"\nException after {thread_count} threads: {e}")
    
    # Signal all threads to terminate
    terminate_threads = True
    
    # Wait for threads to terminate
    print("Terminating threads...", end="")
    time.sleep_ms(500)  # Give threads time to exit
    print("Done")
    
    return thread_count

# Main function to run tests with different stack sizes
def main():
    # List of stack sizes to test (in bytes)
    stack_sizes = [1024, 2048, 4096, 8192, 16386, 32768, 65536]
    
    for stack_size in stack_sizes:
        max_threads = test_threads(stack_size)
        print(f"Maximum threads with stack size {stack_size}: {max_threads}")
        # Allow some time for cleanup before next test
        time.sleep_ms(1000)
    
    print("\nAll tests completed.")

    wifi_icon = lv.label(lv.screen_active())
    wifi_icon.set_text("Test label")
    wifi_icon.align(lv.ALIGN.CENTER, 0, 0)
    wifi_icon.set_style_text_color(COLOR_TEXT_WHITE, 0)
    
    print("done!")

# Run the tests
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error in main: {e}")

main()
