import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { FileCheck2, Moon, Sun, GraduationCap, BookOpen } from 'lucide-react';
import { useAuth, UserRole } from '@/contexts/AuthContext';
import { useTheme } from '@/hooks/use-theme';

const Register = () => {
  const [role, setRole] = useState<UserRole>('student');

  // Student fields
  const [studentUsername, setStudentUsername] = useState('');
  const [rollNumber, setRollNumber] = useState('');
  const [studentPassword, setStudentPassword] = useState('');
  const [studentConfirmPassword, setStudentConfirmPassword] = useState('');
  const [selectedClassId, setSelectedClassId] = useState<string>('');
  const [classrooms, setClassrooms] = useState<{ id: number, name: string }[]>([]);

  // Teacher fields
  const [teacherUsername, setTeacherUsername] = useState('');
  const [teacherPassword, setTeacherPassword] = useState('');
  const [teacherConfirmPassword, setTeacherConfirmPassword] = useState('');
  const [department, setDepartment] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const { registerStudent, registerTeacher, isAuthenticated, user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  // Fetch classrooms on mount
  useEffect(() => {
    const fetchClassrooms = async () => {
      try {
        const response = await fetch('http://localhost:8000/public/classrooms');
        if (response.ok) {
          const data = await response.json();
          setClassrooms(data);
        }
      } catch (error) {
        console.error("Failed to fetch classrooms:", error);
      }
    };
    fetchClassrooms();
  }, []);

  useEffect(() => {
    if (isAuthenticated && user) {
      if (user.role === 'student') {
        navigate('/student-dashboard');
      } else if (user.role === 'teacher') {
        navigate('/teacher-dashboard');
      }
    }
  }, [isAuthenticated, user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    if (role === 'student') {
      await registerStudent(studentUsername, rollNumber, studentPassword, studentConfirmPassword, selectedClassId);
    } else {
      await registerTeacher(teacherUsername, teacherPassword, teacherConfirmPassword, department || undefined);
    }

    setIsLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-primary/5 via-background to-primary/10">
      <div className="absolute top-4 right-4">
        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>
      </div>

      <Card className="w-full max-w-md shadow-soft-lg animate-scale-in">
        <CardHeader className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-primary-light">
              <FileCheck2 className="h-6 w-6 text-primary" />
              <span className="text-xl font-bold text-foreground">AutoEval+</span>
            </div>
          </div>
          <CardTitle className="text-2xl">Create Account</CardTitle>
          <CardDescription>
            Get started with automated answer evaluation
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Role Selection */}
            <div className="space-y-2">
              <Label htmlFor="role">I am a</Label>
              <Select value={role} onValueChange={(value: UserRole) => setRole(value)}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select your role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="student">
                    <div className="flex items-center gap-2">
                      <GraduationCap className="h-4 w-4" />
                      <span>Student</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="teacher">
                    <div className="flex items-center gap-2">
                      <BookOpen className="h-4 w-4" />
                      <span>Teacher</span>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Student Registration Fields */}
            {role === 'student' && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="studentUsername">Student Username</Label>
                  <Input
                    id="studentUsername"
                    type="text"
                    placeholder="Choose a username"
                    value={studentUsername}
                    onChange={(e) => setStudentUsername(e.target.value)}
                    required
                    className="transition-base"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="rollNumber">Roll Number</Label>
                  <Input
                    id="rollNumber"
                    type="text"
                    placeholder="Enter your roll number"
                    value={rollNumber}
                    onChange={(e) => setRollNumber(e.target.value)}
                    required
                    className="transition-base"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="className">Class</Label>
                  <Select value={selectedClassId} onValueChange={setSelectedClassId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select your class" />
                    </SelectTrigger>
                    <SelectContent>
                      {classrooms.map((cls) => (
                        <SelectItem key={cls.id} value={cls.id.toString()}>
                          {cls.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="studentPassword">Password</Label>
                  <Input
                    id="studentPassword"
                    type="password"
                    placeholder="At least 6 characters"
                    value={studentPassword}
                    onChange={(e) => setStudentPassword(e.target.value)}
                    required
                    minLength={6}
                    className="transition-base"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="studentConfirmPassword">Confirm Password</Label>
                  <Input
                    id="studentConfirmPassword"
                    type="password"
                    placeholder="Re-enter your password"
                    value={studentConfirmPassword}
                    onChange={(e) => setStudentConfirmPassword(e.target.value)}
                    required
                    minLength={6}
                    className="transition-base"
                  />
                </div>
              </>
            )}

            {/* Teacher Registration Fields */}
            {role === 'teacher' && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="teacherUsername">Teacher Username</Label>
                  <Input
                    id="teacherUsername"
                    type="text"
                    placeholder="Choose a username"
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
                    placeholder="At least 6 characters"
                    value={teacherPassword}
                    onChange={(e) => setTeacherPassword(e.target.value)}
                    required
                    minLength={6}
                    className="transition-base"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="teacherConfirmPassword">Confirm Password</Label>
                  <Input
                    id="teacherConfirmPassword"
                    type="password"
                    placeholder="Re-enter your password"
                    value={teacherConfirmPassword}
                    onChange={(e) => setTeacherConfirmPassword(e.target.value)}
                    required
                    minLength={6}
                    className="transition-base"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="department">Department (Optional)</Label>
                  <Input
                    id="department"
                    type="text"
                    placeholder="e.g., Computer Science"
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                    className="transition-base"
                  />
                </div>
              </>
            )}

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Creating account...' : `Create ${role === 'student' ? 'Student' : 'Teacher'} Account`}
            </Button>

            <div className="text-center text-sm text-muted-foreground">
              Already have an account?{' '}
              <Link to="/login" className="text-primary hover:underline font-medium">
                Sign in
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default Register;
