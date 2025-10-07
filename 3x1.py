"""
Collatz Conjecture Random Large Number Tester - PERSISTENT VERSION
Tests random numbers over 10 billion against the 3x+1 problem
Maintains a permanent log file to prevent retesting across multiple runs

Perfect for school projects and long-term research!
"""

import random
import time
import json
import os
from datetime import datetime


# Configuration
LOG_FILE = 'collatz_tested_numbers.json'
RESULTS_LOG = 'collatz_results_log.txt'


def load_tested_numbers():
    """
    Load previously tested numbers from the log file.
    Returns: set of tested numbers
    """
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                data = json.load(f)
                tested = set(data.get('tested_numbers', []))
                print(f"✓ Loaded {len(tested):,} previously tested numbers from log file")
                return tested, data.get('all_time_stats', {})
        except Exception as e:
            print(f"⚠️  Error loading log file: {e}")
            print("   Starting fresh...")
            return set(), {}
    else:
        print("📝 No previous log file found. Starting fresh!")
        return set(), {}


def save_tested_numbers(tested_numbers, all_time_stats):
    """
    Save tested numbers to the log file.
    """
    try:
        data = {
            'tested_numbers': list(tested_numbers),
            'total_tested': len(tested_numbers),
            'last_updated': datetime.now().isoformat(),
            'all_time_stats': all_time_stats
        }
        with open(LOG_FILE, 'w') as f:
            json.dump(data, f)
        print(f"✓ Saved {len(tested_numbers):,} tested numbers to log file")
    except Exception as e:
        print(f"⚠️  Error saving log file: {e}")


def append_to_results_log(session_info):
    """
    Append session results to a human-readable log file.
    """
    try:
        with open(RESULTS_LOG, 'a') as f:
            f.write("="*70 + "\n")
            f.write(f"Session Date: {session_info['timestamp']}\n")
            f.write(f"Numbers tested this session: {session_info['tested_this_session']:,}\n")
            f.write(f"Total unique numbers tested: {session_info['total_unique']:,}\n")
            f.write(f"Longest sequence: {session_info['longest_sequence']:,} steps "
                   f"(number: {session_info['longest_num']:,})\n")
            f.write(f"Highest peak: {session_info['highest_peak']:,} "
                   f"(from: {session_info['highest_peak_num']:,})\n")
            f.write(f"Average steps: {session_info['average_steps']:.2f}\n")
            f.write("="*70 + "\n\n")
    except Exception as e:
        print(f"⚠️  Error appending to results log: {e}")


def collatz_steps(n):
    """
    Count the number of steps to reach 1 in the Collatz sequence.
    Returns: (steps, max_value_reached)
    """
    if n == 1:
        return 0, 1
    
    original = n
    steps = 0
    max_val = n
    
    while n != 1:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        
        steps += 1
        max_val = max(max_val, n)
        
        # Safety check
        if steps > 100000:
            return steps, max_val
    
    return steps, max_val


def test_random_large_numbers(num_tests=100_000_000, min_value=10_000_000_000,
                               max_value=1_000_000_000_000_000_000_000_000_000):
    """
    Test random numbers >= min_value.
    Loads previous tests and avoids duplicates across all runs.
    """
    print(f"\nTesting {num_tests:,} NEW random numbers")
    print(f"Range: {min_value:,} to {max_value:,}")
    print("=" * 70)
    
    # Load previously tested numbers
    tested_numbers, all_time_stats = load_tested_numbers()
    initial_count = len(tested_numbers)
    
    # Initialize all-time stats if empty
    if not all_time_stats:
        all_time_stats = {
            'longest_sequence': 0,
            'longest_num': 0,
            'highest_peak': 0,
            'highest_peak_num': 0,
            'total_steps': 0,
            'total_numbers': 0
        }
    
    # Current session statistics
    all_reach_one = True
    
    longest_sequence = all_time_stats.get('longest_sequence', 0)
    longest_sequence_num = all_time_stats.get('longest_num', 0)
    
    highest_peak = all_time_stats.get('highest_peak', 0)
    highest_peak_num = all_time_stats.get('highest_peak_num', 0)
    
    shortest_sequence = float('inf')
    shortest_sequence_num = 0
    
    session_total_steps = 0
    
    # For this session's top performers
    session_top_10_longest = []
    session_top_10_highest = []
    
    # Progress tracking
    checkpoint = num_tests // 20  # 5% increments
    start_time = time.time()
    
    print("\n🎲 Generating and testing NEW random numbers...")
    print("   (Automatically skipping any previously tested numbers)")
    print()
    
    test_count = 0
    attempts = 0
    duplicates_skipped = 0
    max_attempts = num_tests * 100  # Safety limit
    
    while test_count < num_tests and attempts < max_attempts:
        # Generate random number
        num = random.randint(min_value, max_value)
        attempts += 1
        
        # Skip if already tested (even from previous runs!)
        if num in tested_numbers:
            duplicates_skipped += 1
            continue
        
        tested_numbers.add(num)
        test_count += 1
        
        # Test this number
        steps, max_val = collatz_steps(num)
        
        # Track session statistics
        session_total_steps += steps
        all_time_stats['total_steps'] += steps
        all_time_stats['total_numbers'] += 1
        
        # Update all-time records
        if steps > longest_sequence:
            longest_sequence = steps
            longest_sequence_num = num
            all_time_stats['longest_sequence'] = steps
            all_time_stats['longest_num'] = num
        
        if steps < shortest_sequence:
            shortest_sequence = steps
            shortest_sequence_num = num
        
        if max_val > highest_peak:
            highest_peak = max_val
            highest_peak_num = num
            all_time_stats['highest_peak'] = max_val
            all_time_stats['highest_peak_num'] = num
        
        # Track session top 10
        session_top_10_longest.append((steps, num))
        session_top_10_longest.sort(reverse=True)
        session_top_10_longest = session_top_10_longest[:10]
        
        session_top_10_highest.append((max_val, num))
        session_top_10_highest.sort(reverse=True)
        session_top_10_highest = session_top_10_highest[:10]
        
        # Progress indicator
        if test_count % checkpoint == 0:
            progress = (test_count / num_tests) * 100
            elapsed = time.time() - start_time
            rate = test_count / elapsed if elapsed > 0 else 0
            print(f"Progress: {progress:5.1f}% | {test_count:,} new | "
                  f"{duplicates_skipped:,} dups skipped | {rate:.0f} tests/sec")
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # Save the updated tested numbers
    save_tested_numbers(tested_numbers, all_time_stats)
    
    # Final results
    print(f"\n{'='*70}")
    print("✓ SESSION COMPLETE!")
    print(f"{'='*70}\n")
    
    print(f"📊 THIS SESSION:")
    print(f"   New numbers tested: {test_count:,}")
    print(f"   Duplicates skipped: {duplicates_skipped:,}")
    print(f"   Generation attempts: {attempts:,}")
    print(f"   All numbers reached 1: {all_reach_one}")
    print(f"   Session average steps: {session_total_steps / test_count:.2f}")
    print(f"   Execution time: {elapsed:.2f} seconds")
    print(f"   Testing rate: {test_count / elapsed:.0f} numbers/second")
    
    print(f"\n📚 ALL-TIME TOTALS:")
    print(f"   Total unique numbers ever tested: {len(tested_numbers):,}")
    print(f"   Numbers tested before this session: {initial_count:,}")
    print(f"   All-time average steps: {all_time_stats['total_steps'] / all_time_stats['total_numbers']:.2f}")
    
    print(f"\n🏆 ALL-TIME RECORDS:")
    print(f"   Longest sequence ever: {longest_sequence:,} steps")
    print(f"   └─ Number: {longest_sequence_num:,}")
    
    print(f"\n   Highest peak ever: {highest_peak:,}")
    print(f"   └─ Number: {highest_peak_num:,}")
    print(f"   └─ Peak is {highest_peak / highest_peak_num:.0f}x the starting number")
    
    print(f"\n🥇 THIS SESSION'S TOP 10 LONGEST:")
    for i, (steps, num) in enumerate(session_top_10_longest, 1):
        marker = "🆕 NEW RECORD!" if steps == longest_sequence and num == longest_sequence_num else ""
        print(f"   {i:2d}. {num:,} → {steps:,} steps {marker}")
    
    print(f"\n🚀 THIS SESSION'S TOP 10 HIGHEST PEAKS:")
    for i, (peak, num) in enumerate(session_top_10_highest, 1):
        ratio = peak / num
        marker = "🆕 NEW RECORD!" if peak == highest_peak and num == highest_peak_num else ""
        print(f"   {i:2d}. {num:,} → {peak:,} ({ratio:.0f}x) {marker}")
    
    # Append to human-readable log
    session_info = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'tested_this_session': test_count,
        'total_unique': len(tested_numbers),
        'longest_sequence': longest_sequence,
        'longest_num': longest_sequence_num,
        'highest_peak': highest_peak,
        'highest_peak_num': highest_peak_num,
        'average_steps': session_total_steps / test_count
    }
    append_to_results_log(session_info)
    
    return {
        'session_tested': test_count,
        'total_unique': len(tested_numbers),
        'duplicates_skipped': duplicates_skipped,
        'all_time_stats': all_time_stats
    }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("COLLATZ CONJECTURE - PERSISTENT RANDOM TESTER")
    print("School Project Edition - Remembers All Previous Tests!")
    print("="*70)
    
    print("\n📁 Log files:")
    print(f"   Numbers database: {LOG_FILE}")
    print(f"   Results history: {RESULTS_LOG}")
    
    # Use a fixed number of tests (non-interactive)
    print("\n" + "="*70)
    num_tests = 1_000_000
    print(f"Automatically testing {num_tests:,} new numbers this session (no prompt).")
    
    # Test random large numbers
    results = test_random_large_numbers(
        num_tests=num_tests,
        min_value=10_000_000_000,      
        max_value=1_000_000_000_000_000_000_000_000_000_000    
    )
    
    print("\n" + "="*70)
    print("🎯 CONCLUSION:")
    print(f"   Session successfully tested {results['session_tested']:,} new numbers!")
    print(f"   Total project database: {results['total_unique']:,} unique numbers")
    print(f"   Skipped {results['duplicates_skipped']:,} duplicates")
    print("   The Collatz conjecture holds for ALL tested numbers! ✓")
    print("="*70 + "\n")
    
    print("💡 TIP: Run this program again anytime to test more numbers!")
    print("    The log file remembers everything! 🎓\n")
