#!/usr/bin/env python3
"""
Test script for main.py using example.json with CSV output
"""
import subprocess
import sys

def test_csv_output():
    """Test main.py with CSV output format."""
    
    # Test inputs for CSV format
    test_inputs = [
        "example.json",     # config file
        "y",               # use same file for time slots
        "test_output.csv",  # output file (CSV)
        "3",               # limit (3 schedules for quick test)
        "csv",             # output format (CSV)
        "n",               # no config preview
        "n"                # no optimization
    ]
    
    input_data = "\n".join(test_inputs) + "\n"
    
    try:
        print("=" * 60)
        print("TESTING main.py with CSV output")
        print("=" * 60)
        
        result = subprocess.run(
            [sys.executable, "main.py"],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=30
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        print(f"\nReturn code: {result.returncode}")
        
        # Check if CSV file was created
        import os
        if os.path.exists("test_output.csv"):
            print("\n✅ CSV output file 'test_output.csv' was created successfully!")
            
            with open("test_output.csv", "r") as f:
                content = f.read()
                print(f"CSV file size: {len(content)} characters")
                print("First 1000 characters of CSV:")
                print("-" * 40)
                print(content[:1000])
                if len(content) > 1000:
                    print("...")
                print("-" * 40)
        else:
            print("\n❌ CSV file was not created")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_csv_output()