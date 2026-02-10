import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from '@/hooks/use-toast';
import { api } from '@/lib/api'; // Import the axios instance

export type UserRole = 'student' | 'teacher';

interface User {
  username: string; // Mapping to email for backend
  role: UserRole;
  rollNumber?: string;
  department?: string;
  // stored locally
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loginStudent: (username: string, rollNumber: string, password: string) => Promise<boolean>;
  loginTeacher: (username: string, password: string) => Promise<boolean>;
  registerStudent: (username: string, rollNumber: string, password: string, confirmPassword: string, classroomId?: string) => Promise<boolean>;
  registerTeacher: (username: string, password: string, confirmPassword: string, department?: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true); // Added isLoading state
  const navigate = useNavigate();

  useEffect(() => {
    // Check for existing session
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('autoeval_user');

    if (token && savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setIsLoading(false); // Set loading to false after checking session
  }, []);

  const loginStudent = async (username: string, rollNumber: string, password: string): Promise<boolean> => {
    if (!username.trim() || !password.trim()) {
      toast({ title: "Error", description: "Missing credentials", variant: "destructive" });
      return false;
    }

    try {
      // Helper: Auto-append domain if missing
      let email = username.trim();
      if (!email.includes('@')) {
        email += '@school.com';
      }

      // Backend expects: { email, password }
      // Using strict student login endpoint
      const response = await api.post('/auth/student/login', {
        email: email,
        password: password
      });

      const { access_token, full_name, user_id } = response.data;

      // Save Token
      localStorage.setItem('token', access_token);

      // Create User Object
      // Use backend provided full_name if available, else username
      const userData: User = {
        username: full_name || username,
        role: 'student',
        rollNumber,
        department: ""
      };
      setUser(userData);
      localStorage.setItem('autoeval_user', JSON.stringify(userData));

      toast({ title: "Welcome back!", description: "Login successful." });
      navigate('/student-dashboard');
      return true;

    } catch (error: any) {
      console.error("Login Check:", error);
      toast({
        title: "Login Failed",
        description: error.response?.data?.detail || "Invalid credentials",
        variant: "destructive",
      });
      return false;
    }
  };

  const loginTeacher = async (username: string, password: string): Promise<boolean> => {
    if (!username.trim() || !password.trim()) {
      toast({ title: "Error", description: "Missing credentials", variant: "destructive" });
      return false;
    }

    try {
      // Using strict teacher login endpoint
      const response = await api.post('/auth/teacher/login', {
        email: username,
        password: password
      });

      const { access_token, full_name } = response.data;

      localStorage.setItem('token', access_token);

      const userData: User = {
        username: full_name || username,
        role: 'teacher'
      };
      setUser(userData);
      localStorage.setItem('autoeval_user', JSON.stringify(userData));

      toast({ title: "Welcome back!", description: "Login successful." });
      navigate('/teacher-dashboard');
      return true;

    } catch (error: any) {
      toast({
        title: "Login Failed",
        description: error.response?.data?.detail || "Invalid credentials",
        variant: "destructive",
      });
      return false;
    }
  };

  const registerStudent = async (
    username: string,
    rollNumber: string,
    password: string,
    confirmPassword: string
  ): Promise<boolean> => {
    if (password !== confirmPassword) {
      toast({ title: "Error", description: "Passwords do not match", variant: "destructive" });
      return false;
    }

    try {
      // Backend: { email, password, role, roll_number }
      await api.post('/register', {
        email: username,
        password: password,
        role: 'student',
        roll_number: rollNumber
      });

      toast({ title: "Account Created!", description: "Please login now." });
      // Don't auto-login, let them login
      navigate('/student-login');
      return true;

    } catch (error: any) {
      toast({
        title: "Registration Failed",
        description: error.response?.data?.detail || "Could not register.",
        variant: "destructive",
      });
      return false;
    }
  };

  const registerTeacher = async (
    username: string,
    password: string,
    confirmPassword: string,
    department?: string
  ): Promise<boolean> => {
    if (password !== confirmPassword) {
      toast({ title: "Error", description: "Passwords do not match", variant: "destructive" });
      return false;
    }

    try {
      await api.post('/register', {
        email: username,
        password: password,
        role: 'teacher',
        department: department
      });

      toast({ title: "Account Created!", description: "Please login now." });
      navigate('/teacher-login');
      return true;

    } catch (error: any) {
      toast({
        title: "Registration Failed",
        description: error.response?.data?.detail || "Could not register.",
        variant: "destructive",
      });
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('autoeval_user');
    localStorage.removeItem('token'); // Clear the real token!
    toast({
      title: "Logged Out",
      description: "You have been successfully logged out.",
    });
    navigate('/');
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      loginStudent,
      loginTeacher,
      registerStudent,
      registerTeacher,
      logout,
      isLoading
    }}>
      {children}
    </AuthContext.Provider>
  );
};
