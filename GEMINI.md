
# Project Overview

This project implements a delegated voting system in Python. The system allows users to either vote directly or delegate their voting power to other users. The core logic is designed to handle complex delegation chains and cycles, with an iterative algorithm to calculate the final vote distribution.

The project includes:
- A core `delegated_voting` module with a `Voter` and `VotingSystem` class.
- A `delagate_main.py` script that provides a visual representation of the delegation graph using `pygame` and `networkx`.
- Unit tests (`test_delegated_voting.py`) to verify the correctness of the voting algorithm.
- Performance tests (`test_performance.py`) to measure the scalability of the system.

# Building and Running

## Dependencies

The project requires the following Python libraries:
- `pygame`
- `networkx`
- `pytest`

You can install them using pip:
```bash
pip install pygame networkx pytest
```

## Running the Visualization

To see a visual representation of the delegation graph, run the `delagate_main.py` script:
```bash
python delagate_main.py
```

## Running Tests

To run the unit and performance tests, use `pytest`:
```bash
pytest
```

The performance test results will be saved in `performance_results.csv`.

# Development Conventions

- **Testing:** The project uses the `pytest` framework for both unit and performance testing. All new logic should be accompanied by corresponding tests.
- **Code Style:** The code follows standard Python conventions (PEP 8).
- **Modularity:** The core logic is separated from the visualization and testing code.
