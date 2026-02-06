import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileCheck2, Moon, Sun, GraduationCap, BookOpen, ArrowRight } from 'lucide-react';
import { useTheme } from '@/hooks/use-theme';

const Login = () => {
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen py-12 px-4 bg-gradient-to-br from-primary/5 via-background to-primary/10">
      <div className="absolute top-4 right-4">
        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>
      </div>

      {/* Header */}
      <div className="text-center mb-10 animate-fade-in">
        <div className="flex justify-center mb-4">
          <Link to="/" className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-light hover:opacity-80 transition-opacity">
            <FileCheck2 className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold text-foreground">AutoEval+</span>
          </Link>
        </div>
        <h1 className="text-2xl font-bold text-foreground">Welcome Back</h1>
        <p className="text-muted-foreground mt-2">Select your login type below</p>
      </div>

      {/* Login Type Selection Container */}
      <div className="container mx-auto max-w-4xl">
        <div className="grid md:grid-cols-2 gap-8">
          {/* Student Login Selection */}
          <Card
            className="shadow-soft-lg animate-scale-in cursor-pointer hover:shadow-xl hover:scale-105 transition-all duration-300 border-2 hover:border-primary group"
            onClick={() => navigate('/student-login')}
          >
            <CardHeader className="text-center space-y-3">
              <div className="flex justify-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-light group-hover:bg-primary transition-colors duration-300">
                  <GraduationCap className="h-8 w-8 text-primary group-hover:text-primary-foreground transition-colors duration-300" />
                </div>
              </div>
              <CardTitle className="text-2xl mt-4">Student Login</CardTitle>
              <CardDescription className="text-base">
                Access your marks and results
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center pb-8">
              <Button onClick={() => navigate('/student-login')} className="w-full max-w-xs group-hover:bg-primary">
                Login as Student
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>

          {/* Teacher Login Selection */}
          <Card
            className="shadow-soft-lg animate-scale-in cursor-pointer hover:shadow-xl hover:scale-105 transition-all duration-300 border-2 hover:border-primary group"
            onClick={() => navigate('/teacher-login')}
            style={{ animationDelay: '100ms' }}
          >
            <CardHeader className="text-center space-y-3">
              <div className="flex justify-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-light group-hover:bg-primary transition-colors duration-300">
                  <BookOpen className="h-8 w-8 text-primary group-hover:text-primary-foreground transition-colors duration-300" />
                </div>
              </div>
              <CardTitle className="text-2xl mt-4">Teacher Login</CardTitle>
              <CardDescription className="text-base">
                Manage classes and evaluate answers
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center pb-8">
              <Button onClick={() => navigate('/teacher-login')} className="w-full max-w-xs group-hover:bg-primary">
                Login as Teacher
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Register Link */}
        <div className="text-center mt-12 text-sm text-muted-foreground animate-fade-in" style={{ animationDelay: '200ms' }}>
          Don't have an account?{' '}
          <Link to="/register" className="text-primary hover:underline font-medium">
            Create Account
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
