"""
Sample code for testing rubric assessment
"""

def calculate_fibonacci(n):
    """
    Calculate the nth Fibonacci number
    
    Args:
        n (int): The position in the Fibonacci sequence
        
    Returns:
        int: The nth Fibonacci number
    """
    if n <= 0:
        raise ValueError("Input must be a positive integer")
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        a, b = 0, 1
        for _ in range(2, n):
            a, b = b, a + b
        return b

class DataProcessor:
    """A simple class to process data"""
    
    def __init__(self, data=None):
        """Initialize with optional data"""
        self.data = data or []
        
    def add_item(self, item):
        """Add an item to the data list"""
        self.data.append(item)
        
    def get_sum(self):
        """Return the sum of all items"""
        return sum(self.data)
        
    def get_average(self):
        """Return the average of all items"""
        if not self.data:
            return 0
        return self.get_sum() / len(self.data)

# Example usage
if __name__ == "__main__":
    # Calculate and print the 10th Fibonacci number
    fib_number = calculate_fibonacci(10)
    print(f"The 10th Fibonacci number is: {fib_number}")
    
    # Create a data processor and add some numbers
    processor = DataProcessor()
    for i in range(1, 6):
        processor.add_item(i)
    
    print(f"Sum: {processor.get_sum()}")
    print(f"Average: {processor.get_average()}")
