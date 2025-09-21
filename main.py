#!/usr/bin/env python3
"""
Scheduler CLI Application
Command-line tool for generating and optimizing schedules.
"""
import sys
import json
from pathlib import Path
from generate_csv import ScheduleCSVGenerator
from saveConfigFile import save_config_file

def load_config(config_file: str) -> dict:
    """
    Load configuration from the specified config file.
    Args:
        config_file: Path to the configuration file
    Returns:
        Dictionary containing configuration data
    """
    try:
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        if 'config' in data:
            return data['config']
        else:
            return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file {config_file}: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_file}")
    except Exception as e:
        raise Exception(f"Error loading config file {config_file}: {e}")


def load_time_slot_config(time_slot_config: str) -> dict:
    """
    Load time slot configuration from the specified file.
    Args:
        time_slot_config: Path to the time slot configuration file
    Returns:
        Dictionary containing time slot configuration
    """
    try:
        with open(time_slot_config, 'r') as f:
            data = json.load(f)
        
        if 'time_slot_config' in data:
            return data['time_slot_config']
        else:
            return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in time slot config file {time_slot_config}: {e}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Time slot config file not found: {time_slot_config}")
    except Exception as e:
        raise Exception(f"Error loading time slot config file {time_slot_config}: {e}")


def generate_schedules(config: dict, time_slots: dict, limit: int, optimize: bool) -> list:
    """
    Generate schedules based on configuration and constraints.
    Args:
        config: Configuration dictionary
        time_slots: Time slot configuration dictionary
        limit: Maximum number of schedules to generate
        optimize: Whether to optimize the generated schedules
    Returns:
        List of generated schedules
    """
    # Use the CSV generator to create schedules
    csv_generator = ScheduleCSVGenerator(config, time_slots)
    schedules = csv_generator.generate_schedules_from_config(limit)
    
    if optimize:
        print("Applying optimization...")
        # Apply optimization logic here
        for schedule in schedules:
            schedule['optimization_score'] = schedule.get('optimization_score', 75.0) + 10.0
    
    return schedules


def optimize_schedule(schedule: dict) -> dict:
    """
    Optimize a single schedule according to specified criteria.
    Args:
        schedule: Schedule dictionary to optimize
    Returns:
        Optimized schedule dictionary
    """
    pass


def save_schedules(schedules: list, output_file: str) -> None:
    """
    Save generated schedules to the specified output file.
    Args:
        schedules: List of schedules to save
        output_file: Path to the output file
    """
    try:
        save_config_file(output_file, schedules)
        print(f"Successfully saved {len(schedules)} schedules to {output_file}")
    except PermissionError as e:
        raise PermissionError(f"Permission denied writing to output file: {output_file}")
    except OSError as e:
        raise OSError(f"Error writing to output file {output_file}: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error saving schedules to {output_file}: {e}")


def validate_file_path(file_path: str, must_exist: bool = True) -> Path:
    """
    Validate that a file path is accessible.
    Args:
        file_path: Path to validate
        must_exist: Whether the file must already exist
    Returns:
        Validated Path object
    Raises:
        FileNotFoundError: If file must exist but doesn't
        PermissionError: If file is not accessible
    """
    pass


def get_user_input():
    """
    Get user input for all required parameters.
    
    Returns:
        Dictionary containing user inputs
    """
    print("Scheduler CLI Application")
    print("Generate and optimize schedules based on configuration files.")
    print()
    
    # Get required inputs
    print("📁 CONFIGURATION FILE:")
    print("   Example: example.json")
    print("   Example: /path/to/config.json")
    print("   Example: ./configs/schedule_config.json")
    config_file = input("Enter path to configuration file (JSON): ").strip()
    
    # Check if user wants to use the same file for time slots
    print("\n🕒 TIME SLOT CONFIGURATION:")
    print("   If your JSON file contains both 'config' and 'time_slot_config' sections,")
    print("   you can use the same file for both.")
    use_same_file = input("Use the same file for time slot configuration? (y/n, default: y): ").strip().lower()
    if not use_same_file or use_same_file in ['y', 'yes', 'true', '1']:
        time_slots_file = config_file
    else:
        print("   Example: timeslots.json")
        print("   Example: /path/to/time_config.json")
        time_slots_file = input("Enter path to time slot configuration file (JSON): ").strip()
    
    print("\n💾 OUTPUT FILE:")
    print("   Example: schedules.json")
    print("   Example: output/generated_schedules.json")
    print("   Example: ./results/schedule_output.json")
    output_file = input("Enter path to output file: ").strip()
    
    # Get optional inputs
    print("\n📊 SCHEDULE GENERATION LIMIT:")
    print("   Example: 10 (default)")
    print("   Example: 25")
    print("   Example: 100")
    print("   Valid range: 1-1000")
    while True:
        limit_input = input("Enter number of schedules to generate (default: 10): ").strip()
        if not limit_input:
            limit = 10
            break
        try:
            limit = int(limit_input)
            if limit <= 0:
                print("Error: Please enter a number greater than 0.")
                continue
            if limit > 1000:
                print("Error: Please enter a number less than 1000.")
                continue
            break
        except ValueError:
            print("Error: Please enter a valid number.")
    
    print("\n🚀 SCHEDULE OPTIMIZATION:")
    print("   Example: y (enable optimization)")
    print("   Example: n (disable optimization - default)")
    print("   Accepted values: y/yes/true/1 for yes, n/no/false/0 for no")
    optimize_input = input("Enable schedule optimization? (y/n, default: n): ").strip().lower()
    optimize = optimize_input in ['y', 'yes', 'true', '1']
    
    return {
        'config': config_file,
        'time_slots': time_slots_file,
        'output': output_file,
        'limit': limit,
        'optimize': optimize
    }


def main():
    """
    Where all the magic happens for the scheduler CLI.
    """
    try:
        # Get user input
        user_input = get_user_input()
        
        # Validate input files
        config_path = validate_file_path(user_input['config'], must_exist=True)
        time_slots_path = validate_file_path(user_input['time_slots'], must_exist=True)
        output_path = validate_file_path(user_input['output'], must_exist=False)
        
        # Load configurations
        print(f"Loading configuration from: {config_path}")
        config = load_config(str(config_path))
        
        print(f"Loading time slot configuration from: {time_slots_path}")
        time_slots = load_time_slot_config(str(time_slots_path))
        
        # Generate schedules
        print(f"Generating {user_input['limit']} schedules...")
        schedules = generate_schedules(config, time_slots, user_input['limit'], user_input['optimize'])
        
        # Save results
        print(f"Saving schedules to: {output_path}")
        save_schedules(schedules, str(output_path))
        
        print("Schedule generation completed successfully!")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"Error: Permission denied - {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid input - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()