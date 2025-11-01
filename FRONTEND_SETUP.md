# Frontend Configuration

## Backend API URL

The frontend is now configured to use the Render backend: **https://final-proj-backend-2.onrender.com**

### Configuration Files

- **`src/config.js`**: Centralized API URL configuration
  - Default: Uses Render backend URL
  - Can be overridden with `REACT_APP_API_URL` environment variable

### Environment Variables (Optional)

For local development, you can create a `.env` file in the project root:

```env
REACT_APP_API_URL=http://localhost:5000
```

This will override the default Render URL when running locally.

### For Production Deployment

When deploying to Vercel, Netlify, or similar platforms, set the environment variable:

- **Key**: `REACT_APP_API_URL`
- **Value**: `https://final-proj-backend-2.onrender.com`

Or leave it unset to use the default Render URL in `src/config.js`.

## Testing the Connection

1. Start the frontend: `npm start`
2. The app will connect to the Render backend by default
3. To test locally, create `.env` with `REACT_APP_API_URL=http://localhost:5000`

