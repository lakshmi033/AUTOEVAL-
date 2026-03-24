import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileCheck2, Moon, Sun, GraduationCap } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/hooks/use-theme';
import { api } from '@/lib/api';
import { toast } from '@/hooks/use-toast';

const StudentLogin = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { isAuthenticated, user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated && user) {
      if (user.role === 'student') navigate('/student-dashboard');
      else if (user.role === 'teacher') navigate('/teacher-dashboard');
    }
  }, [isAuthenticated, user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Resolve email
      let resolvedEmail = email.trim();
      if (!resolvedEmail.includes('@')) resolvedEmail += '@school.com';

      // Call the new student-specific login endpoint
      const response = await api.post('/student/login', {
        email: resolvedEmail,
        password: password,
      });

      const { access_token, full_name, roll_number, class_name, is_evaluated } = response.data;

      // Store JWT
      localStorage.setItem('token', access_token);

      // Store student metadata for left sidebar
      localStorage.setItem('student_meta', JSON.stringify({
        fullName: full_name || email,
        rollNumber: roll_number ?? '—',
        className: class_name ?? '—',
        isEvaluated: is_evaluated ?? false,
      }));

      // Create user context entry (compatible with existing AuthContext)
      const userData = {
        username: full_name || email,
        role: 'student' as const,
        rollNumber: String(roll_number ?? ''),
        department: '',
      };
      localStorage.setItem('autoeval_user', JSON.stringify(userData));

      toast({ title: 'Welcome!', description: 'Login successful.' });
      // Use a full page reload so AuthContext re-reads the token from localStorage on mount
      setTimeout(() => { window.location.href = '/student-dashboard'; }, 300);

    } catch (error: any) {
      const detail = error?.response?.data?.detail || 'Invalid credentials or not a student account.';
      toast({ title: 'Login Failed', description: detail, variant: 'destructive' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen py-12 px-4 bg-gradient-to-br from-primary/5 via-background to-primary/10">
      <div className="absolute top-4 right-4">
        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>
      </div>

      <div className="text-center mb-10 animate-fade-in">
        <div className="flex justify-center mb-4">
          <Link to="/" className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-light hover:opacity-80 transition-opacity">
            <FileCheck2 className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold text-foreground">AutoEval+</span>
          </Link>
        </div>
        <h1 className="text-2xl font-bold text-foreground">Student Portal</h1>
        <p className="text-muted-foreground mt-2">Sign in to view your evaluation results</p>
      </div>

      <div className="container mx-auto max-w-md">
        <Card className="shadow-soft-lg animate-scale-in">
          <CardHeader className="text-center space-y-3">
            <div className="flex justify-center">
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary-light">
                <GraduationCap className="h-6 w-6 text-primary" />
              </div>
            </div>
            <CardTitle className="text-xl">Student Login</CardTitle>
            <CardDescription>Access your evaluation dashboard</CardDescription>
          </CardHeader>

          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="name@school.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="transition-base"
                  autoComplete="email"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="transition-base"
                  autoComplete="current-password"
                />
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? 'Signing in...' : 'Sign In as Student'}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm text-muted-foreground">
              <Link to="/login" className="text-primary hover:underline">
                Back to Login Selection
              </Link>
            </div>
          </CardContent>
        </Card>

        <div className="text-center mt-8 text-sm text-muted-foreground animate-fade-in" style={{ animationDelay: '200ms' }}>
          Don't have an account?{' '}
          <Link to="/register" className="text-primary hover:underline font-medium">
            Create Account
          </Link>
        </div>
      </div>
    </div>
  );
};

export default StudentLogin;
