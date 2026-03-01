from .simulator import Simulator

if __name__ == "__main__":
    simulator = Simulator()
    simulator.setup()
    simulator.run()