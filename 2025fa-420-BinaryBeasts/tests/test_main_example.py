#!/usr/bin/env python3
"""
Test script for main.py using example.json
Automatically provides inputs to test the functionality.
"""
import subprocess
import sys

def test_main_with_example():
    """Test main.py with example.json and various options."""
    
    # Test inputs for the interactive program
    test_inputs = [
        "example.json",     # config file
        "y",               # use same file for time slots (default)
        "test_output.json", # output file
        "5",               # limit (5 schedules)
        "json",            # output format
        "y",               # show config preview
        "n",               # no optimization
        "y"                # continue after config preview (yes, continue)
    ]
    
    # Join inputs with newlines
    input_data = "\n".join(test_inputs) + "\n"
    
    try:
        print("=" * 60)
        print("TESTING main.py with example.json")
        print("=" * 60)
        print("Inputs being provided:")
        for i, inp in enumerate(test_inputs, 1):
            print(f"  {i}. {inp}")
        print("=" * 60)
        print()
        
        # Run the main.py script with the test inputs
        result = subprocess.run(
            [sys.executable, "main.py"],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=30  # 30 second timeout
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nReturn code: {result.returncode}")
        
        # Check if output file was created
        import os
        if os.path.exists("test_output.json"):
            print("\n✅ Output file 'test_output.json' was created successfully!")
            
            # Show first few lines of output
            with open("test_output.json", "r") as f:
                content = f.read()
                print(f"Output file size: {len(content)} characters")
                print("First 500 characters of output:")
                print("-" * 40)
                print(content[:500])
                if len(content) > 500:
                    print("...")
                print("-" * 40)
        else:
            print("\n❌ Output file 'test_output.json' was not created")
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 30 seconds")
    except FileNotFoundError:
        print("❌ Could not find main.py or Python interpreter")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_main_with_example()