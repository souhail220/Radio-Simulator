from .simulator import Simulator
from .config import logger

if __name__ == "__main__":
    logger.info("Start Project")
    simulator = Simulator(logger)
    simulator.setup()
    simulator.run()