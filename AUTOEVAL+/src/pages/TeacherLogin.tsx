import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileCheck2, Moon, Sun, BookOpen } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/hooks/use-theme';

const TeacherLogin = () => {
    const [teacherUsername, setTeacherUsername] = useState('');
    const [teacherPassword, setTeacherPassword] = useState('');
    const [isTeacherLoading, setIsTeacherLoading] = useState(false);

    const { loginTeacher, isAuthenticated, user } = useAuth();
    const { theme, toggleTheme } = useTheme();
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated && user) {
            if (user.role === 'student') {
                navigate('/student-dashboard');
            } else if (user.role === 'teacher') {
                navigate('/teacher-dashboard');
            }
        }
    }, [isAuthenticated, user, navigate]);

    const handleTeacherSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsTeacherLoading(true);
        await loginTeacher(teacherUsername, teacherPassword);
        setIsTeacherLoading(false);
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
                <h1 className="text-2xl font-bold text-foreground">Teacher Portal</h1>
                <p className="text-muted-foreground mt-2">Enter your credentials to access the teacher dashboard</p>
            </div>

            <div className="container mx-auto max-w-md">
                <Card className="shadow-soft-lg animate-scale-in">
                    <CardHeader className="text-center space-y-3">
                        <div className="flex justify-center">
                            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-primary-light">
                                <BookOpen className="h-6 w-6 text-primary" />
                            </div>
                        </div>
                        <CardTitle className="text-xl">Teacher Login</CardTitle>
                        <CardDescription>
                            Access your teacher dashboard
                        </CardDescription>
                    </CardHeader>

                    <CardContent>
                        <form onSubmit={handleTeacherSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="teacherUsername">Teacher Username</Label>
                                <Input
                                    id="teacherUsername"
                                    type="text"
                                    placeholder="Enter your username"
                                    value={teacherUsername}
                                    onChange={(e) => setTeacherUsername(e.target.value)}
                                    required
                                    className="transition-base"
                                />
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="teacherPassword">Password</Label>
                                <Input
                                    id="teacherPassword"
                                    type="password"
                                    placeholder="Enter your password"
                                    value={teacherPassword}
                                    onChange={(e) => setTeacherPassword(e.target.value)}
                                    required
                                    className="transition-base"
                                />
                            </div>

                            <Button type="submit" className="w-full" disabled={isTeacherLoading}>
                                {isTeacherLoading ? 'Signing in...' : 'Sign In as Teacher'}
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

export default TeacherLogin;
