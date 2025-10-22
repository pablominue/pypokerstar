# PyPokerStar 🎲

A professional poker hand range analyzer and library manager built with React and Python.

## Overview

PyPokerStar is a powerful tool for poker players to:
- Create and analyze preflop ranges
- Save and organize range libraries by position and scenario
- Import/Export ranges in JSON format
- Track hand histories and analyze statistics
- Visualize range data with interactive charts

## Tech Stack

### Frontend
- React.js
- Material UI components
- D3.js for data visualization
- Styled Components

### Backend
- Python FastAPI/Django (in development)
- SQLite/PostgreSQL for data persistence

## Project Structure

```
pypokerstar/
├── pokerserver/          # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── lib/         # Utility functions
│   │   └── config.js    # Configuration
│   └── package.json
└── pypokerstar/         # Python backend
    └── src/
        ├── game/        # Core poker logic
        ├── parsers/     # Hand history parsers
        └── types/       # Type definitions
```

## Features

- **Range Editor**
  - Interactive grid for hand selection
  - Color coding for different actions (Raise, Call, 3Bet, All-in)
  - Percentage calculation of selected combos
  - Undo/Redo functionality
  
- **Range Library**
  - Hierarchical organization (Player → Category → Position)
  - Import/Export as JSON
  - Local storage support
  - API integration ready

- **Hand History Analysis**
  - PokerStars hand history parser
  - Statistical analysis
  - Player profiling

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pypokerstar.git
cd pypokerstar
```

2. Install frontend dependencies:
```bash
cd pokerserver
npm install
```

3. Start the development server:
```bash
npm start
```

## Development

### Frontend Development
```bash
cd pokerserver
npm start
```
The app will be available at `http://localhost:3000`

### Running Tests
```bash
npm test
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- PokerStars for hand history format specifications
- React community for component libraries
- D3.js community for visualization tools

## Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter)
Project Link: [https://github.com/yourusername/pypokerstar](https://github.com/yourusername/pypokerstar)