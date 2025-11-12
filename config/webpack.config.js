const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

// Determine if we're building for GitHub Pages
const isProduction = process.env.NODE_ENV === 'production';
const publicPath = isProduction ? '/bankarstvo/' : '/';

module.exports = {
  mode: isProduction ? 'production' : 'development',
  entry: path.resolve(__dirname, '../frontend/src/index.tsx'),
  output: {
    path: path.resolve(__dirname, '../dist'),
    filename: 'static/js/bundle.[contenthash].js',
    publicPath: publicPath,
    clean: true
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js', '.jsx']
  },
  module: {
    rules: [
      {
        test: /\.(ts|tsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'ts-loader',
          options: {
            configFile: path.resolve(__dirname, 'tsconfig.json')
          }
        }
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader']
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: 'asset/resource'
      }
    ]
  },
  plugins: [
    new CleanWebpackPlugin(),
    new HtmlWebpackPlugin({
      template: path.resolve(__dirname, '../frontend/public/index.html'),
      filename: 'index.html'
    })
  ],
  devServer: {
    historyApiFallback: true,
    static: {
      directory: path.resolve(__dirname, '../static')
    },
    compress: true,
    port: 3000,
    proxy: {
      '/api': 'http://localhost:5000'
    }
  }
};