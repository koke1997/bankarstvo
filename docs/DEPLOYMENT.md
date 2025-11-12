# GitHub Pages Deployment

This document explains how the banking application demo is deployed to GitHub Pages.

## Overview

The React application is automatically built and deployed to GitHub Pages using GitHub Actions whenever changes are pushed to the `main` branch.

## Live Demo

The demo is available at: https://koke1997.github.io/bankarstvo/

## Deployment Configuration

### Build Configuration

The application is configured for GitHub Pages deployment with the following settings:

1. **Base Path**: The app uses `/bankarstvo/` as the base path in production
2. **Router**: React Router is configured with `basename="/bankarstvo"` for production
3. **Webpack**: The webpack config uses `publicPath: '/bankarstvo/'` in production mode

### GitHub Actions Workflow

The deployment is automated using the `.github/workflows/deploy-gh-pages.yml` workflow which:

1. Checks out the code
2. Sets up Node.js 18
3. Installs dependencies with `npm ci`
4. Builds the production React app with `npm run build`
5. Uploads the `dist` folder as a Pages artifact
6. Deploys to GitHub Pages

### Key Files

- **`.github/workflows/deploy-gh-pages.yml`**: GitHub Actions workflow for deployment
- **`config/webpack.config.js`**: Webpack configuration with GitHub Pages support
- **`frontend/src/router/AppRouter.tsx`**: React Router configuration with basename
- **`package.json`**: Build scripts for production

## Local Development

To run the app locally in development mode:

```bash
npm install
npm run dev
```

This will start a development server at `http://localhost:3000` without the `/bankarstvo/` base path.

## Building for Production

To build the app for production locally:

```bash
npm run build
```

This will create a production build in the `dist` folder with the correct base path configuration.

## Manual Deployment

The deployment happens automatically on push to `main`, but you can also trigger it manually:

1. Go to the Actions tab in GitHub
2. Select the "Deploy to GitHub Pages" workflow
3. Click "Run workflow"

## Requirements

- Node.js 18 or higher
- npm 8 or higher
- GitHub Pages must be enabled in repository settings
- Repository settings > Pages > Source should be set to "GitHub Actions"

## Troubleshooting

If the deployment fails:

1. Check the Actions tab for error logs
2. Ensure GitHub Pages is enabled in repository settings
3. Verify that the workflow has proper permissions (pages: write)
4. Check that the build completes successfully locally

## Notes

- The `.nojekyll` file is automatically created during the build to prevent GitHub Pages from processing the site with Jekyll
- The app uses client-side routing, so all routes will work correctly with the configured `historyApiFallback` behavior
- Static assets are bundled in the `dist/static` folder
