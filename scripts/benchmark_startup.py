import time
from app.simulator import Simulator

def benchmark():
    print("Starting benchmark...")
    start_time = time.time()
    
    try:
        instantiation_start = time.time()
        simulator = Simulator()
        instantiation_end = time.time()
        
        setup_start = time.time()
        simulator.setup()
        setup_end = time.time()
        
        total_duration = setup_end - instantiation_start
        print(f"Initialization complete!")
        print(f"Teams loaded: {len(simulator.teams)}")
        print(f"Instantiation time: {instantiation_end - instantiation_start:.4f} seconds")
        print(f"Setup time: {setup_end - setup_start:.2f} seconds")
        print(f"TOTAL TIME TAKEN: {total_duration:.2f} seconds")
        
        if total_duration > 30:
            print("WARNING: Initialization is very slow (> 30s)!")
        else:
            print("Performance is acceptable.")
            
    except Exception as e:
        print(f"Error during benchmark: {e}")

if __name__ == "__main__":
    benchmark()
