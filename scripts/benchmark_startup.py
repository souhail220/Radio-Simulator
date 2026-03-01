import time
from app.simulator import Simulator
from app.config import logger

def benchmark():
    logger.info("Starting benchmark...")
    
    try:
        instantiation_start = time.time()
        simulator = Simulator(logger)
        instantiation_end = time.time()
        
        setup_start = time.time()
        simulator.setup()
        setup_end = time.time()
        
        total_duration = setup_end - instantiation_start
        logger.info("Initialization complete!")
        logger.info(f"Teams loaded: {len(simulator.teams)}")
        logger.info(f"Instantiation time: {instantiation_end - instantiation_start:.4f} seconds")
        logger.info(f"Setup time: {setup_end - setup_start:.2f} seconds")
        logger.info(f"TOTAL TIME TAKEN: {total_duration:.2f} seconds")
        
        if total_duration > 30:
            logger.warning("WARNING: Initialization is very slow (> 30s)!")
        else:
            logger.info("Performance is acceptable.")
            
    except Exception as e:
        logger.error(f"Error during benchmark: {e}")

if __name__ == "__main__":
    benchmark()
