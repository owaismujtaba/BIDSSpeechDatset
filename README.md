# BIDSSpeechDataset

BIDSSpeechDataset is a tool for analyzing and processing speech datasets, particularly designed for use with the Brain Imaging Data Structure (BIDS) format. It provides functionality for handling both EEG and audio data, with a focus on synchronization and analysis.

## Features

- EEG (.edf) and Audio (.xdf) data processing
- GUI interface for easy interaction and visualization
- Synchronization of EEG and Audio data
- BIDS-compatible data handling
- Audio event mapping and analysis
- EEG event processing and visualization

## Project Structure

- `src/`
  - `config.py`: Configuration settings for the project
  - `gui/`
    - `main_interface.py`: Main GUI interface for the application
    - `mapping_page.py`: GUI for EEG and Audio data mapping
  - `audio_data_utils.py`: Utility functions for audio data processing
  - `eeg_data_utils.py`: Utility functions for EEG data processing
  - `audio_analyser.py`: Core functionality for audio analysis
  - `utils.py`: General utility functions

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/owaismujtaba/BIDSSpeechDataset.git
   cd BIDSSpeechDataset
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the project (see Configuration section below)

4. Run the main application:
   ```bash
   python main.py
   ```

## Dependencies

The project requires the following main dependencies:

![PyQt5](https://img.shields.io/badge/PyQt5-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![MNE](https://img.shields.io/badge/MNE-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)

To create a `requirements.txt` file, you can use the following command in your project directory:

```bash
pip freeze > requirements.txt
```

## Configuration

The `src/config.py` file contains various configuration options for the project. Before running the application, you should review and modify these settings as needed:

1. Open `src/config.py` in a text editor.

2. Adjust the following settings:

   - `bidsDir`: Set the path to your BIDS directory
   - `numWorkers`: Set the number of worker processes (default is 20)
   - `use_gui`: Set to `True` to use the GUI interface, `False` for command-line operation
   - `windowIconPath`: Path to the window icon file
   - `audioPlayerDir`: Directory for sample audio files
   - `timeDifference`: Set the time difference for audio synchronization (default is 0)
   - `removeChannel147`: Set to `True` to remove channel 147, `False` to keep it, raises issues with edf export
   - `analyseAudio`: Set to `True` to enable audio analysis, `False` to disable it

3. Save the changes to `config.py`

Example configuration:

## Usage

1. Launch the application using the instructions in the "Getting Started" section.
2. Use the GUI to load your EEG (.edf) and Audio (.xdf) files.
3. Process and analyze the data using the provided tools:
   - View EEG and Audio file information
   - Visualize EEG channels
   - Synchronize EEG and Audio data
   - Map audio events
4. Convert the data to BIDS format.

For more detailed usage instructions, please refer to the in-app guidance and tooltips.

## Contributing

We welcome contributions to the BIDSSpeechDataset project. Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with clear, descriptive messages
4. Push your changes to your fork
5. Submit a pull request to the main repository

Please ensure your code adheres to the project's coding standards and include appropriate tests for new features.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions, issues, or suggestions, please open an issue on the GitHub repository or contact the project maintainers:

- [Owais Mujtaba](mailto:owais.mujtaba123@gmail.com)
- [Project GitHub Issues](https://github.com/owaismujtaba/BIDSSpeechDataset/issues)
