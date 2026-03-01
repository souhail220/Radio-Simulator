import time
from app.simulator import Simulator

def benchmark():
    print("⏱️ Starting benchmark...")
    start_time = time.time()
    
    try:
        simulator = Simulator()
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"✅ Initialization complete!")
        print(f"📊 Teams loaded: {len(simulator.teams)}")
        print(f"⏱️ TOTAL TIME TAKEN: {duration:.2f} seconds")
        
        if duration > 30:
            print("❌ WARNING: Initialization is very slow (> 30s)!")
        else:
            print("🚀 Performance is acceptable.")
            
    except Exception as e:
        print(f"❌ Error during benchmark: {e}")

if __name__ == "__main__":
    benchmark()
