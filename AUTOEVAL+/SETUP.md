# AutoEval+ Frontend Setup Guide

## Project Overview

AutoEval+ is an Automatic Subjective Answer Evaluation System built with React, TypeScript, Tailwind CSS, and Vite. This guide will help you set up and run the project locally.

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1. **Node.js** (version 18.x or higher recommended)
   - Download from: https://nodejs.org/
   - To check if installed: `node --version`

2. **npm** (comes with Node.js)
   - To check if installed: `npm --version`

3. **Code Editor** (VS Code recommended)
   - Download from: https://code.visualstudio.com/

---

## Installation Steps

### Step 1: Extract/Clone Project Files

1. Download and extract the project files to a folder on your computer
2. Open the project folder in VS Code:
   - Right-click the folder → "Open with Code"
   - OR: Open VS Code → File → Open Folder → Select project folder

### Step 2: Install Dependencies

Open the integrated terminal in VS Code (View → Terminal or <kbd>Ctrl+`</kbd>) and run:

```bash
npm install
```

This will install all required dependencies including:
- React and React Router
- Tailwind CSS
- shadcn/ui components
- Lucide React icons
- TypeScript
- And all other project dependencies

**Note:** This may take 2-5 minutes depending on your internet connection.

### Step 3: Start Development Server

After installation completes, run:

```bash
npm run dev
```

You should see output similar to:

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 4: Open in Browser

1. Open your web browser (Chrome, Firefox, Edge, etc.)
2. Navigate to: `http://localhost:5173/`
3. The AutoEval+ landing page should load

---

## Testing the Application

### Test User Registration & Login

1. Click "Get Started" or "Register" button
2. Fill in the registration form:
   - Email: `test@example.com`
   - Password: `test123` (minimum 6 characters)
   - Confirm Password: `test123`
3. Click "Create Account"
4. You should be automatically redirected to the Dashboard

### Test Dashboard Features

1. **Upload Answer Sheet:**
   - Click the upload area under "Answer Sheet"
   - Select an image file (PNG, JPG) or PDF
   - Preview will appear

2. **Process OCR:**
   - After uploading answer sheet, click "Process with OCR"
   - Wait for simulated processing (~2 seconds)
   - Extracted text will appear in the right panel

3. **Upload Answer Key:**
   - Click the upload area under "Sample Answer Key"
   - Select an answer key file

4. **Evaluate:**
   - Once both files are uploaded and OCR is processed
   - Click "Evaluate Answers" button
   - Success notification will appear

### Test Dark Mode

- Click the moon/sun icon in the top-right corner
- The theme should toggle between light and dark mode
- Preference is saved in browser localStorage

### Test Logout

1. Click "Logout" button in navbar
2. You should be redirected to the landing page
3. Try accessing `/dashboard` URL directly
4. You should be redirected to login page (protected route)

---

## Project Structure

```
autoeval-plus/
├── public/              # Static assets
│   ├── robots.txt
│   └── favicon.ico
├── src/
│   ├── assets/          # Images and static files
│   ├── components/      # Reusable React components
│   │   ├── ui/          # shadcn/ui components (Button, Card, etc.)
│   │   ├── Navbar.tsx
│   │   ├── FeatureCard.tsx
│   │   └── ProtectedRoute.tsx
│   ├── contexts/        # React Context providers
│   │   └── AuthContext.tsx
│   ├── hooks/           # Custom React hooks
│   │   ├── use-toast.ts
│   │   ├── use-theme.tsx
│   │   └── use-mobile.tsx
│   ├── pages/           # Page components
│   │   ├── Index.tsx       # Landing page
│   │   ├── Login.tsx       # Login page
│   │   ├── Register.tsx    # Registration page
│   │   ├── Dashboard.tsx   # Main dashboard
│   │   └── NotFound.tsx    # 404 page
│   ├── lib/
│   │   └── utils.ts     # Utility functions
│   ├── App.tsx          # Main app component with routing
│   ├── main.tsx         # Entry point
│   ├── index.css        # Global styles and design tokens
│   └── vite-env.d.ts    # TypeScript declarations
├── index.html           # HTML entry point
├── tailwind.config.ts   # Tailwind CSS configuration
├── vite.config.ts       # Vite configuration
├── package.json         # Dependencies and scripts
└── tsconfig.json        # TypeScript configuration
```

---

## Available Scripts

In the project directory, you can run:

### `npm run dev`
- Starts the development server
- Opens at http://localhost:5173/
- Hot Module Replacement (HMR) enabled
- Changes reflect instantly in browser

### `npm run build`
- Creates optimized production build
- Output goes to `dist/` folder
- Minified and optimized for deployment

### `npm run preview`
- Preview production build locally
- Must run `npm run build` first
- Useful for testing before deployment

### `npm run lint`
- Runs ESLint to check code quality
- Reports TypeScript and React errors

---

## Key Features Implemented

### ✅ Authentication System
- Email/password registration with validation
- Login with session persistence
- Protected routes (Dashboard requires login)
- Auto-redirect after login/logout
- Error handling with toast notifications

### ✅ Multi-Page Layout
- Landing page with hero section and features
- Separate Login and Register pages
- Protected Dashboard page
- Smooth routing with React Router
- 404 Not Found page

### ✅ Dashboard Features
- Answer sheet upload with preview
- Answer key upload with preview
- OCR text extraction simulation
- Extracted text display (scrollable)
- Evaluate button with validation
- Responsive layout (mobile + desktop)

### ✅ UI/UX
- Light blue (#3B82F6) primary color theme
- Inter font family
- Dark mode toggle
- Smooth animations (fade-in, scale, hover)
- Soft shadows and rounded corners
- Fully responsive design
- Toast notifications for all actions

---

## Technology Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router v6** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Pre-built React components
- **Lucide React** - Icon library
- **Radix UI** - Accessible component primitives
- **React Hook Form** - Form handling (ready for future use)
- **TanStack Query** - Data fetching (ready for backend integration)

---

## Current Limitations & Future Integration

### Frontend-Only Features (Currently Simulated)
1. **Authentication:** Uses localStorage (not secure for production)
2. **OCR Processing:** Simulated with mock text
3. **Evaluation:** Simulated comparison

### Backend Integration (Coming Soon)
The following will be added when backend is integrated:

1. **Flask API** - Python backend server
2. **MySQL Database** - User data and evaluation storage
3. **PyTesseract OCR** - Real text extraction from images
4. **NLP Comparison** - Actual answer evaluation algorithms
5. **JWT Authentication** - Secure token-based auth
6. **File Storage** - Uploaded file management
7. **Results History** - Save and retrieve past evaluations

**Backend Setup:**
When the backend is ready, you'll need to:
1. Update API endpoints in frontend code
2. Configure CORS settings
3. Set up environment variables for API URL
4. Implement proper authentication flow with JWT

---

## Troubleshooting

### Port Already in Use
If port 5173 is busy:
```bash
npm run dev -- --port 3000
```

### Dependencies Not Installing
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Errors
```bash
# Check TypeScript configuration
npx tsc --noEmit
```

### Build Errors
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

---

## Browser Compatibility

Tested and working on:
- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Edge (latest)
- ✅ Safari (latest)

---

## Additional Notes

1. **localStorage Usage:** The app stores user data and theme preference in browser localStorage. Clear it via browser DevTools if needed.

2. **Sample Test Credentials:** After registration, any email/password combo can be used. Data is stored locally until browser cache is cleared.

3. **File Upload Limits:** Currently set to 10MB max. Adjust in Dashboard.tsx if needed.

4. **OCR Placeholder:** The "Process with OCR" button shows simulated output. Real OCR requires backend integration.

5. **Network Requests:** No API calls are made in this version. All data is client-side only.

---

## Getting Help

If you encounter issues:

1. Check the browser console (F12 → Console tab)
2. Verify Node.js and npm versions
3. Ensure all dependencies installed successfully
4. Try clearing browser cache and localStorage
5. Restart the development server

---

## Next Steps

1. ✅ Complete frontend setup and testing
2. 🔄 Develop Flask backend with MySQL
3. 🔄 Integrate PyTesseract for OCR
4. 🔄 Connect frontend to backend APIs
5. 🔄 Add evaluation algorithm
6. 🔄 Deploy to production

---

## License & Credits

**Project:** AutoEval+ (Final Year Project)  
**Frontend Stack:** React + TypeScript + Tailwind CSS  
**UI Components:** shadcn/ui  
**Icons:** Lucide React  

---

**Happy Coding! 🚀**
