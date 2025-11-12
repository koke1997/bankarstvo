# Banking Application

A modern banking application built with React, TypeScript, and Python backend.

## 🚀 Live Demo

Check out the live demo: **[https://koke1997.github.io/bankarstvo/](https://koke1997.github.io/bankarstvo/)**

## Features

- User authentication and authorization
- Dashboard with account overview
- Transaction management
- Secure API communication
- Responsive design with modern UI

## Technology Stack

### Frontend
- React 18
- TypeScript
- React Router v6
- Webpack 5
- Tailwind CSS

### Backend
- Python/Flask
- MySQL Database
- Docker & Kubernetes support

## Getting Started

### Prerequisites

- Node.js 18 or higher
- npm 8 or higher
- Python 3.9 or higher
- MySQL 5.7 or higher (for backend)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/koke1997/bankarstvo.git
cd bankarstvo
```

2. Install frontend dependencies:
```bash
npm install
```

3. Install backend dependencies:
```bash
pip install -r requirements.txt
```

### Development

Run the frontend development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### Building for Production

Build the React application:
```bash
npm run build
```

This creates an optimized production build in the `dist` folder.

### Linting

Run linting checks:
```bash
npm run lint
```

### Testing

Run tests:
```bash
npm test
```

## Deployment

The application is automatically deployed to GitHub Pages on every push to the `main` branch. See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment information.

## Project Structure

```
bankarstvo/
├── frontend/          # React frontend application
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── router/
│   │   ├── services/
│   │   └── styles/
│   └── public/
├── api/              # Backend API
├── database/         # Database schemas and migrations
├── config/           # Configuration files
│   ├── webpack.config.js
│   └── tsconfig.json
├── k8s/              # Kubernetes configurations
├── .github/
│   └── workflows/    # CI/CD workflows
└── docs/             # Documentation
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**koke1997**

## Acknowledgments

- Thanks to all contributors who helped build this project
- Inspired by modern banking applications and best practices in web development
